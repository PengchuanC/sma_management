"""
brinson
~~~~~~~
组合brinson归因
@date: 2020-12-03

brinson归因按照日频生成
"""

import abc
import datetime

from sql import models
from investment.utils.holding import fund_holding_stock


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
        """
        holding = fund_holding_stock(self.p, self.d)
        holding = holding[['stockcode', 'ratio']]
        holding = holding.rename(columns={'stockcode': 'secucode', 'ratio': 'weight'})
        return holding

    @property
    def weight(self):
        return self._stock_weight()

    @property
    def change(self):
        pass


pa = PortfolioAllocate('SA5001', date=datetime.date(2020, 12, 1))
print(pa.weight)
