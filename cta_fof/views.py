from django.http.response import JsonResponse
from django.forms.models import model_to_dict
from django.db.models import Sum

from cta_fof import models


def cta_info(request):
    funds = models.Portfolio.objects.filter(valid=True)
    ret = []
    fund: models.Portfolio
    for fund in funds:
        bl = models.Balance.objects.filter(port_code=fund.port_code).latest('date')
        # ble = models.BalanceExpanded.objects.filter(port_code=fund.port_code).latest('date')
        add = added_amount(fund.port_code)
        fund_dict = model_to_dict(fund)
        profit = bl.net_asset - fund.init_money - add
        info = {
            **fund_dict, 'launch_date': fund.launch_date.strftime('%Y-%m-%d'), 'last': bl.date.strftime('%Y-%m-%d'),
            'net_asset': bl.net_asset, 'nav': bl.unit_nav, 'nav_acc': bl.acc_nav, 'cash': bl.savings, 'fa': None,
            'add': add, 'profit': profit
        }
        ret.append(info)
    return JsonResponse({'data': ret})


def added_amount(port_code: str):
    """基金增加份额"""
    add = models.Transactions.objects.filter(
        port_code=port_code, operation='TA申购').aggregate(value=Sum('operation_amount'))['value'] or 0
    minus = models.Transactions.objects.filter(
            port_code=port_code, operation='TA赎回').aggregate(value=Sum('operation_amount'))['value'] or 0
    return add - minus


