from tasks.prev_valuation import pre_valuation
from tasks.asset_allocate import portfolio_asset_allocate
from tasks import fund_position
from shu.from_sma import commit_sma
from sql import tools
from crawl.stock_async import executor
from crawl.fund_fee_howbuy import commit_fund_fee_hb
from crawl.fund_fee import commit_fund_fee_em
from sql.commit.funds_extend import commit_fund_quote
from services.client import Client
from services.backtest_client import Client as BacktestClient
from sma_management.settings import RpcProxyHost


def save_prev_valuation_nav():
    """保存组合预估净值到数据库"""
    tools.commit_stock_daily_quote()
    commit_fund_quote()
    pre_valuation()


def commit_all_db_task():
    """同步组合净值"""
    with Client(RpcProxyHost) as client:
        try:
            client.commit_all()
        except Exception as e:
            print(e)


def commit_all_db_task_hook(task):
    commit_sma()
    tools.commit_return_yield()


def crawl_stock_price():
    """异步爬取股票实时价格"""
    executor()


def commit_capital():
    """同步行业资金流向数据"""
    tools.commit_basic_info()
    tools.commit_index_gil()
    tools.commit_stock_capital_flow()
    tools.commit_capital_flow()


def commit_portfolio_allocate():
    """每日计算组合各类资产持仓占比"""
    portfolio_asset_allocate()


def commit_fund_pos():
    """基金仓位估算"""
    fund_position.commit()


def commit_fund_fee():
    commit_fund_fee_hb()
    commit_fund_fee_em()


def commit_weighted_average_return():
    """更新组合单只基金加权收益"""
    tools.commit_return_yield()


def commit_backtest():
    """同步SMA标准组合回测数据"""
    with BacktestClient(*RpcProxyHost.split(':')) as client:
        client.sync_data()


if __name__ == '__main__':
    # commit_portfolio_allocate()
    # commit_fund_pos()
    # pre_valuation()
    tools.commit_return_yield()
    # save_prev_valuation_nav()
    # commit_sma()
