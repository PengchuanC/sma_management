"""
获取全部组合和组合基础信息
"""
import pandas as pd

from collections import Counter
from django.db.models import Sum, Count, Max
from rest_framework.views import Response, APIView
from dateutil.parser import parse
from django.http import JsonResponse
from django.forms.models import model_to_dict

from investment import models
from investment.models import portfolio, Valuation, Income, ClientPR
from investment.utils.date import latest_trading_day, quarter_end_in_date_series


class BasicInfo(APIView):

    @staticmethod
    def get(request):
        ps = models.Portfolio.objects.filter(settlemented=0).order_by('port_code')
        last = models.Valuation.objects.filter(port_code__settlemented=0).values('port_code').annotate(m=Max('date'))
        last = {x['port_code']: x['m'] for x in last}
        ret = {'sma': [], 'cta': []}
        sma_key = 1
        cta_key = 1
        sma_stat = {'num': 0, 'total': 0, 'avg': 0}
        cta_stat = {'num': 0, 'total': 0, 'avg': 0}
        for p in ps:
            date = last.get(p.port_code)
            if not date:
                continue
            pex = p.portfolioexpanded
            v = models.Valuation.objects.get(port_code=p, date=date)
            vex = models.ValuationEx.objects.get(port_code=v)
            pr = list(models.PurchaseAndRansom.objects.filter(port_code=p).order_by('date'))
            if pr:
                init = pr[0].pr_amount
                pr = pr[1:]
            else:
                init = 0
                pr = []
            ic = models.Income.objects.get(port_code=p, date=date)
            add = sum([x.pr_amount-x.rs_amount for x in pr])
            cash = vex.savings + vex.deposit
            fa = models.ProductSalesMapping.objects.filter(port_code=p)
            fa = fa[0].sales.username if fa else ''
            need = {
                'port_code': p.port_code, 'port_name': p.port_name, 'port_type': p.port_type, 'nav': float(v.unit_nav),
                'nav_acc': float(v.accu_nav), 'launch_date': pex.launch.strftime('%Y-%m-%d'),
                'init_money': float(init), 'add': float(add), 'net_asset': float(v.net_asset),
                'profit': float(ic.total_net_asset_chg), 'last': date.strftime('%Y-%m-%d'), 'cash': float(cash),
                'fa': fa if fa != 'AM FOF' else '',
            }
            if p.port_type != 'CTA':
                need['key'] = sma_key
                ret['sma'].append(need)
                sma_stat['num'] += 1
                sma_stat['total'] += float(v.net_asset)
                sma_key += 1
            else:
                need['key'] = cta_key
                ret['cta'].append(need)
                cta_stat['num'] += 1
                cta_stat['total'] += float(v.net_asset)
                cta_key += 1
        sma_stat['avg'] = sma_stat['total'] / sma_stat['num']
        cta_stat['avg'] = cta_stat['total'] / cta_stat['num']
        ret.update({'sma_stat': sma_stat, 'cta_stat': cta_stat})
        return JsonResponse(ret)


class Capital(APIView):
    """当日出金和入金"""

    @staticmethod
    def get(request):
        date = request.query_params.get('date')
        if not date:
            date = portfolio.Balance.objects.last().date
        else:
            date = parse(date).date()
        date = portfolio.Valuation.objects.filter(date__lte=date).last().date
        pr = models.PurchaseAndRansom.objects.filter(
            date__lte=date).values('confirm', 'pr_amount', 'rs_amount', 'rs_fee')
        pr = pd.DataFrame(pr)
        pr['net'] = pr['pr_amount'] - pr['rs_amount']
        pr = pr.groupby('confirm').sum().astype(float).reset_index().sort_values('confirm', ascending=False)
        pr['key'] = range(1, len(pr)+1)
        p_total = pr['pr_amount'].sum()
        r_total = pr['rs_amount'].sum()
        n_total = pr['net'].sum()
        pr = pr.to_dict(orient='records')
        return Response({'data': pr, 'p_total': p_total, 'r_total': r_total, 'n_total': n_total})


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
        dates = models.Valuation.objects.filter(port_code__settlemented=0).values('date').order_by('date').distinct()
        dates = [x['date'] for x in dates]
        dates = quarter_end_in_date_series(dates)
        asset = models.Valuation.objects.filter(
            port_code__settlemented=0, date__in=dates
        ).values('date').annotate(s=Sum('net_asset'), c=Count('net_asset'))
        asset = [x for x in asset]
        asset = sorted(asset, key=lambda x: x['date'])
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
        profit_sum = models.Income.objects.filter(
            port_code__settlemented=0).values('port_code').annotate(s=Sum('net_asset_chg'))
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
        completed = models.PurchaseAndRansom.objects.values()
        completed = [x for x in completed]
        return Response({'completed': completed})

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
