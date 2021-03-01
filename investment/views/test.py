"""
test
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-07
@desc:
"""

from rest_framework.views import Response, APIView

from investment.utils import capital_flow, holding


class TestViews(APIView):

    @staticmethod
    def get(request):
        holding.fund_holding_stock_by_fund(['110011', '000001'])
        r = capital_flow.category_capital_flow('有色金属', '2020-10-01')
        return Response(r.to_dict(orient='records'))
