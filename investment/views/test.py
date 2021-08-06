"""
test
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-07
@desc:
"""
import datetime

from rest_framework.views import Response, APIView

from investment.utils import capital_flow, holding_v2


class TestViews(APIView):

    @staticmethod
    def get(request):
        r = holding_v2.portfolio_holding_security('PFF003', datetime.date(2021, 6, 1))
        print(r)
        return Response()
