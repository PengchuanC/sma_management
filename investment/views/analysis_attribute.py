"""
投资分析模块-归因分析
包含业绩归因、风格分析等内容
"""
import datetime

import pandas as pd
import numpy as np
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from asgiref.sync import sync_to_async
from rest_framework.views import Response, APIView
from dateutil.relativedelta import relativedelta

from investment import models
from ..utils.holding import fund_holding_stock
from ..utils.holding_v2 import portfolio_holding_stock
from ..utils import fund as fund_util


class StyleAnalysis(APIView):

    @staticmethod
    def get(request):
        params = request.query_params
        port_code = params.get('portCode')
        date = params.get('date')
        if date:
            data = models.PortfolioStyle.objects.filter(port_code=port_code, date__lte=date).all()
        else:
            data = models.PortfolioStyle.objects.filter(port_code=port_code).all()
        data = [model_to_dict(x) for x in data]
        return Response(data)

    @staticmethod
    def parse_request():
        pass


class ExposureAnalysis(APIView):

    @staticmethod
    def get(request):
        params = request.query_params
        port_code = params.get('portCode')
        date = params.get('date')
        if date:
            date = models.Balance.objects.filter(port_code=port_code, date__lte=date).last().date
        else:
            date = models.Balance.objects.filter(port_code=port_code).last().date
        hold = fund_holding_stock(port_code, date.strftime('%Y-%m-%d'))
        stocks = list(hold.stockcode)
        expose_last = models.StockExpose.objects.filter(date__lte=date).last().date
        expose = models.StockExpose.objects.filter(secucode__in=stocks, date=expose_last).all()
        expose = pd.DataFrame([model_to_dict(x) for x in expose])
        data = pd.merge(hold, expose, left_on='stockcode', right_on='secucode', how='left')
        data = data.dropna(how='any')
        factors = ['beta', 'momentum', 'size', 'earnyild', 'resvol', 'growth', 'btop', 'leverage', 'liquidty', 'sizenl']
        factors_cn = ['贝塔', '动量', '市值', '盈利', '波动', '成长', '质量', '杠杆', '流动性', '非线性市值']
        h = np.array(data['ratio'].astype('float'))
        f = data[factors].values.astype('float')
        ret = np.dot(h, f)
        ret = {'name': factors_cn, 'value': ret}
        return Response(ret)


class Exposure(object):
    factors = ['beta', 'momentum', 'size', 'earnyild', 'resvol', 'growth', 'btop', 'leverage', 'liquidty', 'sizenl']
    factors_cn = ['贝塔', '动量', '市值', '盈利', '波动', '成长', '质量', '杠杆', '流动性', '非线性市值']
    names = dict(zip(factors, factors_cn))

    @staticmethod
    async def exposure(request):
        port_code = request.GET.get('portCode')
        date = request.GET.get('date')
        exp = Exposure()
        date = await exp.nearest_tradingday(port_code, date)
        ptf = await exp.portfolio_exposure(port_code, date)
        idx = await exp.index_exposure('000906', date)
        return JsonResponse({'name': exp.factors_cn, 'portfolio': ptf, 'index': idx})

    @staticmethod
    async def nearest_tradingday(port_code, date):
        """最近交易日"""
        if date:
            date = await sync_to_async(models.Balance.objects.filter(port_code=port_code, date__lte=date).last)()
        else:
            date = await sync_to_async(models.Balance.objects.filter(port_code=port_code).last)()
        date = date.date
        return date

    async def style_factor_exposure(self, stocks, date):
        """风格因子 因子暴露"""
        expose_last = await sync_to_async(models.StockExpose.objects.filter(date__lte=date).last)()
        expose_last = expose_last.date
        expose = await sync_to_async(models.StockExpose.objects.filter(secucode__in=stocks, date=expose_last).values)()
        expose = await sync_to_async(pd.DataFrame)(expose)
        expose = expose.set_index('secucode_id')
        expose = expose[self.factors]
        return expose

    async def portfolio_exposure(self, port_code, date):
        """组合放个暴露"""
        holding = await sync_to_async(portfolio_holding_stock)(port_code, date)
        holding = await sync_to_async(pd.Series)(holding)
        exposure = await self.style_factor_exposure(list(holding.index), date)
        exposure['holding'] = holding
        exposure = exposure.astype(float)
        ret = exposure['holding'].dot(exposure[self.factors])
        ret = ret.to_list()
        return ret

    async def index_exposure(self, index_code, date):
        """指数风格暴露"""
        latest = await sync_to_async(models.IndexComponent.objects.filter(secucode=index_code, date__lte=date).last)()
        last = latest.date
        holding = await sync_to_async(models.IndexComponent.objects.filter(secucode=index_code, date=last).values)(
            'stockcode', 'weight'
        )
        holding = await sync_to_async(pd.DataFrame)(holding)
        holding = holding.set_index('stockcode')
        holding = holding / 100
        exposure = await self.style_factor_exposure(list(holding.index), date)
        exposure['holding'] = holding
        exposure = exposure.astype(float)
        ret = exposure['holding'].dot(exposure[self.factors])
        ret = ret.to_list()
        return ret


