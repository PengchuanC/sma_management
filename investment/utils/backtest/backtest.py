import datetime
import pandas as pd

from copy import deepcopy
from .configs import BTConfig
from ...models import FundAdjPrice as FundNav


class BackTest(object):
    """回测模块"""
    w = None
    nav = None
    inited = False
    cap = 0
    change_date = None

    def __init__(self, config: BTConfig):
        self.c = deepcopy(config)

    def init(self):
        """初始化回测需要的数据"""
        self.load_weight()
        self.load_funds_adj_nav()
        self.cap = self.c.init_money
        self.inited = True

    def load_weight(self):
        """载入权重数据"""
        w = self.c.set_weight_data().set_index('date')
        w['equity'] = w['hs300'] + w['zz500'] + w['zz'] + w['hs']
        w['bond'] = w['zcf'] + w['qyz']
        w['alter'] = w['hj']
        w['cash'] = w['hb']
        self.w = w[['target_risk', 'equity', 'bond', 'alter', 'cash']].astype('float')
        if self.c.smooth:
            self.w = self.w.groupby('target_risk').rolling(window=self.c.window * 12).mean().dropna(how='all')

    def load_funds_adj_nav(self):
        """载入基金复权单位净值"""
        f = FundNav
        funds = self.c.equity + self.c.bond + self.c.alter + self.c.cash
        query = FundNav.objects.filter(
            secucode__in=funds, date__range=[self.c.start, self.c.end]
        ).values('date', 'secucode', 'adj_nav')
        df = pd.DataFrame(query)
        df.adj_nav = df.adj_nav.astype('float')
        df = pd.pivot_table(df, index=['date'], columns=['secucode'], values=['adj_nav'])['adj_nav']
        df = df.dropna(how='any')
        df.columns = [x[:6] for x in df.columns]
        self.nav = df

    def back_test(self, weight: pd.DataFrame, nav: pd.DataFrame):
        """回测核心模块-回测"""
        self.cap = self.c.init_money
        ret = []
        # 计算初始权重和持仓量
        date = nav.index[0]
        w = self.allocate_weight(weight, date)
        v = self.calc_holding_value(w, date)
        for date in nav.index:
            # 判断是否为调仓日
            month = m if (m := self.change_date.month + 1) <= 12 else 1
            if date.month != month:
                cap = self.calc_cap(v, date)
                self.cap = cap
                w = self.allocate_weight(weight, date)
                v = self.calc_holding_value(w, date)
            cap = self.calc_cap(v, date)
            self.cap = cap
            ret.append((date, cap))
        return ret

    def allocate_weight(self, weight_df: pd.DataFrame, date: datetime.date):
        """回测核心模块-按比例分配权重
        :param weight_df: 权重的数据集，dataframe格式，包含每个月底
        :param date: 指定日期 : datetime.date
        """
        # 日期重设为小于当前日期的第一个权重存在的日期
        date = [x for x in weight_df.index if x < date][-1]
        self.change_date = date
        ws = weight_df.loc[date]
        w = {}
        w.update({x: ws.equity / len(self.c.equity) for x in self.c.equity})
        w.update({x: ws.bond / len(self.c.bond) for x in self.c.bond})
        w.update({x: ws.alter / len(self.c.alter) for x in self.c.alter})
        w.update({x: ws.cash / len(self.c.cash) for x in self.c.cash})
        return w

    def calc_holding_value(self, weight: dict, date):
        """根据配置比例计算持仓数量"""
        price = self.nav.loc[date]
        value = {code: self.cap * w / price[code] if w else 0 for code, w in weight.items()}
        return value

    def calc_cap(self, value: dict, date: datetime.date):
        """计算指定日期的市值"""
        price = self.nav.loc[date]
        cap = sum(price[code] * v for code, v in value.items())
        return cap

    def back_test_normal(self, weight: pd.DataFrame, nav: pd.DataFrame):
        """不调仓"""
        ret = []
        # 计算初始权重和持仓量
        date = nav.index[-1]
        w = self.allocate_weight(weight, date)
        v = self.calc_holding_value(w, nav.index[0])
        for date in nav.index:
            cap = self.calc_cap(v, date)
            self.cap = cap
            ret.append((date, cap))
        return ret

    def run(self, target_risk):
        if not self.inited:
            print('error: before run process, you must init it.')
            return
        if self.c.smooth:
            weight = self.w.loc[target_risk, :]
        else:
            weight = self.w[self.w.target_risk == target_risk]
        if self.c.change:
            ret = self.back_test(weight, self.nav)
        else:
            ret = self.back_test_normal(weight, self.nav)
        ret = pd.DataFrame(ret, columns=['date', f'{target_risk}']).set_index('date')
        return ret
