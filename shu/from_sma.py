"""
from_sma
~~~~~~~~
从sma客户服务系统导入组合数据
第一版采用导出excel文件再读取的方式，性能消耗过大
因此第二版采用rpc服务读取数据，保存到另一个数据库
"""
import datetime

from django.db import transaction
from django.db.models import Max

import serializers.server_pb2 as pb
from serializers.client import SMABackendServices
from shu import models
from sma_management.logger import logger


class Shu(object):

    def __init__(self, host: str, port: int):
        self.client = SMABackendServices(host, port)

    @staticmethod
    def _get_portfolio():
        data = models.Portfolio.objects.filter(settlemented=0)
        for p in data:
            yield p.port_code

    @staticmethod
    def _max_date(model, port_code):
        date = model.objects.filter(
            port_code_id=port_code).aggregate(md=Max('date'))['md'] or datetime.date(2020, 1, 1)
        date = date.strftime('%Y-%m-%d')
        return date

    def portfolio(self):
        for p in self.client.portfolio():
            models.Portfolio.objects.update_or_create(
                id=p.id, defaults={
                    'port_code': p.port_code, 'port_name': p.port_name, 'port_type': p.port_type,
                    'benchmark': p.benchmark, 't_n': p.t_n, 'settlemented': p.settlemented
                }
            )
        for pe in self.client.portfolio_ex():
            models.PortfolioExpanded.objects.update_or_create(
                id=pe.id, defaults={
                    'init_money': pe.init_money, 'activation': pe.activation, 'fund_id': pe.fund_id,
                    'launch': pe.launch, 'port_code_id': pe.port_code_id
                }
            )
        logger.info('portfolio sync succeed')

    def balance(self):
        ba = ['asset', 'debt', 'net_asset', 'unit_nav', 'accu_nav', 'nav_increment', 'date', 'port_code_id']
        bea = [
            'savings', 'settlement_reserve', 'deposit', 'stocks', 'bonds', 'abs', 'funds', 'metals', 'other',
            'resale_agreements', 'purchase_rec', 'ransom_pay', 'date', 'port_code_id'
        ]
        for p in self._get_portfolio():
            date = self._max_date(models.Valuation, p)
            for b in self.client.balance(p, date):
                models.Valuation.objects.update_or_create(
                    id=b.id, defaults={x: getattr(b, x) for x in ba}
                )
            for be in self.client.balance_ex(p, date):
                models.ValuationEx.objects.update_or_create(
                    id=be.id, defaults={x: getattr(be, x) for x in bea}
                )
            date = self._max_date(models.ValuationBenchmark, p)
            for bm in self.client.balance_benchmark(p, date):
                models.ValuationBenchmark.objects.update_or_create(
                    id=bm.id, defaults={'unit_nav': bm.unit_nav, 'date': bm.date, 'port_code_id': bm.port_code_id}
                )
        logger.info('balance sync succeed')

    def transaction(self):
        va = ['digest', 'code', 'value', 'date', 'port_code_id']
        ta = [
            'date', 'operation', 'operation_flag', 'secucode', 'entrust_quantity', 'entrust_price',  'busin_quantity',
            'occur_amount', 'subject_amount', 'fare', 'note', 'market', 'port_code_id'
        ]
        ha = [
            'date', 'secucode', 'market', 'begin_shares', 'current_shares', 'mkt_cap', 'today_fare', 'fare',
            'today_dividend', 'dividend', 'today_profit', 'profit', 'port_code_id'
        ]
        for p in self._get_portfolio():
            date = self._max_date(models.Vouchers, p)
            for v in self.client.voucher(p, date):
                models.Vouchers.objects.update_or_create(
                    id=v.id, defaults={x: getattr(v, x) for x in va}
                )
            date = self._max_date(models.Transactions, p)
            for t in self.client.trans(p, date):
                models.Transactions.objects.update_or_create(
                    id=t.id, defaults={x: getattr(t, x) for x in ta}
                )
            date = self._max_date(models.Holding, p)
            for h in self.client.holding(p, date):
                models.Holding.objects.update_or_create(
                    id=h.id, defaults={x: getattr(h, x) for x in ha}
                )
        logger.info('transactions sync succeed')

    def security(self):
        sa = ['secucode', 'secuabbr', 'category', 'category_code']
        sca = ['first', 'second', 'secucode_id']
        sqa = ['quote', 'note', 'date', 'auto_date', 'port_code_id', 'secucode_id']
        for s in self.client.security():
            models.Security.objects.update_or_create(
                id=s.id, defaults={x: getattr(s, x) for x in sa}
            )
        for sc in self.client.security_category():
            models.SecurityCategory.objects.update_or_create(
                id=sc.id, defaults={x: getattr(sc, x) for x in sca}
            )
        for p in self._get_portfolio():
            date = self._max_date(models.SecurityQuote, p)
            for sq in self.client.security_quote(p, date):
                models.SecurityQuote.objects.update_or_create(
                    id=sq.id, defaults={x: getattr(sq, x) for x in sqa}
                )
        logger.info('security sync succeed')

    def income(self):
        ia = ['date', 'unit_nav', 'net_asset_chg', 'total_net_asset_chg', 'unit_nav_chg', 'port_code_id']
        iea = [
            'date', 'total', 'today_total', 'equity', 'today_equity', 'fix_income', 'today_fix_income', 'alternative',
            'today_alternative', 'monetary', 'today_monetary', 'fare', 'today_fare', 'other', 'today_other',
            'port_code_id'
        ]
        for p in self._get_portfolio():
            date = self._max_date(models.Income, p)
            for i in self.client.income(p, date):
                models.Income.objects.update_or_create(
                    id=i.id, defaults={x: getattr(i, x) for x in ia}
                )
            date = self._max_date(models.IncomeEx, p)
            for ie in self.client.income_ex(p, date):
                models.IncomeEx.objects.update_or_create(
                    id=ie.id, defaults={x: getattr(ie, x) for x in iea}
                )
        logger.info('income sync succeed')

    def users(self):
        ca = ['username', 'password', 'chiname', 'identify_no', 'mobile', 'gender', 'role']
        sa = ['username', 'telephone', 'email']
        cma = ['holder_id', 'port_code_id']
        sma = ['port_code_id', 'sales_id']
        for c in self.client.customer():
            models.User.objects.update_or_create(
                id=c.id, defaults={x: getattr(c, x) for x in ca}
            )
        for s in self.client.sales():
            models.NomuraOISales.objects.update_or_create(
                id=s.id, defaults={x: getattr(s, x) for x in sa}
            )
        for cm in self.client.customer_mapping():
            models.ProductUserMapping.objects.update_or_create(
                id=cm.id, defaults={x: getattr(cm, x) for x in cma}
            )
        for sm in self.client.sales_mapping():
            models.ProductSalesMapping.objects.update_or_create(
                id=sm.id, defaults={x: getattr(sm, x) for x in sma}
            )
        logger.info('user sync succeed')

    def pr(self):
        pa = [
            'date', 'confirm', 'pr_quantity', 'pr_amount', 'rs_quantity', 'rs_amount', 'pr_fee_backend', 'rs_fee',
            'rs_fee_org', 'org_name', 'port_code_id'
        ]
        for p in self._get_portfolio():
            date = self._max_date(models.PurchaseAndRansom, p)
            for i in self.client.pr(p, date):
                models.PurchaseAndRansom.objects.update_or_create(
                    id=i.id, defaults={x: getattr(i, x) for x in pa}
                )
        logger.info('purchase-ransom sync succeed')

    def start(self):
        with transaction.atomic():
            self.portfolio()
            self.security()
            self.users()
            self.balance()
            self.transaction()
            self.income()
        self.client.close()


def commit_sma():
    """从客户服务系统更新sma数据"""
    shu = Shu('10.170.129.129', 50060)
    shu.start()


__all__ = ('commit_sma',)


if __name__ == '__main__':
    commit_sma()
