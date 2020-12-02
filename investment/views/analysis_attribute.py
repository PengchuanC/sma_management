"""
投资分析模块-归因分析
包含业绩归因、风格分析等内容
"""
import pandas as pd
import numpy as np
from django.forms.models import model_to_dict
from rest_framework.views import Response, APIView
from investment import models
from ..utils.holding import fund_holding_stock


class StyleAnalysis(APIView):

    @staticmethod
    def get(request):
        params = request.query_params
        port_code = params.get('portCode')
        date = params.get('date')
        if date:
            data = models.PortfolioStyle.objects.filter(port_code=port_code, date__lte=date).all()
        else:
            data = models.PortfolioStyle.objects.filter(port_code=port_code).all()
        data = [model_to_dict(x) for x in data]
        return Response(data)

    @staticmethod
    def parse_request():
        pass


class ExposureAnalysis(APIView):

    @staticmethod
    def get(request):
        params = request.query_params
        port_code = params.get('portCode')
        date = params.get('date')
        if date:
            date = models.Balance.objects.filter(port_code=port_code, date__lte=date).last().date
        else:
            date = models.Balance.objects.filter(port_code=port_code).last().date
        hold = fund_holding_stock(port_code, date.strftime('%Y-%m-%d'))
        stocks = list(hold.stockcode)
        expose = models.StockExpose.objects.filter(secucode__in=stocks, date=date).all()
        expose = pd.DataFrame([model_to_dict(x) for x in expose])
        data = pd.merge(hold, expose, left_on='stockcode', right_on='secucode', how='left')
        factors = ['beta', 'momentum', 'size', 'earnyild', 'resvol', 'growth', 'btop', 'leverage', 'liquidty', 'sizenl']
        factors_cn = ['贝塔', '动量', '市值', '盈利', '波动', '成长', '质量', '杠杆', '流动性', '非线性市值']
        h = np.array(data['ratio'])
        f = data[factors].values
        ret = np.dot(h, f)
        ret = {'name': factors_cn, 'value': ret}
        return Response(ret)
