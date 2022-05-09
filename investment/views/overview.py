"""
overview
~~~~~~~~
组合账户总览
"""
import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from django.db.models import F
from django.forms.models import model_to_dict
from django.http import JsonResponse
from channels.db import database_sync_to_async
from rest_framework.views import APIView, Response
from pandas import DataFrame
from asgiref.sync import sync_to_async

from investment import models
from investment.views.analysis import FundHoldingView
from investment.utils.holding_v2 import asset_type_penetrate


class OverviewView(APIView):

    @staticmethod
    async def unit_nav(request):
        """产品净值曲线"""
        port_code: str = request.GET.get('portCode')
        base = await sync_to_async(models.Portfolio.objects.get)(port_code=port_code)
        base = base.benchmark
        p = await sync_to_async(
            models.Valuation.objects.filter(port_code=port_code).annotate(p=F('unit_nav')).values)('date', 'p')
        b = await sync_to_async(
            models.ValuationBenchmark.objects.filter(port_code=port_code).annotate(b=F('unit_nav')).values)('date', 'b')
        b = await sync_to_async(list)(b)
        b = {x['date']: x['b'] for x in b}
        ret = []
        p = await sync_to_async(list)(p)
        for p_ in p:
            date = p_['date']
            b_ = b.get(date)
            if not b_:
                continue
            ret.append({'date': date, 'p': p_['p'], 'b': b_})
        return JsonResponse({'data': ret, 'base': base})

    @staticmethod
    async def asset_allocate(request):
        """穿透资产配置"""
        port_code: str = request.GET.get('portCode')
        date = await sync_to_async(models.Holding.objects.filter(port_code=port_code).last)()
        date = date.date
        r = await sync_to_async(asset_type_penetrate)(port_code, date)
        ret = [
            {'name': '权益', 'value': float(r['equity'])},
            {'name': '固收', 'value': float(r['fix_income'])},
            {'name': '另类', 'value': float(r['alternative'])},
            {'name': '货币', 'value': float(r['monetary'])},
            {'name': '其他', 'value': float(r['other'])}
        ]
        lever = round(sum([x['value'] for x in ret]), 2)
        return JsonResponse({'data': ret, 'lever': lever})

    @staticmethod
    async def avg_asset_allocate(request):
        """穿透资产区间平均配置"""
        port_code: str = request.GET.get('portCode')
        start = request.GET.get('start')
        end = request.GET.get('end')
        if not start or not end:
            end = await database_sync_to_async(models.Valuation.objects.filter(port_code=port_code).last)()
            end = end.date
            start = end - relativedelta(days=30)
        ret = await database_sync_to_async(
            models.PortfolioAssetAllocate.objects.filter(port_code=port_code, date__range=(start, end)).all)()
        ret = await sync_to_async(list)(ret)
        ret = DataFrame([model_to_dict(x) for x in ret])
        r = ret.mean()
        ret = [
            {'name': '权益', 'value': float(r['equity'])},
            {'name': '固收', 'value': float(r['fix_income'])},
            {'name': '另类', 'value': float(r['alter'])},
            {'name': '货币', 'value': float(r['money'])},
            {'name': '其他', 'value': float(r['other'])}
        ]
        lever = round(sum([x['value'] for x in ret]), 2)
        return JsonResponse({'data': ret, 'lever': lever})

    @staticmethod
    async def history_asset_allocate(request):
        """基金成立以来持仓配置情况

        Args:
            request:

        Returns:

        """
        port_code: str = request.GET.get('portCode')
        ret = await database_sync_to_async(models.PortfolioAssetAllocate.objects.filter(port_code=port_code).values)(
            'date', 'equity', 'fix_income', 'alter', 'money', 'other'
        )
        ret = await sync_to_async(list)(ret)
        ret = [x for x in ret]
        return JsonResponse({'data': ret})

    @staticmethod
    async def question(request):
        """客户评测

        Args:
            request:

        Returns:

        """
        port_code = request.GET.get('portCode')
        exists = await sync_to_async(models.ClientQ.objects.filter(port_code=port_code).exists)()
        if not exists:
            return JsonResponse({'data': {}})
        data = await database_sync_to_async(models.ClientQ.objects.get)(port_code=port_code)
        return JsonResponse({'data': model_to_dict(data)})

    @staticmethod
    async def pre_valuation_compare_real(request):
        port_code = request.GET.get('portCode')
        pre = await sync_to_async(models.PreValuedNav.objects.filter(port_code=port_code).values)('date', 'value')
        income = await sync_to_async(models.Income.objects.filter(port_code=port_code).values)('date', 'unit_nav_chg')
        pre = await sync_to_async(DataFrame)(pre)
        income = await sync_to_async(DataFrame)(income)
        income = income.rename(columns={'unit_nav_chg': 'change_pct'})
        income['change_pct'] /= 100
        data = pre.merge(income, on='date', how='left').dropna(how='any')
        data = data.sort_values('date')
        data = data.to_dict(orient='records')
        return JsonResponse({'data': data})


def fund_position(request):
    """基金平均仓位
        modify date: 2021-05-08 加入沪深300收盘价
    """
    port_code = request.GET.get('portCode')
    last = models.FundPosEstimate.objects.last()
    last = last.date
    start = last - datetime.timedelta(days=90)
    ret = models.FundPosEstimate.objects.filter(date__range=(start, last))
    port = models.PortfolioAssetAllocate.objects.filter(
        port_code=port_code, date__range=(start, last)).values('date', 'equity')
    ret = [model_to_dict(x) for x in ret]
    ret = pd.DataFrame(ret)
    port = pd.DataFrame(port).rename(columns={'equity': 'portfolio'})
    hs300 = models.IndexQuote.objects.filter(secucode='000300', date__range=(start, last)).values('date', 'close')
    hs300 = pd.DataFrame(hs300)
    ret = ret.merge(port, on='date', how='left')
    ret = ret.merge(hs300, on='date', how='left')
    ret = ret.fillna(method='pad')
    ret = ret.where(ret.notnull(), None)
    ret = ret.to_dict(orient='records')
    return JsonResponse({'data': ret})
