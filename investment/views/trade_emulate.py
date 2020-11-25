"""
trade_emulate
~~~~~~~~~~~~~
组合模拟调仓

1、A、B、C 三支基金为全集
A 33% B 34% C 33%
假定调整为 A 30% B 38% C 32%
FIFO计算A 3% +C 1%赎回费，以及B 4%申购费*折扣费率档（折扣费率档需要可设定）
输出投资指令

2、A、B、C、D四支基金为全集，A、B为权益类基金，C、D为债券类基金
A 25% B 25% C 25% D 25%
假定需要提升权益类基金由50%至60%：
    篮子下单：按当前市值比例分配给A、B基金，即10%中各分配5%给A、B
a.	判定C、D是否与A、B隶属同一基金公司，确保转换两端不存在同一基金公司产品
b.	预估10%权益类基金对应金额，按照T-1日组合市值*10%估算金额
c.	按照50%：50%分配至A、B基金计算应转入金额
d.	按照90%的转换比例，计算应转出金额=A应转入金额/(1-申购费率*折扣费率档) + B应转入金额/(1-申购费率*折扣费率档)，
e.	比较C、D赎回费，按照FIFO原则，对比C、D当前持仓份额对应的历次申购份额所持有时间适用的赎回费档，优先赎回最低赎回费档，
    直至满足C转出份额*T-1日净值*（1-赎回费率）/90%+ D转出份额*T-1日净值*（1-赎回费率）/90%=应转出金额，对应的C转出份额和D转出份额
f.	输出投资指令
"""

import datetime

from functools import lru_cache
from django.db.models import Sum
from django.http import JsonResponse
from rest_framework.views import APIView, Response
from investment import models


class RansomFee(object):
    """计算赎回适用费率档"""

    data = None

    def __init__(self, secucode: str):
        self.s = secucode
        self.init()

    def init(self):
        """获取费率数据"""
        fpf = models.FundPurchaseFee
        data = fpf.objects.filter(secucode=self.s, operate='sell').all()
        self.data = data

    def calc_fee_ratio(self, date: datetime.date):
        """计算赎回适用费率档"""
        days = (datetime.date.today() - date).days
        r: models.FundPurchaseFee
        for r in self.data:
            if r.low <= days and not r.high:
                return r.fee
            elif r.low <= days < r.high:
                return r.fee


class PurchaseFee(object):
    """计算前端申购适用费率档"""
    data = None

    def __init__(self, secucode):
        self.s = secucode
        self.init()

    def init(self):
        fpf = models.FundPurchaseFee
        data = fpf.objects.filter(secucode=self.s, operate='buy').all()
        self.data = data

    def calc_purchase_fee(self, money: float):
        """输入申购金额，计算申购费"""
        for d in self.data:
            if all({money / 10000 >= d.low, d.high is None}):
                return d.fee, d.fee
            elif d.low <= money/10000 < d.high:
                return float(d.fee) * money, d.fee
        return None


