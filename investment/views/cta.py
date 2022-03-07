"""
@author: chuanchao.peng
@date: 2022/3/7 14:07
@file cta.py
@desc:
"""

import requests as r
import pandas as pd

from django.http.response import JsonResponse
from django.forms.models import model_to_dict
from django.db.models import Sum
from investment.models import Funds, Portfolio, Valuation as Balance, Transactions, Holding, Security


def cta_info(request):
    funds = Portfolio.objects.filter(settlemented=0, port_type__in=(6, ))
    ret = []
    fund: Portfolio
    num = len(funds)
    total = 0
    for fund in funds:
        bl = Balance.objects.filter(port_code=fund.port_code).latest('date')
        add = added_amount(fund.port_code)
        fund_dict = model_to_dict(fund)
        profit = bl.net_asset - fund.init_money - add
        info = {
            **fund_dict, 'launch_date': fund.launch_date.strftime('%Y-%m-%d'), 'last': bl.date.strftime('%Y-%m-%d'),
            'net_asset': bl.net_asset, 'nav': bl.unit_nav, 'nav_acc': bl.acc_nav, 'cash': bl.savings, 'fa': None,
            'add': add, 'profit': profit, 'port_type': 'CTA'
        }
        ret.append(info)
        total += bl.net_asset
    average = total / num
    return JsonResponse({'data': ret, 'total': total, 'num': num, 'avg': average})


def added_amount(port_code: str):
    """基金增加份额"""
    add = Transactions.objects.filter(
        port_code=port_code, operation='TA申购').aggregate(value=Sum('operation_amount'))['value'] or 0
    minus = Transactions.objects.filter(
            port_code=port_code, operation='TA赎回').aggregate(value=Sum('operation_amount'))['value'] or 0
    return add - minus


def holding(request):
    """cta fof持有的基金"""
    port_code = request.GET['port_code']
    last = Holding.objects.filter(port_code=port_code).latest('date').date
    asset = Balance.objects.filter(port_code=port_code, date=last).last().net_asset
    hold = Holding.objects.filter(
        port_code=port_code, date=last).values('secucode', 'current_shares', 'mkt_cap', 'date')
    hold = pd.DataFrame(hold)
    resp = r.get('http://10.170.129.129/cta/api/')
    data = resp.json()['data']
    data = pd.DataFrame(data)
    columns = ['secucode', 'secuabbr', 'recent', 'week', 'month', 'quarter', 'ytd', 'last_year', 'si']
    data = data[columns]
    names = Security.objects.filter(secucode__in=list(hold.secucode))
    names = {x.secucode: x.secuabbr for x in names}
    hold = hold.merge(data, on='secucode', how='left')
    hold.secuabbr = hold.agg(lambda x: names.get(x.secucode), axis=1)
    hold = hold.sort_values('mkt_cap', ascending=False)
    hold['recent'] = hold.agg(lambda x: x.recent if x.recent else x.date, axis=1)
    hold['ratio'] = hold['mkt_cap'] / asset
    hold = hold.astype(object).where(hold.notnull(), None)
    hold = hold.to_dict(orient='records')
    return JsonResponse(hold, safe=False)


def transaction(request):
    port_code = request.GET['port_code']
    secucode = request.GET['secucode']
    data = Transactions.objects.filter(port_code=port_code, secucode=secucode, operation='开放式基金申购成交确认').values()
    data = [x for x in data]
    ret = []
    for x in data:
        v = {
            'secucode': x['secucode'], 'amount': x['subject_amount'], 'share': x['busin_quantity'],
            'price': x['entrust_price'], 'date': x['date']
        }
        ret.append(v)
    return JsonResponse(ret, safe=False)
