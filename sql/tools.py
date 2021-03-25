"""
commit
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-07
@desc:
"""

from django.db.transaction import atomic
from sql.commit.index import (
    commit_basic_info, commit_index_quote, commit_basic_info_wind, commit_index_quote_wind, commit_index_component
)
from sql.commit.funds import commit_funds, commit_fund_data, commit_fund_associate, commit_fund_asset_allocate
from sql.commit.funds_extend import *
from sql.commit.tradingday import commit_tradingdays
from sql.commit.stock import (
    commit_stock, commit_industry_sw, commit_stock_expose, commit_stock_daily_quote, commit_stock_capital_flow
)
from sql.commit import commit_style
from sql.commit import commit_brinson
from tasks.task import commit_fund_fee
from crawl.fund_limit import commit_fund_limit


def commit_index_gil():
    """指数数据-聚源"""
    with atomic():
        commit_basic_info()
        commit_index_quote()
        commit_index_component()


def commit_index_wind():
    """指数数据-万得，当前仅上海金数据使用Wind"""
    with atomic():
        commit_basic_info_wind()
        commit_index_quote_wind()


def commit_index():
    """指数数据-聚源、万得"""
    commit_basic_info()
    commit_index_quote()
    commit_basic_info_wind()
    commit_index_quote_wind()
    commit_index_component()


def commit_fund():
    """提交规模基金相关数据"""
    commit_funds()
    commit_fund_fee()
    commit_fund_limit()
    commit_fund_associate()
    commit_fund_data()
    commit_fund_asset_allocate()
    commit_holding_top_ten()
    commit_holding_stock_detail()
    commit_announcement()
    commit_fund_advisor()
    commit_asset_allocate_hk()
    commit_fund_holding_stock_hk()


def commit_trading_day():
    with atomic():
        commit_tradingdays()


def commit_stocks():
    commit_stock()
    commit_stock_daily_quote()
    commit_industry_sw()
    commit_stock_expose()
    commit_stock_capital_flow()


def commit_preprocess():
    """提交预处理的数据
    主要指组合风格分析及brinson归因等
    """
    commit_style()
    commit_brinson()


__all__ = (
    'commit_index', 'commit_index_gil', 'commit_index_wind', 'commit_fund', 'commit_trading_day', 'commit_stocks',
    'commit_preprocess'
)
