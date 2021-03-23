from tasks.prev_valuation import pre_valuation
from tasks.asset_allocate import portfolio_asset_allocate
from tasks import fund_position
from command import shu_commit
from sql import tools
from crawl.stock_async import executor
from crawl.fund_fee_howbuy import commit_fund_fee


def save_prev_valuation_nav():
    """保存组合预估净值到数据库"""
    tools.commit_stock_daily_quote()
    pre_valuation()


def commit_all_db_task():
    """同步组合净值"""
    shu_commit()


def crawl_stock_price():
    """异步爬取股票实时价格"""
    executor()


def commit_capital():
    """同步行业资金流向数据"""
    tools.commit_basic_info()
    tools.commit_index_gil()
    tools.commit_stock_capital_flow()


def commit_portfolio_allocate():
    portfolio_asset_allocate()


def commit_fund_pos():
    """基金仓位估算"""
    fund_position.commit()


if __name__ == '__main__':
    commit_fund_pos()
