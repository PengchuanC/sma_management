"""
投资分析模块-归因分析
包含业绩归因、风格分析等内容
"""
import datetime
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
        data = data.dropna(how='any')
        factors = ['beta', 'momentum', 'size', 'earnyild', 'resvol', 'growth', 'btop', 'leverage', 'liquidty', 'sizenl']
        factors_cn = ['贝塔', '动量', '市值', '盈利', '波动', '成长', '质量', '杠杆', '流动性', '非线性市值']
        h = np.array(data['ratio'].astype('float'))
        f = data[factors].values.astype('float')
        ret = np.dot(h, f)
        ret = {'name': factors_cn, 'value': ret}
        return Response(ret)


class BrinsonAnalysis(APIView):
    """获取组合Brinson归因，默认多期"""

    def get(self, request):
        params = request.query_params
        port_code = params.get('portCode')
        date = params.get('date')
        index = params.get('index') or '000906'
        if date:
            data = models.PortfolioBrinson.objects.filter(port_code=port_code, index=index, date__lte=date).all()
        else:
            data = models.PortfolioBrinson.objects.filter(port_code=port_code, index=index).all()
        data = [model_to_dict(x) for x in data]
        data = pd.DataFrame(data)
        for q in ['q1', 'q2', 'q3', 'q4']:
            data[q] = data[q].astype('float') + 1
        data = data[['industry', 'q1', 'q2', 'q3', 'q4']].groupby('industry').agg(self.cumprod)
        data['raa'] = data['q2'] - data['q1']
        data['rss'] = data['q3'] - data['q1']
        data['rin'] = data['q4'] - data['q3'] - data['q2'] + data['q1']
        data['rtt'] = data['q4'] - data['q1']
        data = data.reset_index()
        ret = data.to_dict(orient='records')
        return Response(ret)

    @staticmethod
    def cumprod(s: pd.Series):
        """计算累乘值"""
        s = s.cumprod()
        return (s.iloc[-1] - 1)*100


class MovingVolatility(APIView):
    """滚动30日波动率

    """

    @staticmethod
    def get(request):
        params = request.query_params
        port_code = params.get('portCode')
        date: str = params.get('date')
        if not date:
            date = datetime.date.today().strftime('%Y-%m-%d')
        nav = models.Balance.objects.filter(port_code=port_code, date__lte=date).values('acc_nav', 'date')
        nav = pd.DataFrame(nav).set_index('date')
        pct = nav.pct_change().dropna()
        std = pct.rolling(30).std().dropna()
        std = np.round(std * np.sqrt(250)*100, 2)
        std = std.reset_index()
        std = std.to_dict(orient='records')
        return Response(std)
