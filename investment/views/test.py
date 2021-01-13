"""
test
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-07
@desc:
"""

from rest_framework.views import Response, APIView

from investment.utils import capital_flow


class TestViews(APIView):

    @staticmethod
    def get(request):
        r = capital_flow.category_capital_flow('有色金属', '2020-10-01')
        return Response(r.to_dict(orient='records'))
