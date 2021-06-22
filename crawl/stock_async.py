import re
import asyncio
import datetime
import time
from math import ceil
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import aiohttp
import databases
import sqlalchemy as sa

from itertools import groupby
from typing import List
from dateutil.parser import parse
from sma_management.settings import DATABASES

# 爬虫暂停时间
CRAWL_STOP_TIME = 10

# 保证是同一时间获取的数据
TIME = datetime.datetime.now().time()

# 数据库默认配置
default = DATABASES['default']
URI = f"mysql://{default['USER']}:{default['PASSWORD']}@{default['HOST']}:{default['PORT']}/{default['NAME']}" \
      f"?charset=utf8mb4"
metadata = sa.MetaData()

# 任务调度器
scheduler = AsyncIOScheduler()

# 数据来源
basicUrl = "http://hq.sinajs.cn/"

# 数据库
database = databases.Database(URI)

# 证券代码模板
code_pattern = re.compile(r'\d{5,6}')
date_pattern = re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}')

# 表单
Holding = sa.Table(
    'sma_holding_fund',
    metadata,
    sa.Column('secucode', sa.String(12)),
    sa.Column('date', sa.DATE()),
    sa.Column('category', sa.String(50)),
    sa.Column('trade_market', sa.INTEGER)
)

Stock = sa.Table(
    'sma_fund_holding_stock',
    metadata,
    sa.Column('secucode_id', sa.String(12)),
    sa.Column('stockcode', sa.String(12)),
    sa.Column('date', sa.DATE())
)

Price = sa.Table(
    'sma_stocks_realtime_price',
    metadata,
    sa.Column('secucode_id', sa.String(12)),
    sa.Column('price', sa.DECIMAL(10, 2)),
    sa.Column('prev_close', sa.DECIMAL(10, 2)),
    sa.Column('date', sa.DATE()),
    sa.Column('time', sa.TIME())
)

Observe = sa.Table(
    'sma_observe_pool',
    metadata,
    sa.Column('secucode_id', sa.String(12))
)


async def etf_in_portfolio() -> list:
    """获取持仓中的etf"""
    await database.connect()
    query = sa.select([Holding.c.secucode]).where(
        Holding.columns.date == sa.select([sa.func.max(Holding.columns.date)]),
        Holding.c.trade_market.in_([1, 2])
    )
    funds = await database.fetch_all(query)
    funds = {x[0] for x in funds}
    return list(funds)


async def stocks_in_portfolio() -> list:
    """获取基金组合中的全部股票和etf

    Returns:
        股票列表

    """
    await database.connect()
    query = sa.select([Holding.columns.secucode]).where(
        Holding.columns.date == sa.select([sa.func.max(Holding.columns.date)])
    )
    funds = await database.fetch_all(query)
    funds = [x[0] for x in funds]

    query = sa.select([Observe.columns.secucode_id])
    observe = await database.fetch_all(query)
    funds = funds + [x[0] for x in observe]
    funds = list(set(funds))
    query = sa.select([Stock]).where(
        Stock.columns.secucode_id.in_(funds)
    )
    ret = await database.fetch_all(query)
    ret = sorted(ret, key=lambda x: (x[0]))
    group = groupby(ret, key=lambda x: x[0])
    stocks = []
    for _, val in group:
        val = list(val)
        date = max(x[2] for x in val)
        stocks.extend([x[1] for x in val if x[2] == date])
    stocks = list(set(stocks))
    etf = await etf_in_portfolio()
    stocks += etf
    await database.disconnect()
    return stocks


def format_stock(code: str):
    """格式化股票代码

    Args:
        code: 证券代码，不包含前后缀

    Returns:
        包含前缀的股票代码

    """
    if len(code) == 6:
        return 'sh' + code if code.startswith('6') else 'sz' + code
    return 'hk' + code


async def request(params: str) -> str:
    """爬取股票实时行情

    Args:
        params: 股票代码序列，逗号拼接

    Returns:
        行情

    """
    async with aiohttp.request('GET', basicUrl, params={'list': params}) as r:
        content = await r.text()
    return content


def format_response(response: str):
    """格式化爬取的结果

    Args:
        response: 响应内容

    Returns:

    """
    items = response.split(';')
    for row in items:
        if len(row) < 20:
            continue
        row: str = row.strip('\n').strip('"').strip(',')
        item: List = row.split(',')
        code = re.search(code_pattern, item[0]).group()
        date = re.search(date_pattern, row).group()
        date = parse(date).date()
        if len(item) >= 33:
            price = float(item[3])
            prev = float(item[2])
        else:
            price = float(item[6])
            prev = float(item[3])
        yield {'secucode_id': code, 'date': date, 'time': TIME, 'price': price, 'prev_close': prev}


async def insert(values: List[dict]):
    """写入数据

    Args:
        values:

    Returns:

    """
    sql = Price.insert()
    async with database as db:
        await db.execute_many(sql, values)


def chunk(array, size=1):
    chunks = int(ceil(len(array) / float(size)))
    return [array[i * size:(i + 1) * size] for i in range(chunks)]


async def commit(stocks: List[str]):
    """爬取数据并保存"""
    stocks: List[str] = [format_stock(x) for x in stocks]
    stocks: str = ','.join(stocks)
    resp: str = await request(stocks)
    ret = format_response(resp)
    ret = list(ret)
    await insert(ret)


async def main():
    stocks: List[str] = await stocks_in_portfolio()
    stocks_chunk = chunk(stocks, 20)
    global TIME
    TIME = datetime.datetime.now().time().strftime('%H:%M:%S')
    for sc in stocks_chunk:
        await commit(sc)


async def clear():
    """清除历史交易日数据"""
    sql = 'truncate table sma_stocks_realtime_price;'
    async with database as db:
        await db.execute(sql)


def schedule():
    scheduler.add_job(main, 'cron', day_of_week='0-4', hour='9', minute='30-59', second='*/10')
    scheduler.add_job(main, 'cron', day_of_week='0-4', hour='10,13,14', second='*/10')
    scheduler.add_job(main, 'cron', day_of_week='0-4', hour='11', minute='0-29', second='*/10')
    scheduler.add_job(main, 'cron', day_of_week='0-4', hour='15', minute='0', second='10')
    scheduler.add_job(clear, 'cron', day_of_week='0-4', hour='9', minute='0', second='0')
    scheduler.start()


def executor():
    schedule()
    pool = asyncio.get_event_loop()
    pool.run_forever()


if __name__ == '__main__':
    executor()
