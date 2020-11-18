"""
dataset
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""

import re
import datetime

from typing import List
from numpy import nan
from pathlib import Path
from dateutil.parser import parse
from shu.sma_export.connector import sql_executor
from shu.sma_export.parse_configs import configs


TABLES = {y: x for x, y in configs['targets'].items()}
PATTERN = re.compile(r'\d{8}')


def last_trading_day() -> datetime.date:
    """最新交易日"""
    # sql = 'select max(date) as date from sma_balance'
    # data = sql_executor(sql)
    # date = data.date[0]
    # return date

    # 2020年11月6日修改逻辑：最新交易日应该从文件夹中读取
    dirs = configs['target_path']
    dirs = Path(dirs) / '组合资产负债表'
    files = dirs.glob('*.xlsx')
    dates = [parse(PATTERN.search(x.name).group()).date() for x in files] + [datetime.date(2020, 1, 1)]
    return max(dates)


def whole_trading_days(table) -> List[datetime.date]:
    """全部交易日"""
    sql = f'select distinct(date) as date from {table} order by date'
    data = sql_executor(sql)
    date = list(data.date)
    return date


def export(table: str, date: datetime.date=None):
    """从mysql database 读取数据"""
    if date:
        date = date.strftime('%Y-%m-%d')
        sql = f'select * from {table} where date = "{date}"'
    else:
        sql = f'select * from {table}'
    data = sql_executor(sql)
    if date:
        data = data.drop('id', axis=1)
    data = data.replace(nan, None)
    return data
