"""
commit
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-07
@desc:
"""

from django.db.transaction import atomic
from sql.commit.index import commit_basic_info, commit_index_quote, commit_basic_info_wind, commit_index_quote_wind
from sql.commit.funds import commit_funds, commit_fund_data
from sql.commit.tradingday import commit_tradingdays
from sql.commit.stock import commit_stock, commit_industry_sw


__all__ = (
    'commit_index', 'commit_index_gil', 'commit_index_wind', 'commit_fund', 'commit_trading_day', 'commit_stocks'
)


def commit_index_gil():
    """指数数据-聚源"""
    with atomic():
        commit_basic_info()
        commit_index_quote()


def commit_index_wind():
    """指数数据-万得"""
    with atomic():
        commit_basic_info_wind()
        commit_index_quote_wind()


def commit_index():
    """指数数据-聚源、万得"""
    commit_basic_info()
    commit_index_quote()
    commit_basic_info_wind()
    commit_index_quote_wind()


def commit_fund():
    commit_funds()
    commit_fund_data()


def commit_trading_day():
    with atomic():
        commit_tradingdays()


def commit_stocks():
    commit_stock()
    commit_industry_sw()
