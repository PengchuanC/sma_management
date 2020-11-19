"""
overview
~~~~~~~~
组合账户总览
"""

from django.db.models import F
from rest_framework.views import APIView, Response
from investment import models


class OverviewView(APIView):

    @staticmethod
    def get(request):
        port_code = request.query_params.get('portCode')
        p = models.Balance.objects.filter(port_code=port_code).annotate(p=F('unit_nav')).values('date', 'p')
        b = models.ValuationBenchmark.objects.filter(port_code=port_code).annotate(b=F('unit_nav')).values('date', 'b')
        b = {x['date']: x['b'] for x in b}
        ret = []
        for p_ in p:
            date = p_['date']
            ret.append({'date': date, 'p': p_['p'], 'b': b[date]})
        return Response(ret)