class BrinsonAnalysis(APIView):
    """获取组合Brinson归因，默认多期"""

    def get(self, request):
        params = request.query_params
        port_code = params.get('portCode')
        date = params.get('date')
        index = params.get('index') or '000906'
        if date:
            data = models.PortfolioBrinson.objects.filter(port_code=port_code, index=index, date__lte=date).all()
        else:
            data = models.PortfolioBrinson.objects.filter(port_code=port_code, index=index).all()
        data = [model_to_dict(x) for x in data]
        data = pd.DataFrame(data)
        for q in ['q1', 'q2', 'q3', 'q4']:
            data[q] = data[q].astype('float') + 1
        data = data[['industry', 'q1', 'q2', 'q3', 'q4']].groupby('industry').agg(self.cumprod)
        data['raa'] = data['q2'] - data['q1']
        data['rss'] = data['q3'] - data['q1']
        data['rin'] = data['q4'] - data['q3'] - data['q2'] + data['q1']
        data['rtt'] = data['q4'] - data['q1']
        data = data.reset_index()
        ret = data.to_dict(orient='records')
        return Response(ret)

    @staticmethod
    def cumprod(s: pd.Series):
        """计算累乘值"""
        s = s.cumprod()
        return (s.iloc[-1] - 1)*100

    @staticmethod
    def sum(s: pd.Series):
        """计算累乘值"""
        return s.sum()*100


class MovingVolatility(APIView):
    """滚动30日波动率

    """

    @staticmethod
    def return_bound(s: float, risk_free=0.015):
        s = float(s) - risk_free/365
        return min([0, s])

    @staticmethod
    def get(request):
        params = request.query_params
        port_code = params.get('portCode')
        date: str = params.get('date')
        if not date:
            date = datetime.date.today().strftime('%Y-%m-%d')
        nav = models.Balance.objects.filter(port_code=port_code, date__lte=date).values('acc_nav', 'date')
        nav = pd.DataFrame(nav).set_index('date')
        pct = nav.pct_change().dropna()
        std = pct.rolling(30).std().dropna()
        std = np.round(std * np.sqrt(250)*100, 2)
        std = std.acc_nav
        std.name = 'vol'

        downside_pct = pct['acc_nav'].apply(MovingVolatility.return_bound)
        downside_std = downside_pct.copy().rolling(30).std().dropna()
        downside_std = np.round(downside_std * np.sqrt(250) * 100, 2)
        downside_std.name = 'downside_vol'
        downside_std = pd.concat([std, downside_std], axis=1)
        downside_std = downside_std.reset_index()
        downside_std = downside_std.to_dict(orient='records')
        return Response(downside_std)


