"""
brinson
~~~~~~~
组合brinson归因
@date: 2020-12-03
@desc: brinson归因按照日频生成
"""

import abc
import datetime
import pandas as pd

from django.db.models import Max
from sql import models
from investment.utils.holding import fund_holding_stock
from investment.utils.holding_v2 import portfolio_holding_stock


class Allocate(abc.ABC):
    """资产配置抽象类

    资产配置的抽象类
    Attributes:
        self.weight: 资产配置比例
        self.change: 资产当日涨跌幅
    """

    @property
    def weight(self):
        """行业配置权重"""
        raise NotImplementedError()

    @property
    def change(self):
        """行业涨跌幅"""
        raise NotImplementedError()


class PortfolioAllocate(Allocate):
    """SMA组合资产配置情况"""
    _weight = pd.DataFrame()

    def __init__(self, port_code: str, date: datetime.date):
        """
        Args:
            port_code (str): 组合代码
            date (datetime.date): 选定的交易日期
        """
        self.p = port_code
        self.d = date

    def _stock_weight(self):
        """股票配置比例

        组合股票配置比例根据组合所持有的基金计算，需要使用到基金在组合中的净值占比
        和股票在基金中的净值占比，前者根据每日估值表可以获得，后者根据公募基金最新
        报告期获取，季报采用前十大持仓，半年报和年报采用完整持仓

        Returns:
            DataFrame: | secucode | weight | industry | change |
        """
        if not self._weight.empty:
            return self._weight
        holding = portfolio_holding_stock(self.p, self.d)
        holding = [{'secucode': x, 'weight': y}for x, y in holding.items()]
        holding = pd.DataFrame(holding)
        holding = holding[holding.weight != 0]
        holding.weight = holding.weight.astype(float)
        holding.weight /= holding.weight.sum()
        if not isinstance(holding, pd.DataFrame):
            return None
        return self._added(holding, self.d)

    @classmethod
    def _added(cls, holding, date):
        stocks = list(holding.secucode)
        m = models.StockIndustrySW
        industry = m.objects.filter(secucode__in=stocks).all()
        industry = {x.secucode.secucode: x.firstindustryname for x in industry}
        holding['industry'] = holding.secucode.apply(lambda x: industry.get(x))
        change = models.StockDailyQuote.objects.filter(
            secucode__in=stocks, date=date
        ).all()
        change = {x.secucode.secucode: x.closeprice / x.prevcloseprice - 1 for x in change}
        holding['change'] = holding.secucode.apply(lambda x: change.get(x))
        return holding

    @staticmethod
    def format_weight_change(data):
        """格式化core返回的结果"""
        sw = models.StockIndustrySW.objects.values('firstindustryname').distinct()
        sw = pd.DataFrame(sw)
        sw = sw.rename(columns={'firstindustryname': 'industry'})
        data = data.reset_index()
        data = pd.merge(sw, data, on='industry', how='left')
        data = data.fillna(0)
        data = data.set_index('industry')
        return data

    @property
    def weight(self):
        """行业配置比例

        行业配置比例指行业市值占权益市值比例
        Returns:
            Series
            >>> self.weight
            industry
            交通运输     0.04712243786184013222487976769
            休闲服务     0.02927308738101760784195512812
            传媒       0.03153064982391022063088072711
        """
        holding = self._stock_weight().copy()
        weight = holding[['industry', 'weight']].groupby('industry').sum()
        weight = weight.weight / weight.weight.sum()
        data = self.format_weight_change(weight)
        return data.weight

    @property
    def change(self):
        """行业涨跌幅

        行业涨跌幅计算方式为 股票涨跌幅*股票权重
        依此法算出的行业涨跌幅实际暗含了在组合在行业权重的影响
        需要除去此影响，即需要计算满仓该行业的涨跌幅
        在计算行业涨跌幅时，并非使用该行业股票涨跌幅的简单平均
        行业涨跌幅=股票涨跌幅*股票占组合权重/行业占组合权重
        Returns:
            Series
            >>> self.change
            industry
            交通运输      0.009384236809883881769665764067
            休闲服务      0.01011928807606773871016248895
            传媒         0.02828580270302707551405546491
        """
        holding = self._stock_weight().copy()
        holding.change = holding.change.astype(float) * holding.weight.astype(float)
        holding = holding.groupby('industry')[['change', 'weight']].sum()
        holding.change = holding.agg(lambda x: x.change / x.weight if x.weight != 0 else 0, axis=1)
        data = holding.change
        data = self.format_weight_change(data)
        return data.change


