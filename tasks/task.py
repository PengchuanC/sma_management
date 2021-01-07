from tasks.prev_valuation import pre_valuation
from command import shu_commit, fund_limit, tools, fund_fee


def save_prev_valuation_nav():
    """保存组合预估净值到数据库"""
    pre_valuation()


def commit_all_db_task():
    """执行所有同步任务"""
    shu_commit()
    tools.commit_stocks()
    tools.commit_fund()
    tools.commit_index_gil()
    tools.commit_tradingdays()
    tools.commit_preprocess()
    fund_limit.commit_fund_limit()
    fund_fee.commit_fund_fee()
