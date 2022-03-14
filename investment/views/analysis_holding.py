import datetime

import pandas as pd
from django.http.response import JsonResponse
from asgiref.sync import sync_to_async

from investment import models
from investment.utils.date import last_tradingday_in_balance
from rpc.fund_screen_client import Client


class AnalysisHolding(object):
    """
    分析持有期单只基金表现
    """

    @staticmethod
    async def get(request):
        params = request.GET
        port_code = params.get('portCode')
        _type = params.get('type', '1')
        if not port_code:
            return JsonResponse({'error': '没有指定组合'})
        date = params.get('date')
        date = await last_tradingday_in_balance(port_code, date)
        ah = AnalysisHolding()
        ry = await ah.weighted_average_return(port_code, date)
        holding = await ah.holding(port_code, date)
        data = holding.merge(ry, on='secucode', how='outer')
        funds = list(data.secucode)
        fc = FundClassify(funds, _type)
        category = await fc.dispatch()
        names = await ah.names(funds)
        data = data.merge(category, on='secucode', how='outer')
        data = data.merge(names, on='secucode', how='outer')
        ret = ah.format(data)
        return JsonResponse({'data': ret})

    @staticmethod
    async def weighted_average_return(port_code: str, date: datetime.date) -> pd.DataFrame:
        """基金加权平均收益"""
        last = await sync_to_async(
            models.ReturnYield.objects.filter(port_code=port_code, date__lte=date).latest)('date')
        date = last.date
        ry = await sync_to_async(
            models.ReturnYield.objects.filter(
                port_code=port_code, date=date, deal_value__gt=0).values)('secucode', 'deal_value', 'ret_yield')
        data = await sync_to_async(pd.DataFrame)(ry)
        data['ret_yield'] *= data['deal_value']
        data = data.groupby('secucode').sum()
        data['ret_yield'] /= data['deal_value']
        data = data.reset_index().drop('deal_value', axis=1)
        return data

    @staticmethod
    async def holding(port_code: str, date: datetime.date):
        """持仓占比，累计收益"""
        holding = await sync_to_async(
            models.Holding.objects.filter(port_code=port_code, date=date).values)('secucode', 'mkt_cap', 'profit')
        data = await sync_to_async(pd.DataFrame)(holding)
        data['holding_ratio'] = data['mkt_cap'] / data['mkt_cap'].sum()
        return data

    @staticmethod
    async def names(funds):
        official = await sync_to_async(models.Funds.objects.filter(secucode__in=funds).values)()
        official = await sync_to_async(pd.DataFrame)(official)
        query = list(official.secucode)
        other = [x for x in funds if x not in query]
        other = await sync_to_async(models.Security.objects.filter(secucode__in=other).values)('secucode', 'secuabbr')
        other = await sync_to_async(pd.DataFrame)(other)
        other = other.rename(columns={'secuabbr': 'secuname'})
        data = pd.concat([official, other])
        return data

    @staticmethod
    def format(data: pd.DataFrame):
        """格式化数据"""
        func = {'mkt_cap': 'sum', 'profit': 'sum', 'holding_ratio': 'sum', 'ret_yield': 'mean'}
        total = data.agg(func)
        total = total.to_dict()
        total.update({'category': '合计', 'second': None, 'secuname': '合计', 'key': 0, 'secucode': None})
        group = data.groupby('category').agg({**func, 'second': 'first'}).sort_values('holding_ratio', ascending=False)
        group = group.reset_index()
        group['secuname'] = '合计'
        group['secucode'] = None
        data = data.sort_values(['holding_ratio', 'ret_yield'], ascending=[False, False])
        ret = [total]
        count = 1
        for _, g in group.iterrows():
            _g = g.to_dict()
            _g['key'] = count
            _g['second'] = None
            count += 1
            d = data[data.category == g.category]
            d['category'] = None
            children = []
            for _, r in d.iterrows():
                r = r.to_dict()
                r['key'] = count
                children.append(r)
                count += 1
            _g['children'] = children
            ret.append(_g)
        return ret


class FundClassify(object):

    def __init__(self, funds, typ):
        self.funds = funds
        self.type = typ

    async def _noi_classify(self):
        """野村公募基金分类，用于生成其他基金分类"""
        ret = Client.simple('fund_category', self.funds)
        data = pd.DataFrame(ret)
        query = list(data.secucode)
        other = [x for x in self.funds if x not in query]
        other = await sync_to_async(
            models.Security.objects.filter(secucode__in=other).values_list)('secucode', 'category')
        other = await sync_to_async(pd.DataFrame)(other, columns=['secucode', 'first'])
        other['second'] = other['first']
        data = pd.concat([data, other])
        return data

    async def noi_first(self):
        data = await self._noi_classify()
        data['category'] = data['first']
        return data[['secucode', 'category', 'second']]

    async def noi_second(self):
        data = await self._noi_classify()
        data['category'] = data['second']
        return data[['secucode', 'category', 'second']]

    async def positive_or_negative(self):
        """主动被动型分类"""
        negative = ['股票ETF及联接型', '股票被动指数型', '债券指数型']
        data = await self._noi_classify()
        data['category'] = data['second'].apply(lambda x: '被动型' if x in negative else '主动型')
        return data[['secucode', 'category', 'second']]

    async def invest_pool(self):
        """自定义的基金类型"""
        data = await self._noi_classify()
        important = await sync_to_async(
            models.ImportantHolding.objects.filter(secucode__in=self.funds).values)('secucode', 'important')
        important = await sync_to_async(list)(important)
        important = [{'secucode': x['secucode'], 'category': x['important']} for x in important]
        important = pd.DataFrame(important)
        data = data.merge(important, on='secucode', how='outer')
        data['category'] = data['category'].fillna('其他')
        return data[['secucode', 'category', 'second']]

    async def dispatch(self):
        _type = self.type
        if _type == '1':
            category = await self.noi_first()
        elif _type == '2':
            category = await self.noi_second()
        elif _type == '3':
            category = await self.positive_or_negative()
        elif _type == '4':
            category = await self.invest_pool()
        else:
            category = await self.noi_first()
        return category
