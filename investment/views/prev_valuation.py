"""
pre_valuation
~~~~~~~~~~~~~
盘中估值，采用socket协议
"""

import json
import pandas as pd
import datetime

from copy import deepcopy
from asyncio import sleep
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Max

from investment import models
from investment.utils.holding import fund_holding_stock, fund_holding_stock_by_fund, holding_etf_in_exchange
from investment.views.analysis import FundHoldingView


class PreValuationConsumer(AsyncJsonWebsocketConsumer):
    connected = False
    holding = None
    etf = None
    equity = 0
    time = datetime.datetime.now().time().strftime('%H:%M:%S')

    async def connect(self):
        self.connected = True
        await self.accept()

    async def disconnect(self, close_code):
        self.connected = False
        await self.close(close_code)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):

        init_data = await self.on_receive(text_data)
        await self.send(text_data=json.dumps(init_data))

        while True:
            await sleep(15)
            ret = await self.push()
            if not ret:
                break
            await self.send(text_data=json.dumps(ret))

    @database_sync_to_async
    def on_receive(self, port_code: str):
        """连接时一次性返回的数据"""
        if datetime.datetime.now().time() < datetime.time(9, 30, 0):
            return
        date = models.Balance.objects.filter(port_code=port_code).last().date
        holding = fund_holding_stock(port_code, date, in_exchange=False)
        etf = holding_etf_in_exchange(port_code, date)
        etf = pd.DataFrame([{'stockcode': x, 'ratio': y}
                           for x, y in etf.items()])
        ratio = FundHoldingView.asset_allocate(port_code, date)
        stock = ratio['stock']
        equity = holding.ratio.sum() / stock
        self.equity = equity
        self.holding = holding
        self.etf = etf
        stocks = holding.stockcode
        stocks = models.StockRealtimePrice.objects.filter(secucode__in=list(stocks)+list(etf.stockcode)).values(
            'secucode', 'prev_close', 'price', 'time'
        )
        stocks = pd.DataFrame(stocks)
        stocks.time = stocks.time.apply(lambda x: x.strftime('%H:%M:%S'))
        stocks = stocks[stocks['price'] != 0]
        stocks['change'] = stocks.price / stocks.prev_close - 1
        data = holding.merge(stocks, left_on='stockcode',
                             right_on='secucode', how='inner')
        data['real_change'] = (data.ratio * data.change).astype('float')
        data = data.groupby('time')['real_change'].sum().reset_index()
        data['real_change'] /= float(equity)
        data = data.rename(columns={'time': 'name', 'real_change': 'value'})
        if not etf.empty:
            etf_d = etf.merge(stocks, left_on='stockcode',
                              right_on='secucode', how='inner')
            etf_d['real_change'] = etf_d.ratio * etf_d.change.astype('float')
            etf_d = etf_d.groupby('time')['real_change'].sum().reset_index()
            etf_d = etf_d.rename(columns={'time': 'name'})
            data = data.merge(etf_d, on='name', how='left')
            data = data.fillna(0)
            data['value'] += data['real_change']
            data = data[['name', 'value']]
        data = data.to_dict(orient='records')
        return data[:-1]

    @database_sync_to_async
    def push(self):
        """后续推送的数据"""
        holding = self.holding
        if not isinstance(holding, pd.DataFrame):
            return
        if datetime.datetime.now().time() > datetime.time(15, 0, 20):
            self.disconnect(0)
            return
        ret = self.calc(holding, self.etf, self.equity)
        return ret

    @staticmethod
    def calc(holding, etf, equity):
        """计算实时涨跌幅"""
        last = models.StockRealtimePrice.objects.last().time
        last = models.StockRealtimePrice.objects.filter(
            time__lt=last).last().time
        stocks = holding.stockcode
        etfs = etf.stockcode
        codes = list(stocks) + list(etfs)
        stocks = models.StockRealtimePrice.objects.filter(
            secucode__in=codes, time=last
        ).values('secucode', 'prev_close', 'price')
        stocks = pd.DataFrame(stocks)
        stocks = stocks[stocks['price'] != 0]
        stocks['change'] = stocks.price / stocks.prev_close - 1
        data = holding.merge(stocks, left_on='stockcode',
                             right_on='secucode', how='inner')
        data['real_change'] = data.ratio * data.change
        data['real_change'] = data['real_change'].astype('float') / equity
        value = data.real_change.sum()
        if not etf.empty:
            etf_d = etf.merge(stocks, left_on='stockcode',
                              right_on='secucode', how='inner')
            etf_d['real_change'] = etf_d.ratio * etf_d.change.astype('float')
            value += etf_d.real_change.sum()
        return [{'name': last.strftime('%H:%M:%S'), 'value': value}]


