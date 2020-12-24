"""
overview
~~~~~~~~
组合账户总览
"""

from django.db.models import F
from django.forms.models import model_to_dict
from django.http import JsonResponse
from channels.db import database_sync_to_async
from rest_framework.views import APIView, Response
from investment import models
from investment.views.analysis import FundHoldingView


class OverviewView(APIView):

    @staticmethod
    def get(request):
        """产品净值曲线"""
        port_code = request.query_params.get('portCode')
        p = models.Balance.objects.filter(port_code=port_code).annotate(p=F('unit_nav')).values('date', 'p')
        b = models.ValuationBenchmark.objects.filter(port_code=port_code).annotate(b=F('unit_nav')).values('date', 'b')
        b = {x['date']: x['b'] for x in b}
        ret = []
        for p_ in p:
            date = p_['date']
            ret.append({'date': date, 'p': p_['p'], 'b': b[date]})
        return Response(ret)

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
    async def question(request):
        """客户评测

        Args:
            request:

        Returns:

        """
        port_code = request.GET.get('portCode')
        data = await database_sync_to_async(models.ClientQ.objects.get)(port_code=port_code)
        return JsonResponse({'data': model_to_dict(data)})
