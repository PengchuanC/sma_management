from tasks.prev_valuation import pre_valuation
from command import shu_commit
from crawl.stock_async import executor


def save_prev_valuation_nav():
    """保存组合预估净值到数据库"""
    pre_valuation()


def commit_all_db_task():
    """执行所有同步任务"""
    shu_commit()


def crawl_stock_price():
    """异步爬取股票实时价格"""
    executor()
