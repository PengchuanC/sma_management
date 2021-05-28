"""
获取全部组合和组合基础信息
"""
import pandas as pd

from collections import Counter
from django.db.models import Sum, Count
from rest_framework.views import Response, APIView
from dateutil.parser import parse
from django.http import JsonResponse
from django.forms.models import model_to_dict

from investment.models import portfolio, Balance, Income, ClientPR
from investment.utils.date import latest_trading_day, quarter_end_in_date_series


class BasicInfo(APIView):
    @staticmethod
    def get(request):
        last = latest_trading_day(portfolio.Balance)
        ports = portfolio.Portfolio.objects.filter(
            balance__date=last
        ).values(
            'port_code', 'port_type', 'port_name', 'launch_date', 'balance__net_asset', 'init_money',
            'balance__unit_nav', 'balance__acc_nav', 'balance__savings', 'sales__name', 'balance__security_deposit'
        )
        purchase = portfolio.Transactions.objects.filter(operation='TA申购').values('port_code').annotate(
            money=Sum('operation_amount'))
        purchase = {x['port_code']: x['money'] for x in purchase}
        redemption = portfolio.Transactions.objects.filter(operation='TA赎回').values('port_code').annotate(
            money=Sum('operation_amount'))
        redemption = {x['port_code']: x['money'] for x in redemption}
        add = dict(Counter(purchase) + Counter(redemption))
        profit = portfolio.Income.objects.values('port_code').annotate(profit=Sum('change'))
        profit = {x['port_code']: x['profit'] for x in profit}
        rename = {
            'balance__net_asset': 'net_asset', 'balance__unit_nav': 'nav', 'balance__acc_nav': 'nav_acc',
            'sales__name': 'fa'
        }
        f_ports = []
        pt = {1: '现金型', 2: '固收型', 3: '平衡型', 4: '成长型', 5: '权益型'}
        count = 0
        total = 0
        for p in ports:
            for o, n in rename.items():
                p[n] = p.pop(o)
            p['launch_date'] = p['launch_date'].strftime('%Y-%m-%d')
            p['add'] = add.get(p['port_code'])
            p['profit'] = profit.get(p['port_code'])
            p['port_type'] = pt.get(p['port_type'])
            p['key'] = count
            p['cash'] = p.pop('balance__savings') + p.pop('balance__security_deposit')
            p['last'] = last.strftime('%Y-%m-%d')
            f_ports.append(p)
            count += 1
            total += float(p['net_asset'])
        return Response(
            {'data': f_ports, 'num': count, 'total': total, 'avg': total / count, 'last': last.strftime('%Y-%m-%d')})


class Capital(APIView):
    """当日出金和入金"""

    @staticmethod
    def get(request):
        date = request.query_params.get('date')
        if not date:
            date = portfolio.Balance.objects.last().date
        else:
            date = parse(date).date()
        date = portfolio.Balance.objects.filter(date__lte=date).last().date
        rename = {'TA申购冲现': 'purchase', 'TA赎回冲现': 'ransom'}
        ret = portfolio.Transactions.objects.filter(
            date=date, operation__in=['TA申购冲现', 'TA赎回冲现'], port_code__balance__date=date
        ).values('operation').annotate(amount=Sum('operation_amount')).values(
            'operation', 'amount', 'port_code__balance__unit_nav'
        )

        ret = {rename.get(x['operation']): x['amount'] if x['operation'] == 'TA申购' else x['amount'] * x[
            'port_code__balance__unit_nav'] for x in ret}

        pr = []
        if ret:
            # 检测到当日有申赎，查询具体申赎纪录
            pr_ = portfolio.Transactions.objects.filter(
                date=date, operation__in=list(rename.keys()), port_code__balance__date=date
            ).values(
                'port_code', 'operation', 'operation_amount', 'port_code__balance__unit_nav',
                'port_code__port_name'
            )
            count = 1
            for _pr in pr_:
                _pr['nav'] = _pr.pop('port_code__balance__unit_nav')
                _pr['port_name'] = _pr.pop('port_code__port_name')
                _pr['key'] = count
                pr.append(_pr)
                count += 1
        return Response({'total': ret, 'date': date.strftime('%Y-%m-%d'), 'detail': pr})


class ProfitAttribute(object):
    """全部sma产品盈亏分布情况

    """

    @staticmethod
    def quarter(request):
        """每季度增加资金

        Args:
            request: Django request object

        Returns:
            季度末新增资金

        """
        dates = Balance.objects.filter(port_code__valid=True).values('date').order_by('date').distinct()
        dates = [x['date'] for x in dates]
        dates = quarter_end_in_date_series(dates)
        asset = Balance.objects.filter(
            port_code__valid=True, date__in=dates
        ).values('date').annotate(s=Sum('asset'), c=Count('asset'))
        asset = [x for x in asset]
        asset = [{'date': 0, 's': 0, 'c': 0}] + asset
        asset = pd.DataFrame(asset).set_index('date')
        asset = asset.diff(1).dropna()
        total = asset.sum()
        asset = asset.reset_index()
        asset.date = asset.date.apply(lambda x: x.strftime('%Y%m'))
        asset = asset.to_dict(orient='records')
        total = total.to_dict()
        asset.append({'date': '合计', 's': total['s'], 'c': total['c']})
        return JsonResponse({'data': asset})

    @staticmethod
    def profit(request):
        """全部sma产品盈亏分布情况

        Args:
            request: Django request object

        Returns:

        """
        profit_sum = Income.objects.filter(port_code__valid=True).values('port_code').annotate(s=Sum('change'))
        profit = {'up': 0, 'down': 0}
        count = {'up': 0, 'down': 0}
        for p in profit_sum:
            if p['s'] > 0:
                count['up'] += 1
                profit['up'] += p['s']
            else:
                count['down'] += 1
                profit['down'] += p['s']
        return JsonResponse({'profit': profit, 'count': count})


class PurchaseAndRansom(APIView):
    """客户申购赎回申请

    """

    @staticmethod
    def get(request):
        """全部未完成申请赎回记录

        Args:
            request:

        Returns:

        """
        completed = ClientPR.objects.filter(complete=True).all()
        completed = [PurchaseAndRansom.to_dict(x) for x in completed]
        uncompleted = ClientPR.objects.filter(complete=False).all()
        uncompleted = [PurchaseAndRansom.to_dict(x) for x in uncompleted]
        return Response({'completed': completed, 'uncompleted': uncompleted})

    @staticmethod
    def put(request):
        idx = request.query_params.get('id')
        ret: ClientPR = ClientPR.objects.get(id=idx)
        ret.complete = True
        ret.save()
        return Response({'code': 0})

    @staticmethod
    def to_dict(m):
        ret = model_to_dict(m)
        ret['key'] = ret['id']
        return ret
