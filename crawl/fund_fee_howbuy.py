import re
import asyncio
import time

import aiohttp
import pandas as pd

from itertools import chain
from typing import List
from lxml.etree import ParserError

from crawl.stock_async import database, metadata, sa, Holding

# 爬虫地址
Basic = 'https://www.howbuy.com/fund/ajax/gmfund/fundrate.htm'

# 爬虫暂停时间
CRAWL_STOP_TIME = 10

# 正则模板
purchase = re.compile(r'\d+')
ransom = re.compile(r'\d+')

FundFee = sa.Table(
    'sma_fund_purchase_fee',
    metadata,
    sa.Column('secucode_id', sa.String(12)),
    sa.Column('operate', sa.String(4)),
    sa.Column('low', sa.INT),
    sa.Column('high', sa.INT),
    sa.Column('fee', sa.DECIMAL(18, 4))
)


async def request(fund: str):
    """获取基金数据表格"""
    url = Basic
    async with aiohttp.request('GET', url, params={'jjdm': fund}) as r:
        content = await r.text()
    content = pd.read_html(content)
    return content


def format_purchase_info(data: List[pd.DataFrame]):
    """整理申购数据"""
    header = data[3]
    header = list(header.iloc[0])
    fee = data[4]
    fee.columns = header
    fee = fee.iloc[:, 1:].T
    for period, r in fee.iterrows():
        low, high, fee = _format_period(purchase, period, r[1])
        yield low, high, fee, 'buy'


def format_ransom_info(data: List[pd.DataFrame]):
    """整理赎回数据"""
    fee = data[7].set_index(0).T
    for _, r in fee.iterrows():
        low, high, fee = _format_period(purchase, r[0], r[1])
        yield low, high, fee, 'sell'


def _format_period(compiler, word, fee):
    ratio = float(fee[:-1]) / 100
    if word == '不限':
        return 0, None, ratio
    period = re.findall(compiler, word)
    if len(period) == 1:
        low = int(period[0])
        high = None
    else:
        low, high = period
        low, high = int(low), int(high)
    return low, high, ratio


async def holding_funds():
    """当前持有的基金"""
    query = sa.select([Holding.columns.secucode]).where(
        Holding.columns.date == sa.select([sa.func.max(Holding.columns.date)])
    )
    funds = await database.fetch_all(query)
    funds = {x[0] for x in funds}
    return funds


async def fund_fee(fund: str):
    """获取基金费用信息的model"""
    data = await request(fund)
    p = format_purchase_info(data)
    r = format_ransom_info(data)
    ret = []
    for low, high, fee, op in chain(p, r):
        ret.append({'secucode_id': fund, 'operate': op, 'low': low, 'high': high, 'fee': fee})
    return ret


async def run():
    await database.connect()

    funds = await holding_funds()
    ret = []
    for fund in funds:
        try:
            r = await fund_fee(fund)
            ret.append(r)
        except ParserError:
            pass

    ret = list(chain.from_iterable(ret))
    delete = FundFee.delete()
    await database.execute(delete)
    sql = FundFee.insert()
    await database.execute_many(sql, values=ret)
    await database.disconnect()


def test():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fund_fee('010696'))


def commit_fund_fee():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


if __name__ == '__main__':
    commit_fund_fee()
