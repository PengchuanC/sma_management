"""
处理宜信流水
"""

import datetime
import pandas as pd

from itertools import groupby
from dateutil.parser import parse
from shu.configs import local_files_path
from shu import models


__all__ = ('commit_transaction', )


columns_mapping = {
    '基金代码': 'secucode', '业务名称': 'operation', '申请时间': 'apply', '确认时间': 'confirm', '确认金额': 'amount',
    '确认份额': 'shares', '手续费': 'fee'
}


def read_transaction_yx(file_path: str):
    """读取excel文件"""
    data = pd.read_excel(file_path, engine='openpyxl', converters={'基金代码': str})
    data = data[columns_mapping.keys()]
    data = data.rename(columns=columns_mapping)
    data.secucode = data.secucode.str.zfill(6)
    data = data.sort_values(['secucode', 'apply'])
    yield data


def transaction_files_yx():
    """宜信普泽交易流水
    流水文件命名方式为 {port_code}_{trading_date | yyyymmdd}.xlsx
    {
        'PFF003': [
        ['PFF003', datetime.date(2021, 3, 5),
        WindowsPath('p:/code/sma/data/management/transaction/yixin/PFF003_20210305.xlsx')]
        ]
    }
    """
    yx_files_path = local_files_path / 'transaction' / 'yixin'
    yx_files = yx_files_path.glob('*.xlsx')
    yx_files = sorted(yx_files)

    files = []
    for x in yx_files:
        stem = x.stem
        name, date = stem.split('_')
        date = parse(date).date()
        abs_path = x.absolute()
        files.append([name, date, abs_path])

    files = groupby(files, key=lambda f: f[0])
    files = {x[0]: list(x[1]) for x in files}
    return files


def commit_transaction():
    portfolio = models.Portfolio.objects.filter(settlemented=0)
    for port_code in portfolio:
        _commit_transaction(port_code)


def _commit_transaction(port_code: models.Portfolio):
    """同步交易流水"""
    latest = models.TransactionsYX.objects.filter(port_code=port_code)
    if not latest.exists():
        latest = datetime.date(2021, 1, 1)
    else:
        latest = latest.latest('confirm').confirm
    dataset = transaction_files_yx()
    dataset = dataset.get(port_code.port_code)
    if dataset is None:
        return

    m = []
    for _, date, path in dataset:
        # 历史流水，无需导入
        # if date <= latest:
        #     continue
        data = read_transaction_yx(path)
        data = next(data)
        data['port_code'] = port_code
        data = data.sort_values(by='confirm')
        data.confirm = data.confirm.apply(lambda x: parse(str(x)).date())
        # 二次验证历史流水，无需导入
        data = data[data.confirm > latest]
        m.extend([models.TransactionsYX(**x) for _, x in data.iterrows()])

    models.TransactionsYX.objects.bulk_create(m)


def commit_holding():
    """根据宜信的交易流水计算宜信持仓份额"""
    portfolio = models.TransactionsYX.objects.values('port_code').distinct()
    portfolio = {models.Portfolio.objects.get(port_code=x['port_code']) for x in portfolio}
    for port_code in portfolio:
        _commit_holding(port_code)


def _commit_holding(port_code: models.Portfolio):
    latest = models.HoldingYX.objects.filter(port_code=port_code)
    if not latest.exists():
        latest = datetime.date(2021, 1, 1)
    else:
        latest = latest.latest().date

    full_dates = models.Balance.objects.filter(port_code=port_code.port_code, date__gt=latest).values('date').distinct()
    full_dates = sorted([x['date'] for x in full_dates])

    transactions = models.TransactionsYX.objects.filter(
        port_code=port_code, confirm__gt=latest).order_by('confirm', 'secucode')
    transactions = [x for x in transactions]
    transactions = groupby(transactions, key=lambda x: x.confirm)
    transactions = {x[0]: {y.secucode: y for y in x[1]} for x in transactions}

    # 逐日计算持仓
    for date in full_dates:
        m = []
        # 获取当前日期前一交易日持仓
        last = models.HoldingYX.objects.filter(port_code=port_code, date__lte=date)
        # 前一交易日持仓不存在(一般为首日)
        if not last.exists():
            holding = {}
        else:
            last = last.latest().date
            holding = models.HoldingYX.objects.filter(port_code=port_code, date=last)
            holding = {x.secucode: x.shares for x in holding}

        # 获取当日流水
        dataset = transactions.get(date, None)
        # 当日不存在任何流水记录
        if not dataset:
            for r, shares in holding.items():
                m.append(models.HoldingYX(port_code=port_code, shares=shares, date=date, secucode=r))
            models.HoldingYX.objects.bulk_create(m)
            continue

        funds = set([x for x in holding] + [x for x in dataset])
        for fund in funds:
            old = holding.get(fund, 0)
            t = dataset.get(fund, None)
            # 无新流水
            if not t:
                m.append(models.HoldingYX(port_code=port_code, shares=old, date=date, secucode=fund))
                continue

            changes = 0
            if t.operation == '申购确认':
                old += t.shares
                changes = t.shares

            elif t.operation == '赎回确认':
                old -= t.shares
                changes = -t.shares

            m.append(models.HoldingYX(port_code=port_code, shares=old, date=date, secucode=fund, shares_change=changes))

        models.HoldingYX.objects.bulk_create(m)


if __name__ == '__main__':
    commit_transaction()
    commit_holding()
