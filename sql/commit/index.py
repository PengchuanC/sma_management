"""
index
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-04
@desc: 同步指数数据
"""

from datetime import timedelta
from WindPy import w

from sql import models
from sql.commit.wind_wrapper import use_wind
from sql.sql_templates import index as template
from sql.utils import read_oracle, render


def get_indexes():
    """获取本地中的指数列表"""
    indexes = models.Index.objects.values_list('secucode')
    indexes = [x[0] for x in indexes]
    return indexes


def get_index_basic_info():
    """获取指数基本信息，增量方式"""
    basic = models.IndexBasicInfo.objects.values_list('secucode')
    basic = [x[0] for x in basic]
    indexes = get_indexes()
    indexes = [x for x in indexes if '.' not in x]
    added = [x for x in indexes if x not in basic]
    added = "'" + "','".join(added) + "'"
    sql = render(template.basic_info, '<codelist>', added)
    data = read_oracle(sql)
    data = data.to_dict(orient='records')
    return data


def commit_basic_info():
    data = get_index_basic_info()
    _commit_basic_info(data)


def _commit_basic_info(data: dict):
    m = []
    for i in data:
        secucode = models.Index.objects.get(secucode=i['secucode'])
        i.update({'secucode': secucode})
        model = models.IndexBasicInfo(**i)
        m.append(model)
    models.IndexBasicInfo.objects.bulk_create(m)


def get_index_quote(secucode):
    """获取指数交易数据"""
    last = models.IndexQuote.objects.filter(secucode=secucode).last()
    if last:
        date = last.date
    else:
        date = models.IndexBasicInfo.objects.get(secucode=secucode).basedate.date()
    for tmpl in [template.quote, template.quote_cb, template.quote_os]:
        sql = render(tmpl, '<code>', secucode)
        sql = render(sql, '<date>', date.strftime('%Y-%m-%d'))
        data = read_oracle(sql)
        if not data.empty:
            data.columns = [x.lower() for x in data.columns]
            return data.to_dict(orient='records')


def commit_index_quote():
    """提交指数的行情数据"""
    indexes = get_indexes()
    indexes = [x for x in indexes if '.' not in x]
    _commit_index_quote(indexes, get_index_quote)


def _commit_index_quote(codelist: list, func: callable):
    for index in codelist:
        data = func(index)
        if not data:
            continue
        m = []
        secucode = models.Index.objects.get(secucode=data[0]['secucode'])
        for i in data:
            i.update({'secucode': secucode})
            m.append(models.IndexQuote(**i))
        models.IndexQuote.objects.bulk_create(m)


@use_wind
def get_index_basic_info_wind():
    """获取指数数据-wind"""
    basic = models.IndexBasicInfo.objects.values_list('secucode')
    basic = [x[0] for x in basic]
    indexes = get_indexes()
    indexes = [x for x in indexes if '.' in x and x not in basic]
    err, data = w.wss(indexes, "sec_name,basedate,sec_type", usedf=True)
    if data.empty or err != 0:
        return []
    data['secucode'] = data.index
    data['secuabbr'] = data['SEC_NAME']
    data['chiname'] = data['secuabbr']
    data['category'] = data['SEC_TYPE']
    data['component'] = data['category']
    data['basedate'] = data['BASEDATE']
    data['source'] = 2
    data = data[['secucode', 'secuabbr', 'chiname', 'category', 'component', 'source', 'basedate']]
    data = data.to_dict(orient='records')
    return data


def commit_basic_info_wind():
    data = get_index_basic_info_wind()
    _commit_basic_info(data)


@use_wind
def get_index_quote_wind(secucode):
    """获取指数收盘价-wind"""
    last = models.IndexQuote.objects.filter(secucode=secucode).last()
    if last:
        date = last.date
        date = date + timedelta(days=1)
    else:
        date = models.IndexBasicInfo.objects.get(secucode=secucode).basedate.date()
    date = date.strftime('%Y-%m-%d')
    err, data = w.wsd(secucode, "pre_close,close,pct_chg", date, "", "", usedf=True)
    if err != 0 or data.empty or len(data) == 1:
        return []
    data = data.rename(columns={'PRE_CLOSE': 'pre_close', 'CLOSE': 'close', 'PCT_CHG': 'change'})
    data = data.dropna(how='all')
    data['date'] = data.index
    data['secucode'] = secucode
    data = data.to_dict(orient='records')
    return data


def commit_index_quote_wind():
    """提交指数的行情数据-wind"""
    indexes = get_indexes()
    indexes = [x for x in indexes if '.' in x]
    _commit_index_quote(indexes, get_index_quote_wind)


__all__ = ['commit_basic_info', 'commit_basic_info_wind', 'commit_index_quote', 'commit_index_quote_wind']