class ProfitAnalysis(object):
    """
    收益拆解到单一资产
    """
    @staticmethod
    async def get(request):
        """
        Args:
            request: Django Request obj.

        Returns:

        """
        params = request.GET
        port_code = params['portCode']
        date = params.get('date')
        pa = ProfitAnalysis()
        if not date:
            date = datetime.date.today()
        nearest = await sync_to_async(models.Income.objects.filter(port_code=port_code, date__lte=date).latest)('date')
        date = nearest.date
        week = date + relativedelta(days=-7)
        month = date + relativedelta(months=-1)
        quarter = date + relativedelta(months=-3)
        durations = {'week': week, 'month': month, 'quarter': quarter, 'setup': None}
        data = []
        for name, duration in durations.items():
            ret = await pa.period_contribution(port_code, duration, date)
            ret.name = name
            data.append(ret)
        data = pd.concat(data, axis=1)
        data['secucode'] = data.index
        funds = list(data.index)
        names = await fund_util.fund_name_async(funds)
        classify = fund_util.fund_classify(funds)
        classify.update({port_code: '组合'})
        data['secuabbr'] = data['secucode'].apply(lambda x: names.get(x))
        data['classify'] = data['secucode'].apply(lambda x: classify.get(x))
        data['classify'] = data['classify'].fillna('私募理财')
        ret = pa.format(data)
        return JsonResponse(ret, safe=False)

    @staticmethod
    async def period_contribution(port_code, start, end):
        """区间组合资产净值变动"""
        prev_holding = None
        prev = 1
        if start is not None:
            queryset = await sync_to_async(models.Balance.objects.filter)(port_code=port_code, date__lte=start)
            exists = await sync_to_async(queryset.exists)()
            if exists:
                obj = await sync_to_async(queryset.latest)('date')
                prev = obj.unit_nav
                start = obj.date
                prev_holding = await sync_to_async(
                    models.Holding.objects.filter(port_code=port_code, date=start).values
                )('secucode', 'total_profit')
                prev_holding = await sync_to_async(list)(prev_holding)
                prev_holding = {x['secucode']: x['total_profit'] for x in prev_holding}
        current = await sync_to_async(models.Balance.objects.get)(port_code=port_code, date=end)
        cur_holding = await sync_to_async(
            models.Holding.objects.filter(port_code=port_code, date=end).values
        )('secucode', 'total_profit')
        cur_holding = await sync_to_async(list)(cur_holding)
        cur_holding = {x['secucode']: x['total_profit'] for x in cur_holding}
        cur_holding = pd.Series(cur_holding, name='current')
        if prev_holding is not None:
            prev_holding = pd.Series(prev_holding, name='prev')
            data = pd.concat([prev_holding, cur_holding], axis=1).fillna(0)
            cur_holding = data.current - data.prev
        cur_holding /= cur_holding.sum()
        current = current.unit_nav
        change = current / prev - 1
        cur_holding *= change
        cur_holding[port_code] = change
        return cur_holding

    @staticmethod
    def format(data: pd.DataFrame):
        data = data.astype(object)
        data = data.where(data.notnull(), None)
        cls = ['组合', '股票型', '债券型', '另类', 'QDII型', '货币型', '私募理财']
        key = 1
        ret = []
        for c in cls:
            d = data[data.classify == c]
            if d.empty:
                continue
            ratio = d[['week', 'month', 'quarter', 'setup']].sum().to_dict()
            father = {'key': key, 'secucode': '', 'secuabbr': c, **ratio}
            key += 1
            children = []
            d = d.sort_values(['setup', 'quarter', 'month'], ascending=[False, False, False])
            for _, _d in d.iterrows():
                ratio = _d[['week', 'month', 'quarter', 'setup']].to_dict()
                child = {'key': key, 'secucode': _d.secucode, 'secuabbr': _d.secuabbr, **ratio}
                children.append(child)
                key += 1
            father['children'] = children
            ret.append(father)
        return ret
