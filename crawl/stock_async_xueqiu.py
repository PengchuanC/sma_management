"""
@author: chuanchao.peng
@date: 2022/1/21 13:06
@file stock_async_xueqiu.py
@desc:
"""
import asyncio
import datetime
import time
from copy import deepcopy

import aiohttp

from crawl.stock_async import insert, Price, executor, clear


BASE_URL = "https://xueqiu.com/service/v5/stock/screener/quote/list"

PAYLOAD = {
    "page": 1,
    "size": 1000,
    "order": "desc",
    "orderby": "percent",
    "order_by": "percent",
    "market": "CN",
    "type": "sh_sz",
    "_": 0
}


def update_query_params(page: int = 1, size: int = 1000, market: str = 'CN'):
    payload = deepcopy(PAYLOAD)
    if market == 'CN':
        tp = 'sh_sz'
    else:
        tp = 'hk'
    # 获取毫秒级时间戳
    timestamp = int(time.time() * 1000)
    payload.update({
        'page': page, 'size': size, 'market': market, 'type': tp, '_': timestamp
    })
    return payload


def get_session():
    headers = {
        'Host': 'xueqiu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62'
    }
    session = aiohttp.ClientSession(headers=headers)
    return session


async def fetch_stock_quote(payload: dict):
    """爬虫"""
    session = get_session()
    async with session.get(BASE_URL, params=payload) as resp:
        status_code = resp.status
        if status_code != 200:
            return []
        content = await resp.json()
    await session.close()
    return content['data']['list']


async def fetch_stock_quote_loop(payload: dict):
    """爬取多页"""
    while True:
        content = await fetch_stock_quote(payload)
        if not content:
            break
        yield content
        payload["page"] += 1


async def fetch(params: dict):
    params = update_query_params(**params)
    date = datetime.datetime.now()
    dt = date.strftime('%Y-%m-%d')
    tm = date.strftime('%H:%M:%S')
    async for stocks in fetch_stock_quote_loop(params):
        ret = []
        for stock in stocks:
            price = stock['current']
            # 新上市基金昨收视为现价
            prev = round(price - stock['chg'] if stock['chg'] else price, 2)
            m = {'secucode': stock['symbol'][-6:], 'date': dt, 'time': tm, 'price': price, 'prev_close': prev}
            ret.append(m)
        await insert(ret)


async def commit():
    await fetch({'size': 1000, 'market': 'CN'})
    await fetch({'size': 1000, 'market': 'HK'})


if __name__ == '__main__':
    executor(commit, clear)

