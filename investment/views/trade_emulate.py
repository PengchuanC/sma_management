"""
trade_emulate
~~~~~~~~~~~~~
组合模拟调仓

1、A、B、C 三支基金为全集(先计算赎回金额)
A 33% B 34% C 33%
假定调整为 A 30% B 38% C 32%
FIFO计算A 3% +C 1%赎回费，以及B 4%申购费*折扣费率档（折扣费率档需要可设定）
输出投资指令

2、A、B、C、D四支基金为全集，A、B为权益类基金，C、D为债券类基金(先计算申购需要金额)
A 25% B 25% C 25% D 25%
假定需要提升权益类基金由50%至60%：
    篮子下单：按当前市值比例分配给A、B基金，即10%中各分配5%给A、B
a.	判定C、D是否与A、B隶属同一基金公司，确保转换两端不存在同一基金公司产品
b.	预估10%权益类基金对应金额，按照T-1日组合市值*10%估算金额
c.	按照50%：50%分配至A、B基金计算应转入金额
d.	按照90%的转换比例，计算应转出金额=A应转入金额/(1-申购费率*折扣费率档) + B应转入金额/(1-申购费率*折扣费率档)，
e.	比较C、D赎回费，按照FIFO原则，对比C、D当前持仓份额对应的历次申购份额所持有时间适用的赎回费档，优先赎回最低赎回费档，
    直至满足C转出份额*T-1日净值*（1-赎回费率）*90%+ D转出份额*T-1日净值*（1-赎回费率）*90%=应转出金额，对应的C转出份额和D转出份额
f.	输出投资指令
"""

import datetime
import pandas as pd

from collections import OrderedDict
from functools import lru_cache
from django.db.models import Sum
from django.http import Http404, HttpResponse, JsonResponse
from decimal import Decimal
from rest_framework.views import APIView, Response
from copy import deepcopy
from investment import models
from investment.utils import fund as fund_util

# 投资指令模板
from investment.utils.download import file_dir

instruct_template = OrderedDict({
    '基金代码': '', '组合编号': '', '投资类型': '1', '证券代码': '', '委托方向': 'E', '指令金额': 0, '指令数量': 0, '分红方式': 2,
    '巨额赎回标志': 1, '开始日期': None, '结束日期': None, '转入组合编号': '', '转入投资类型': '1', '转入证券代码': '',
    '基金名称': '', '组合名称': '', '转入组合名称': None, '销售渠道': None
})


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
            elif d.low <= money / 10000 < d.high:
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


# 复杂模式，批量转换或篮子下单
class ComplexEmuView(APIView):
    """批量基金转换
    """

    def post(self, request):
        ret = self.case_one(request)
        return Response(ret)

    def case_one(self, request):
        """第一种情况

        多支基金转换为同一支基金，先赎回后申购，利用赎回金额的90%来申购新基金
        Args:
            request: drf request object, must contain dst、src and portCode field. :
            {'portCode': 'SA5001', 'src': [{'secucode': '166005', 'secuname': '中欧价值A', 'ratio': '0.035',
            'target': '0.005'}], 'dst': '166005'}
        Returns:
            Examples: abc
        """
        data = request.data
        dst = data.get('dst')
        src = data.get('src')
        port_code = data.get('portCode')

        # 根据赎回百分比计算赎回基金的赎回份额和合计赎回金额
        amount = 0  # 合计赎回金额
        records = []  # 赎回份额
        template = []  # 投资指令模板
        asset = models.Balance.objects.filter(port_code=port_code).last().net_asset
        date = datetime.date.today()
        count = 0
        for src_ in src:
            change = Decimal(src_['ratio']) - Decimal(src_['target']) / 100
            money = change * asset
            secucode = src_['secucode']
            nav = models.FundAdjPrice.objects.filter(secucode=secucode).last().nav
            share = round(money / nav, 2)
            money = round(share * nav, 2)
            monetary = fund_util.fund_is_monetary(secucode)
            if monetary:
                amount += money
            else:
                amount += money * Decimal(0.9)
            t = deepcopy(instruct_template)
            update = OrderedDict({'基金代码': port_code, '证券代码': secucode, '指令数量': share, '转入证券代码': dst})
            t.update(update)
            template.append(t)
            rf = RansomFee(secucode)
            r_fee = rf.calc_fee_ratio(date)
            records.append({
                'secucode': secucode, 'operate': '转出', 'amount': share,
                'fee': round(r_fee * nav * share, 2), 'key': count, 'secuname': src_['secuname']
            })
            count += 1
        amount = round(float(amount), 2)
        p = PurchaseFee(dst)
        p_fee, _ = p.calc_purchase_fee(amount)
        name = models.Funds.objects.get(secucode=dst).secuname
        records.append({
            'secucode': dst, 'secuname': name, 'operate': '转入', 'amount': amount, 'fee': round(p_fee, 2), 'key': count
        })
        template = pd.DataFrame(template)
        self.generate_instruct(template)
        return records

    @staticmethod
    def fund_holding_ratio(port_code: str, funds: list or None):
        """基金在组合中的市值占比

        Args:
            port_code: 组合代码
            funds: 基金列表
        Returns:
            指定基金的持仓市值
            Examples: {'110011': 0.05}
        """
        date = models.Holding.objects.filter(port_code=port_code).last().date
        if funds:
            hold = models.Holding.objects.filter(port_code=port_code, secucode__in=funds, date=date).all()
        else:
            hold = models.Holding.objects.filter(port_code=port_code, date=date).all()
        asset = models.Balance.objects.filter(port_code=port_code).last().net_asset
        ratio = {x.secucode: x.mkt_cap / asset for x in hold}
        return ratio

    @staticmethod
    def fund_holding_ratio_http(request):
        """将基金持仓以JsonResponse返回"""
        port_code: str = request.GET.get('portCode')
        date = models.Holding.objects.filter(port_code=port_code).last().date
        hold = models.Holding.objects.filter(port_code=port_code, date=date).values('secucode', 'mkt_cap')
        funds = [x['secucode'] for x in hold]
        names = models.Funds.objects.filter(secucode__in=funds).all()
        names = {x.secucode: x.secuname for x in names}
        asset = models.Balance.objects.filter(port_code=port_code).last().net_asset
        ret = [{'secucode': x['secucode'], 'secuname': names.get(x['secucode']), 'ratio': x['mkt_cap'] / asset}
               for x in hold]
        return JsonResponse({'data': ret})

    @staticmethod
    def generate_instruct(data: pd.DataFrame):
        """生成投资指令
        Args:
            data: 根据投资指令模板生成的数据
        """
        date = datetime.date.today().strftime('%Y%m%d')
        path = file_dir / f'SMA_{date}.xlsx'
        data.to_excel(path, sheet_name='导入指令Clean', index=False)

    @staticmethod
    def download(request):
        date = datetime.date.today().strftime('%Y%m%d')
        file_path = file_dir / f'SMA_{date}.xlsx'
        if file_path.is_file():
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + file_path.name
                return response
        raise Http404


