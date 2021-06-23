"""
capital_flow
~~~~~~~~~~~~
行业资金流入情况

@date: 2021-01-13
"""

import math

import pandas as pd

from django.http import JsonResponse
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from rest_framework.views import APIView, Response

from investment.utils import capital_flow as cf
from investment import models


class CapitalFlowView(APIView):

    @staticmethod
    def get(request):
        """获取行业资金流入情况和行业指数涨跌幅"""
        category = request.query_params.get('category')
        date = request.query_params.get('date')
        if date:
            end = parse(date).date()
        else:
            end = models.CapitalFlow.objects.last().date
        start = end - relativedelta(months=3, days=15)
        ret = cf.category_capital_flow(category, start)

        code = category
        pct = models.IndexQuote.objects.filter(secucode=code, date__range=(start, end)).values('date', 'change')
        pct = pd.DataFrame(pct)
        pct['change'] = round(pct['change'].astype('float'), 2)
        ret = ret.merge(pct, how='left', on='date')
        ret = ret.drop(['SIGMA5'], axis=1)
        max_ = ret.max()
        min_ = ret.min()
        max_cf = max([max(
            max_[['MA3', 'MA5', 'MA10', 'MA5_HIGH', 'MA5_LOW']]),
            abs(min(min_[['MA3', 'MA5', 'MA10', 'MA5_HIGH', 'MA5_LOW']]))
        ])
        max_chg = max([max_['change'], abs(min_['change'])])
        max_cf = math.ceil(max_cf/100)*100
        max_chg = math.ceil(max_chg)
        ret = ret.fillna('null')
        ret = ret.to_dict(orient='records')
        return Response({'data': ret, 'max1': max_cf, 'max2': max_chg})

    @staticmethod
    def category(request):
        """获取全部申万行业分类"""
        cate = cf.sw_first_categories()
        return JsonResponse({'data': cate})


class CapitalFlowOutlookView(APIView):
    def get(self, request):
        categories = cf.sw_first_categories()
        info = self.formatter(categories
                              )
        return JsonResponse(info, safe=False)

    def post(self, request):
        secucode = request.data['secucode']
        categories = cf.sw_second_categories(secucode) or [{'secucode': secucode}]
        info = self.formatter(categories)
        return JsonResponse(info, safe=False)

    def formatter(self, categories):
        indexes = [x['secucode'] for x in categories]
        latest = models.IndustryCF.objects.last().date
        info = models.IndustryCF.objects.filter(secucode__in=indexes, date=latest).values()
        info = self.sort(info)
        return info

    @staticmethod
    def sort(data):
        data = pd.DataFrame(data)

        def status(ma3, high, low):
            if ma3 > high:
                return (ma3 - low) / (high - low)
            elif ma3 < low:
                return (ma3 - high) / (high - low)
            return (ma3 - low) / (high - low)

        data['rank'] = data.agg(lambda x: status(x.ma3, x.ma5_high, x.ma5_low), axis=1)
        data = data.sort_values('rank', ascending=False)
        return data.to_dict(orient='records')