class IndexAllocate(PortfolioAllocate):
    """指数资产配置情况"""

    def __init__(self, index_code: str, date: datetime.date):
        """
        Args:
            index_code (str): 指数代码，建议使用中证800
            date (datetime.date): 交易日期
        """
        self.i = index_code
        self.d = date
        super(IndexAllocate, self).__init__(index_code, date)

    def _stock_weight(self):
        if not self._weight.empty:
            return self.weight
        md = models.IndexComponent.objects.filter(secucode=self.i).aggregate(m=Max('date')).get('m')
        holding = models.IndexComponent.objects.filter(secucode=self.i, date=md).values('stockcode', 'weight')
        holding = pd.DataFrame(holding)
        holding.weight = holding.weight.astype(float)
        holding.weight /= holding.weight.sum()
        holding = holding.rename(columns={'stockcode': 'secucode'})
        holding = self._added(holding, self.d)
        return holding

    @property
    def weight(self):
        """行业配置比例

        行业配置比例指行业市值占权益市值比例
        Returns:
            Series
            >>> self.weight
            industry
            交通运输     0.04712243786184013222487976769
            休闲服务     0.02927308738101760784195512812
            传媒       0.03153064982391022063088072711
        """
        holding = self._stock_weight().copy()
        weight = holding.groupby('industry')['weight'].sum()
        weight = weight / weight.sum()
        data = self.format_weight_change(weight)
        return data.weight


class Model(object):
    def __init__(self, fund: str, index: str, date: datetime.date):
        self.f = PortfolioAllocate(fund, date)
        self.i = IndexAllocate(index, date)

    @property
    def q1(self):
        """基准收益：基准中行业权重*基准中行业收益"""
        q1 = self.i.weight * self.i.change
        q1.name = 'q1'
        return q1

    @property
    def q2(self):
        """主动资产配置：组合中行业权重*基准中行业收益"""
        q2 = self.f.weight * self.i.change
        q2.name = 'q2'
        return q2

    @property
    def q3(self):
        """主动股票选择：基准中行业权重*组合中行业收益"""
        q3 = self.i.weight * self.f.change
        q3.name = 'q3'
        return q3

    @property
    def q4(self):
        """主动股票选择：组合中行业权重*组合中行业收益"""
        q4 = self.f.weight * self.f.change
        q4.name = 'q4'
        return q4

    @property
    def raa(self):
        """资产配置收益"""
        return self.q2 - self.q1

    @property
    def rss(self):
        """个股选择收益"""
        return self.q3 - self.q1

    @property
    def rin(self):
        """交互作用收益"""
        return self.q4 - self.q3 - self.q2 + self.q1

    @property
    def rtt(self):
        """总收益"""
        return self.q4 - self.q1

    def quick_look(self, preview=False):
        raa = self.raa
        rss = self.rss
        rin = self.rin
        rto = self.rtt
        data = pd.DataFrame(
            [self.q1, self.q2, self.q3, self.q4, raa, rss, rin, rto],
            index=["基准收益(Q1)", "主动资产配置(Q2)", "主动股票选择(Q3)", "组合收益(Q4)", "资产配置", "个股选择", "交叉作用", "超额总收益"]
        ).T
        if preview:
            print(data)
        return data


def commit_brinson():
    """提交Brinson归因数据"""
    index = '000906'
    portfolios = models.Portfolio.objects.filter(settlemented=0).all()
    for p in portfolios:
        dates = models.Balance.objects.filter(port_code=p).order_by('date').values('date')
        dates = [x['date'] for x in dates]
        max_ = models.PortfolioBrinson.objects.filter(port_code=p).aggregate(m=Max('date'))['m']
        if max_:
            dates = [x for x in dates if x > max_]
        dates = sorted(set(dates))
        for date in dates:
            print(p.port_code, date)
            model = Model(p, index, date)
            data = []
            try:
                for attr in ['q1', 'q2', 'q3', 'q4']:
                    data.append(getattr(model, attr))
                data = pd.concat(data, axis=1)
                data = data.reset_index()
                data['port_code'] = p
                data['index'] = index
                data['date'] = date
                to = [models.PortfolioBrinson(**x) for _, x in data.iterrows()]
                models.PortfolioBrinson.objects.bulk_create(to)
            except AttributeError as e:
                print(date, e)
            except Exception as e:
                raise e


if __name__ == '__main__':
    # p = models.Portfolio.objects.get(port_code='PFF005')
    # model = Model(p, index='000906', date=datetime.date(2021, 8, 16))
    # model.q4
    # model.q1
    commit_brinson()
