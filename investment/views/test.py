"""
test
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-07
@desc:
"""

from rest_framework.views import Response, APIView
from django.http import JsonResponse
from itsdangerous import TimedJSONWebSignatureSerializer


tjs = TimedJSONWebSignatureSerializer(secret_key='hxb xabj789323121=')


class TestViews(APIView):

    @staticmethod
    def get(request):
        from investment.functions.mvo import Optimize

        indexes = ['H00300', 'H00905', 'H11025', 'Y00001', 'Y00045', '000832', 'AU9999.SGE', 'HSITR']
        o = Optimize(indexes=indexes, bounds={'H11025': (0, 1), 'AU9999.SGE': (0, 0.05)})
        r = o.optimize([0.02, 0.05, 0.12, 0.15])

        return Response(r)


async def token(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    token_ = tjs.dumps({'username': username, 'password': password})
    return JsonResponse({'token': str(token_)})
