"""
pre_valuation
~~~~~~~~~~~~~
盘中估值，采用socket协议
"""

import json
import pandas as pd
import datetime

from asyncio import sleep
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from investment import models
from investment.utils.holding import fund_holding_stock
from investment.views.analysis import FundHoldingView


class PreValuationConsumer(AsyncJsonWebsocketConsumer):
    connected = False
    holding = None
    equity = 0

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
        holding = fund_holding_stock(port_code, date)
        ratio = FundHoldingView.asset_allocate(port_code, date)
        stock = ratio['stock']
        equity = float(holding.ratio.sum()) / stock
        self.equity = equity
        self.holding = holding
        stocks = holding.stockcode
        stocks = models.StockRealtimePrice.objects.filter(secucode__in=stocks).values(
            'secucode', 'prev_close', 'price', 'time'
        )
        stocks = pd.DataFrame(stocks)
        stocks['change'] = stocks.price / stocks.prev_close - 1
        data = holding.merge(stocks, left_on='stockcode', right_on='secucode', how='inner')
        data['real_change'] = (data.ratio * data.change).astype('float')
        data.time = data.time.apply(lambda x: x.strftime('%H:%M:%S'))
        data = data.groupby('time')['real_change'].sum().reset_index()
        data['real_change'] = data['real_change'] / equity
        data = data.rename(columns={'time': 'name', 'real_change': 'value'}).to_dict(orient='records')
        return data

    @database_sync_to_async
    def push(self):
        """后续推送的数据"""
        holding = self.holding
        if not isinstance(holding, pd.DataFrame):
            return
        if datetime.datetime.now().time() > datetime.time(15, 0, 20):
            self.disconnect(0)
            return
        last = models.StockRealtimePrice.objects.last().time
        stocks = holding.stockcode
        stocks = models.StockRealtimePrice.objects.filter(
            secucode__in=stocks, time=last
        ).values('secucode', 'prev_close', 'price')
        stocks = pd.DataFrame(stocks)
        stocks['change'] = stocks.price / stocks.prev_close - 1
        data = holding.merge(stocks, left_on='stockcode', right_on='secucode', how='inner')
        data['real_change'] = data.ratio * data.change
        data['real_change'] = data['real_change'].astype('float') / self.equity
        return [{'name': last.strftime('%H:%M:%S'), 'value': data.real_change.sum()}]