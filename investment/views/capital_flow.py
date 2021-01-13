"""
capital_flow
~~~~~~~~~~~~
行业资金流入情况

@date: 2021-01-13
"""

import datetime

from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from rest_framework.views import APIView, Response

from investment.utils import capital_flow as cf
from investment import models


class CapitalFlowView(APIView):

    @staticmethod
    def get(request):
        category = request.query_params.get('category')
        date = request.query_params.get('date')
        if date:
            end = parse(date).date()
        else:
            end = models.CapitalFlow.objects.last().date
        start = end - relativedelta(months=3, days=15)
        ret = cf.category_capital_flow(category, start)
        ret = ret.to_dict(orient='records')
        return Response(ret)
