from tasks.prev_valuation import pre_valuation
from command import run_all


def save_prev_valuation_nav():
    """保存组合预估净值到数据库"""
    pre_valuation()


def commit_all_db_task():
    """执行所有同步任务"""
    run_all()