class BulkFundValuationConsumer(AsyncJsonWebsocketConsumer):
    """批量返回基金的实时涨跌幅"""
    connected = False
    holding = None
    names = None
    equity = 0
    time = datetime.datetime.now().time().strftime('%H:%M:%S')
    # 持仓基金
    holding_fund = []

    async def connect(self):
        self.connected = True
        funds = await self.target_funds()
        await self.fund_holding(funds)
        await self.accept()

    async def disconnect(self, close_code):
        self.connected = False
        await self.close(close_code)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        ret = await self.calc()
        await self.send(text_data=json.dumps(ret))

        while True:
            await sleep(30)
            ret = await self.push()
            if not ret:
                break
            await self.send(text_data=json.dumps(ret))

    async def push(self):
        if not isinstance(self.holding, pd.DataFrame):
            return
        if datetime.datetime.now().time() > datetime.time(15, 0, 20):
            await self.disconnect(3000)
            return
        return await self.calc()

    async def calc(self):
        holding = self.holding
        stocks = list(set(list(holding.stockcode)))
        changes = await self.stock_price(stocks)
        data = pd.merge(holding, changes, on='stockcode', how='left')
        data['change'] = data['ratio'] * data['change']
        data['change'] = data['change'].astype('float')
        data = data.groupby(['time', 'secucode'])['change'].sum()
        data = data.reset_index()
        data = pd.merge(self.names, data, on='secucode', how='outer')
        data['key'] = data.index + 1
        data = data.rename(columns={'time': 'name', 'change': 'value'})
        data['name'] = data['name'].fillna(method='pad')
        data['value'] = data['value'].fillna(0)
        return data.to_dict(orient='records')

    @database_sync_to_async
    def target_funds(self):
        last = models.Holding.objects.aggregate(mdate=Max('date'))['mdate']
        funds = models.Holding.objects.filter(
            date=last).values('secucode').distinct()
        funds = [x['secucode'] for x in funds]

        observe = models.ObservePool.objects.values('secucode').distinct()
        observe = [x['secucode'] for x in observe]
        self.holding_fund = deepcopy(funds)

        funds += observe
        funds = list(set(funds))
        return funds

    @database_sync_to_async
    def fund_holding(self, funds):
        """获取基金持仓"""
        # 最新持仓
        holding = fund_holding_stock_by_fund(funds)
        funds = list(set(list(holding.secucode)))
        names = models.Funds.objects.filter(
            secucode__in=funds).values('secucode', 'secuname')
        names = pd.DataFrame(names)
        holding = names.merge(holding, on='secucode', how='outer')
        self.holding = holding
        names = holding[['secucode', 'secuname']].drop_duplicates()
        names['hold'] = names['secucode'].apply(
            lambda x: '是' if x in self.holding_fund else '否')
        self.names = names

    @database_sync_to_async
    def stock_price(self, stocks: list, tick=True):
        last = models.StockRealtimePrice.objects.last().time
        last = models.StockRealtimePrice.objects.filter(
            time__lt=last).last().time
        if tick:
            stocks = models.StockRealtimePrice.objects.filter(
                secucode__in=stocks, time=last
            ).values('secucode', 'prev_close', 'price', 'time')
        else:
            stocks = models.StockRealtimePrice.objects.filter(
                secucode__in=stocks, time__lte=last
            ).values('secucode', 'prev_close', 'price', 'time')
        stocks = pd.DataFrame(stocks)
        stocks = stocks.rename(columns={'secucode': 'stockcode'})
        stocks = stocks[stocks['price'] != 0]
        stocks['time'] = stocks['time'].apply(lambda x: x.strftime('%H:%M:%S'))
        stocks['change'] = stocks.price / stocks.prev_close - 1
        return stocks[['stockcode', 'change', 'time']]


class FundValuationConsumer(BulkFundValuationConsumer):

    secucode = ''

    async def connect(self):
        self.connected = True
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        fund = text_data
        if fund != self.secucode:
            self.secucode = fund
            await self.fund_holding([fund])
            ret = await self.on_receive()
            await self.send(text_data=json.dumps(ret))
        while True:
            await sleep(15)
            ret = await self.push()
            if not ret:
                break
            ret = ret
            await self.send(text_data=json.dumps(ret))

    async def on_receive(self):
        """连接时一次性返回的数据"""
        if datetime.datetime.now().time() < datetime.time(9, 30, 0):
            return
        holding = self.holding
        stocks = list(set(list(holding.stockcode)))
        changes = await self.stock_price(stocks, tick=False)
        data = pd.merge(holding, changes, on='stockcode', how='left')
        data['change'] = data['ratio'] * data['change']
        data['change'] = data['change'].astype('float')
        data = data.groupby(['secucode', 'time'])['change'].sum()
        data = data.reset_index()
        data = pd.merge(self.names, data, on='secucode', how='outer')
        data['key'] = data.index + 1
        data = data[['time', 'change']]
        data = data.rename(columns={'time': 'name', 'change': 'value'})
        return data.to_dict(orient='records')