# 简易模式，计算单只基金数据
class SimpleEmuView(APIView):
    @staticmethod
    def get_portfolio(request):
        data: list = models.Portfolio.objects.all()
        data = [{'port_code': x.port_code, 'port_name': x.port_name, 'id': x.id} for x in data]
        return JsonResponse({'data': data})

    @staticmethod
    def get_portfolio_cash(request):
        """获取组合最新可用现金"""
        port_code: str = request.GET.get('portCode')
        balance = models.Balance.objects.filter(port_code=port_code).last()
        cash = balance.savings
        date = balance.date.strftime('%Y-%m-%d')
        funds = models.Holding.objects.filter(port_code=port_code, date=date).values('secucode').distinct()
        funds = [x['secucode'] for x in funds]
        funds = models.FundStyle.objects.filter(secucode__in=funds, fundtype='货币市场型基金').values('secucode').distinct()
        funds = [x['secucode'] for x in funds]
        shares = models.Holding.objects.filter(
            port_code=port_code, secucode__in=funds, date=date
        ).aggregate(shares=Sum('holding_value'))['shares']
        return JsonResponse({'date': date, 'cash': cash, 'shares': shares})

    @staticmethod
    def get_funds(request):
        """获取基金列表"""
        keyword: str = request.GET.get('keyword')
        port_code: str = request.GET.get('portCode')
        if not port_code:
            return JsonResponse({'data': []})
        if not keyword:
            data = models.Holding.objects.filter(port_code=port_code).values('secucode').distinct()
        else:
            data = models.Holding.objects.filter(
                secucode__istartswith=keyword, port_code=port_code
            ).values('secucode').distinct()
        secucode = [x['secucode'] for x in data]
        data = models.Funds.objects.filter(secucode__in=secucode).values('secucode', 'secuname')
        data = [x for x in data]
        return JsonResponse({'data': data})

    @staticmethod
    def get_fund_nav(request):
        """获取单只基金净值"""
        secucode: str = request.GET.get('secucode')
        nav, date = SimpleEmuView._get_fund_nav(secucode)
        port_code: str = request.GET.get('portCode')
        available = 0
        if port_code and secucode:
            last = models.Holding.objects.filter(port_code=port_code, secucode=secucode).last()
            available = last.holding_value if last else available
        return JsonResponse({'fund': secucode, 'nav': nav, 'date': date, 'available': available})

    @staticmethod
    def _get_fund_nav(secucode: str):
        data: models.FundAdjPrice = models.FundAdjPrice.objects.filter(secucode=secucode).last()
        nav = data.nav
        date = data.date.strftime('%Y-%m-%d')
        return nav, date

    @staticmethod
    def get_trading_history(request):
        """获取基金交易记录"""
        secucode: str = request.GET.get('secucode')
        port_code: str = request.GET.get('portCode')
        if not secucode or not port_code:
            return JsonResponse({'data': []})

        ret_ = SimpleEmuView.get_fund_available(port_code, secucode)

        return JsonResponse({'data': ret_})

    @staticmethod
    @lru_cache()
    def get_fund_available(port_code: str, secucode: str):
        """获取基金在不同费率档下可用数量"""
        data = models.Holding.objects.filter(port_code=port_code, secucode=secucode).order_by('date').all()
        ret = []
        prev = 0
        ransom = 0
        rf = RansomFee(secucode)
        for i, d in enumerate(data):
            buy_amount = round(float(d.holding_value) - prev, 2)
            if buy_amount == 0:
                continue
            elif buy_amount < 0:
                ransom += buy_amount
            prev = float(d.holding_value)
            r = {'key': i, 'date': d.date, 'buy_amount': buy_amount, 'amount': prev, 'fee': rf.calc_fee_ratio(d.date)}
            ret.append(r)

        ret_ = []
        for x in ret:
            if x['buy_amount'] < 0:
                x['available'] = 0
            else:
                available = x['buy_amount'] + ransom
                if available >= 0:
                    ransom = 0
                    x['available'] = available
                else:
                    ransom = available
                    x['available'] = available
            ret_.append(x)
        return ret_

    @staticmethod
    def get_ransom_fee(request):
        """计算赎回费用"""
        secucode: str = request.GET.get('secucode')
        port_code: str = request.GET.get('portCode')
        shares = request.GET.get('shares')
        if any({not shares, not secucode, not port_code}):
            return JsonResponse({'fee': None})
        available = SimpleEmuView.get_fund_available(port_code, secucode)
        nav, _ = SimpleEmuView._get_fund_nav(secucode)
        shares = float(shares)
        fee = 0
        for r in available:
            ava = r['available']
            ratio = r['fee']
            if shares < ava:
                fee += shares * float(nav) * float(ratio)
                break
            else:
                fee += ava * float(nav) * float(ratio)
                shares -= ava
        return JsonResponse({'fee': fee})

    @staticmethod
    def get_purchase_fee(request):
        secucode: str = request.GET.get('secucode')
        money: str = request.GET.get('money')
        if any({not secucode, not money}):
            return JsonResponse({'fee': None, 'ratio': None})
        pf = PurchaseFee(secucode)
        fee, ratio = pf.calc_purchase_fee(float(money))
        return JsonResponse({'fee': fee, 'ratio': ratio})
