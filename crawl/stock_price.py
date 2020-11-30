"""
stock_price
~~~~~~~~~~~
从新浪爬取当日股票实时价格
1. 15点过后不在爬取
2. 为了节省空间，首次执行爬虫时会删除前日数据
"""

import datetime
import math
import time

import requests as r

from typing import List
from dateutil.parser import parse
from crawl import models


# 爬虫暂停时间
CRAWL_STOP_TIME = 10

# 保证是同一时间获取的数据
TIME = datetime.datetime.now().time()


basicUrl = "http://hq.sinajs.cn/list="


def get_stock_price(stocks: list):
    """爬取数据"""
    stocks_str: str = stock_code_formatter(stocks)
    url = basicUrl + stocks_str
    resp = r.get(url)
    resp.close()
    data_str = resp.content.decode('gbk')
    return data_str


def stock_code_formatter(stocks: List[str]) -> str:
    """股票代码处理"""
    stocks: List = [x for x in stocks if len(x) == 6]
    stocks = ['sh' + x if x.startswith('6') else 'sz' + x for x in stocks]
    stocks: str = ','.join(stocks)
    return stocks


def parse_str_2_model(ret_str: str, stocks: list):
    """解析爬虫返回的字符串， 需求原始的stocks列表"""
    global TIME
    stocks = models.Stock.objects.filter(secucode__in=stocks).all()
    stocks = {x.secucode: x for x in stocks}
    data = ret_str.split(';')
    data = [x.strip() for x in data if len(x) > 50]
    ret = []
    for d in data:
        code: str = d[13: 19]
        d: str = d[21: -1].strip(',')
        d: list = d.split(',')
        prev_close = float(d[2])
        price: float = float(d[3])
        if len(d) == 33:
            date: datetime.date = parse(d[-3]).date()
        else:
            date: datetime.date = parse(d[-4]).date()
        if (sc := stocks.get(code)) is not None:
            ret.append(models.StockRealtimePrice(secucode=sc, prev_close=prev_close, price=price, date=date, time=TIME))
    models.StockRealtimePrice.objects.bulk_create(ret)


def commit_stock_price(stocks: list):
    global TIME
    TIME = datetime.datetime.now().time()
    if len(stocks) <= 200:
        data_str = get_stock_price(stocks)
        parse_str_2_model(data_str, stocks)
        return
    length = math.floor(len(stocks) / 200) + 1
    for i in range(length):
        s = stocks[i*200: (i+1)*200]
        data_str = get_stock_price(s)
        parse_str_2_model(data_str, s)


class CrawlStockPrice(object):

    def __init__(self):
        self.stocks = self.get_stocks()
        self.time = datetime.time(15, 0, 10)
        self.clear_history()

    @staticmethod
    def get_stocks():
        """获取全部持仓基金中包含的股票"""
        date = models.Holding.objects.last().date
        funds = models.Holding.objects.filter(date=date).values('secucode').distinct()
        funds = [x['secucode'] for x in funds]
        date = models.FundHoldingStock.objects.last().date
        stocks = models.FundHoldingStock.objects.filter(secucode__in=funds, date=date).values('stockcode').distinct()
        stocks = list({x['stockcode'] for x in stocks})
        return stocks

    @staticmethod
    def clear_history():
        to_delete = models.StockRealtimePrice.objects.filter(date__lt=datetime.date.today()).all()
        t: models.StockRealtimePrice
        for t in to_delete:
            t.delete()

    def run(self):
        now = datetime.datetime.now().time()
        while True:
            if (datetime.time(9, 30, 0) < now < datetime.time(11, 30, 0)) \
                    or (datetime.time(13, 0, 0) < now < datetime.time(15, 0, 10)):
                commit_stock_price(self.stocks)
                time.sleep(CRAWL_STOP_TIME)
            else:
                time.sleep(60)
        # commit_stock_price(self.stocks)


if __name__ == '__main__':
    c = CrawlStockPrice()
    c.run()
