"""
command
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-07
@desc:
"""
import click

from sql import tools
from shu.run import shu_commit
from crawl import fund_limit, fund_fee


@click.group()
def root():
    pass


@root.group()
def index():
    pass


@root.command()
def fund():
    tools.commit_fund()


@root.command()
def stock():
    tools.commit_stocks()


@root.command()
def tradingday():
    tools.commit_trading_day()


@index.command()
def gil():
    tools.commit_index_gil()


@index.command()
def wind():
    tools.commit_index_wind()


@index.command()
def run_index():
    tools.commit_index()


@root.command()
def shu():
    shu_commit()


@root.command()
def run_all():
    """存在依赖顺序，shu必须先commit"""
    shu_commit()
    tools.commit_stocks()
    tools.commit_fund()
    tools.commit_index_gil()
    tools.commit_tradingdays()
    tools.commit_preprocess()
    fund_limit.commit_fund_limit()
    fund_fee.commit_fund_fee()


if __name__ == '__main__':
    root()
