"""
mvo
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-07
@desc: 均值方差模型计算组合资产配置比例
"""

from rest_framework.views import APIView, Response
from django.db.models import Q

from investment import models
from investment.functions import mvo


class IndexInfoViews(APIView):

    @staticmethod
    def get(request):
        indexes = models.IndexBasicInfo.objects.filter(~Q(category='风格类指数')).values(
            'secucode', 'chiname', 'category', 'component'
        ).order_by('category', 'component')
        return Response(indexes)


class MvoViews(APIView):

    @staticmethod
    def get(request):
        data = request.query_params
        indexes = data.get('indexes')
        bounds = data.get('bounds')
        risks = data.get('risks')
        window = data.get('window')
        window = int(window) if window else None
        optimize = mvo.Optimize(indexes=indexes, bounds=bounds, window=window)
        ret = optimize.optimize(risks=risks)
        return Response(ret)
