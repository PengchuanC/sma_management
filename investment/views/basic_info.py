"""
获取全部组合和组合基础信息
"""

from collections import Counter
from django.db.models import Sum
from rest_framework.views import Response, APIView
from dateutil.parser import parse

from investment.models import portfolio
from investment.utils.date import latest_trading_day


class BasicInfo(APIView):
    @staticmethod
    def get(request):
        last = latest_trading_day(portfolio.Balance)
        ports = portfolio.Portfolio.objects.filter(
            balance__date=last
        ).values(
            'port_code', 'port_type', 'port_name', 'launch_date', 'balance__net_asset', 'init_money',
            'balance__unit_nav', 'balance__acc_nav', 'balance__savings'
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
            'balance__savings': 'cash'
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
            p['last'] = last.strftime('%Y-%m-%d')
            f_ports.append(p)
            count += 1
            total += float(p['net_asset'])
        return Response({'data': f_ports, 'num': count, 'total': total, 'avg': total / count})


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
        rename = {'TA申购': 'purchase', 'TA赎回': 'ransom'}
        ret = portfolio.Transactions.objects.filter(
            date=date, operation__in=['TA申购', 'TA赎回'], port_code__balance__date=date
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