class ComplexEmuBulkView(ComplexEmuView):
    """批量转换模式"""

    def post(self, request):
        ret = self.case_two(request)
        return Response(ret)

    def case_two(self, request):
        """第二种转换模式

        将C、D基金转换为A、B基金，过程中注意同一基金公司不得互相转换
        """
        data = request.data
        dst = data.get('dst')
        src = data.get('src')
        port_code = data.get('portCode')
        rise = data.get('rise') / 100
        date = datetime.date.today()

        funds = [x['secucode'] for x in dst] + [x['secucode'] for x in src]
        asset = models.Balance.objects.filter(port_code=port_code).last().net_asset
        need = asset * Decimal(rise) / Decimal(0.9)  # 赎回金额需要达到的值
        information = []
        for src_ in src:
            secucode = src_['secucode']
            info = SimpleEmuView.get_fund_available(port_code, secucode)
            for inf in info:
                inf.update({'secucode': secucode})
                information.append(inf)
        information = pd.DataFrame(information)
        information = information[information.available > 0]
        information = information.sort_values(by='fee')  # 按费用升序排列的可用份额明细

        advisors = models.FundAdvisor.objects.filter(secucode__in=funds).all()
        advisors = {x.secucode.secucode: x for x in advisors}

        average = need / len(dst)
        template = []
        records = []
        count = 0
        src_name = {x['secucode']: x['secuname'] for x in src}
        for dst_ in dst:
            secucode = dst_['secucode']
            need_amount = average
            for idx, row in information.copy().iterrows():
                sell_code = row['secucode']
                if row.available == 0:
                    continue
                if advisors.get(secucode) == advisors.get(sell_code):  # 同一基金公司，跳过
                    continue
                if round(need_amount, 2) == 0:
                    break
                nav = models.FundAdjPrice.objects.filter(secucode=sell_code).last().nav
                need_shares = round(need_amount / nav, 2)
                if need_shares < row.available:
                    shares = need_shares
                    need_amount -= need_shares * nav
                    information.loc[idx, 'available'] = Decimal(row.available) - shares
                else:
                    shares = Decimal(row.available)
                    need_amount -= shares * nav
                    information.loc[idx, 'available'] = 0
                t = deepcopy(instruct_template)
                if shares != 0:
                    r = RansomFee(sell_code)
                    r_fee = r.calc_fee_ratio(date) * shares * nav
                    records.append(
                        {'secucode': sell_code, 'secuname': src_name[sell_code], 'operate': '转出', 'amount': shares,
                         'fee': r_fee, 'key': count})
                    update = OrderedDict(
                        {'基金代码': port_code, '基金名称': dst_['secuname'], '证券代码': sell_code, '指令数量': shares,
                         '转入证券代码': secucode})
                    t.update(update)
                    template.append(t)
                    count += 1
            p = PurchaseFee(secucode)
            p_amount, _ = p.calc_purchase_fee(float(average))
            records.append({'secucode': secucode, 'secuname': dst_['secuname'], 'operate': '转入', 'amount': average,
                            'fee': p_amount, 'key': count})
            count += 1
        template = pd.DataFrame(template)
        self.generate_instruct(template)
        return records
