"""
overview
~~~~~~~~
组合账户总览
"""
import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import F
from django.forms.models import model_to_dict
from django.http import JsonResponse
from channels.db import database_sync_to_async
from rest_framework.views import APIView, Response
from pandas import DataFrame
from investment import models
from investment.views.analysis import FundHoldingView


class OverviewView(APIView):

    @staticmethod
    def get(request):
        """产品净值曲线"""
        port_code = request.query_params.get('portCode')
        base = models.Portfolio.objects.get(port_code=port_code).base
        p = models.Balance.objects.filter(port_code=port_code).annotate(p=F('unit_nav')).values('date', 'p')
        b = models.ValuationBenchmark.objects.filter(port_code=port_code).annotate(b=F('unit_nav')).values('date', 'b')
        b = {x['date']: x['b'] for x in b}
        ret = []
        for p_ in p:
            date = p_['date']
            ret.append({'date': date, 'p': p_['p'], 'b': b[date]})
        return Response({'data': ret, 'base': base})

    @staticmethod
    def asset_allocate(request):
        """穿透资产配置"""
        port_code: str = request.GET.get('portCode')
        date = models.Balance.objects.filter(port_code=port_code).last().date
        r = FundHoldingView.asset_allocate(port_code, date)
        ret = [
            {'name': '权益', 'value': float(r['stock'])},
            {'name': '固收', 'value': float(r['bond'])},
            {'name': '另类', 'value': float(r['metals'])},
            {'name': '货币', 'value': float(r['monetary'])}
        ]
        return JsonResponse({'data': ret})

    @staticmethod
    def avg_asset_allocate(request):
        """穿透资产区间平均配置"""
        port_code: str = request.GET.get('portCode')
        start = request.GET.get('start')
        end = request.GET.get('end')
        if not start or not end:
            end = models.Balance.objects.filter(port_code=port_code).last().date
            start = end - relativedelta(days=30)
        ret = models.PortfolioAssetAllocate.objects.filter(port_code=port_code, date__range=(start, end)).all()
        ret = DataFrame([model_to_dict(x) for x in ret])
        r = ret.mean()
        ret = [
            {'name': '权益', 'value': float(r['equity'])},
            {'name': '固收', 'value': float(r['fix_income'])},
            {'name': '另类', 'value': float(r['alter'])},
            {'name': '货币', 'value': float(r['money'])}
        ]
        return JsonResponse({'data': ret})

    @staticmethod
    async def question(request):
        """客户评测

        Args:
            request:

        Returns:

        """
        port_code = request.GET.get('portCode')
        data = await database_sync_to_async(models.ClientQ.objects.get)(port_code=port_code)
        return JsonResponse({'data': model_to_dict(data)})


def fund_position(request):
    """基金平均仓位"""
    last = models.FundPosEstimate.objects.last()
    last = last.date
    start = last - datetime.timedelta(days=90)
    ret = models.FundPosEstimate.objects.filter(date__range=(start, last))
    ret = [model_to_dict(x) for x in ret]
    return JsonResponse({'data': ret})
