"""
从天天基金网爬取基金申购限额数据
"""

import json
import requests as r
import pandas as pd

from datetime import date

from crawl import models


base = 'http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?t=8&page=<page/>,1000&js=reData&sort=maxsg,asc'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63'
}


session = r.session()


def get_info():
    req = session.get(base.replace('<page/>', '1'), headers=headers)
    content = req.content.decode('utf-8')
    content = content[11:]
    for attr in ['datas', 'record', 'pages', 'curpage', 'showday']:
        content = content.replace(attr, f'"{attr}"')
    content = json.loads(content)
    return int(content['pages'])


def get_limit(page: str):
    req = session.get(base.replace('<page/>', page), headers=headers)
    content = req.content.decode('utf-8')
    content = content[11:]
    for attr in ['datas', 'record', 'pages', 'curpage', 'showday']:
        content = content.replace(attr, f'"{attr}"')
    content = json.loads(content)
    df = pd.DataFrame(content['datas'])
    df = df.iloc[:, [0, 5, 6, 8, 9]]
    df.columns = ['secucode', 'apply_type', 'redeem_type', 'min_apply', 'max_apply']
    df['date'] = date.today()
    return df.to_dict(orient='records')


def commit_fund_limit():
    pages = get_info() + 1
    for p in range(1, pages):
        p = str(p)
        try:
            data = get_limit(p)
            for row in data:
                fund = models.Funds.objects.get(secucode=row.pop('secucode'))
                if fund:
                    models.FundPurchaseAndRedeem.objects.update_or_create(
                        secucode=fund, date=row.pop('date'), defaults=row
                    )
        except Exception as e:
            print(e)


if __name__ == '__main__':
    commit_fund_limit()
