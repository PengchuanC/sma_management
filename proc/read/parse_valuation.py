"""
parsing_valuation
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-06-28
@desc: 解析估值表
"""
from typing import Dict

import pandas as pd
from dateutil.parser import parse


def rstrip(text: str):
    """
    去除右侧的中英文冒号
    :return:
    """
    text = text.rstrip(":")
    text = text.rstrip("：")
    return text


def locate(data, row_label, col_label="市值"):
    """
    从DataFrame中获取指定数据
    :param data: 数据源 : pd.DataFrame
    :param row_label: 行标签 : str
    :param col_label: 列标签 : str
    :return: 指定数据
    """
    try:
        ret = data.loc[row_label, col_label]
    except KeyError:
        ret = 0
    except Exception as e:
        print(f"估值表数据解析错误，行列标签为“{row_label}”、”{col_label}“，" + str(e))
        raise e
    ret = round(float(ret), 4)
    return ret


def analyze(data):
    """
    解析估值表，获取需要的数据
    :param data: pd.DataFrame
    :return:
    """
    data = data[data['科目代码'].notnull()].copy()
    data['市值'] = data['市值'].fillna(method='bfill')
    data = data.fillna(0)
    data['科目代码'] = data['科目代码'].apply(rstrip)
    data = data.set_index('科目代码')
    asset = locate(data, '资产类合计')
    debt = locate(data, '负债类合计')
    net_asset = locate(data, '基金资产净值')
    shares = locate(data, '实收资本', '数量')
    unit_nav = locate(data, '基金单位净值', '市值')
    acc_nav = locate(data, '累计单位净值', '市值')
    savings = locate(data, '1002', '市值')  # 银行存款
    fund_invest = locate(data, '1105', '市值')  # 基金投资
    dividend_rec = locate(data, '1203')  # 应收股利
    interest_rec = locate(data, '1204')  # 应收利息
    purchase_rec = locate(data, '1207')  # 应收申购款
    redemption_pay = locate(data, '2203')  # 应付赎回款
    redemption_fee_pay = locate(data, '2204')  # 应付赎回费
    management_pay = locate(data, '2206')  # 应付管理人报酬
    custodian_pay = locate(data, '2207')  # 应付托管费
    profit_pay = locate(data, '223201')  # 应付利润，即分红
    withholding_pay = locate(data, '2501')  # 预提费用
    liquidation = locate(data, '3003')  # 证券清算款
    value_added = locate(data, '基金资产净值', '估值增值')  # 估值增值
    cash_dividend = locate(data, '累计派现金额', '科目名称')
    ret = {
        'asset': asset, 'debt': debt, 'net_asset': net_asset, 'shares': shares, 'unit_nav': unit_nav,
        'acc_nav': acc_nav, 'savings': savings, 'fund_invest': fund_invest, 'dividend_rec': dividend_rec,
        'interest_rec': interest_rec, 'purchase_rec': purchase_rec, 'redemption_pay': redemption_pay,
        'management_pay': management_pay, 'custodian_pay': custodian_pay, 'withholding_pay': withholding_pay,
        'liquidation': liquidation, 'value_added': value_added, 'redemption_fee_pay': redemption_fee_pay,
        'profit_pay': profit_pay, 'cash_dividend': cash_dividend
    }
    return ret


def locate_new(data, row, col='EN_SZ'):
    if row == '累计单位净值':
        v = data[data['VC_KMDM'].apply(lambda x: row in x)]
    else:
        v = data[data['VC_KMDM'] == row]
    v = v[[col, 'L_ZTBH', 'D_YWRQ']]
    v.columns = ['value', 'o32', 'date']
    if row == '累计单位净值':
        v = v.fillna(method='bfill')
    return v


def analyze_new(data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    data = data[data['VC_KMDM'].notnull()].copy()
    data['EN_SZ'] = data['EN_SZ'].fillna(method='bfill')
    data = data.fillna(0)
    data['VC_KMDM'] = data['VC_KMDM'].apply(rstrip)
    mapping = {
        'asset': ('资产类合计',), 'debt': ('负债类合计',), 'net_asset': ('基金资产净值',), 'shares': ('实收资本', 'L_SL'),
        'unit_nav': ('基金单位净值', 'VC_KMMC'), 'acc_nav': ('累计单位净值', 'VC_KMMC'), 'savings': ('1002',),
        'fund_invest': ('1105',), 'dividend_rec': ('1203',), 'interest_rec': ('1204',), 'purchase_rec': ('1207',),
        'redemption_pay': ('2203',), 'redemption_fee_pay': ('2204',), 'management_pay': ('2206',),
        'custodian_pay': ('2207',), 'profit_pay': ('223201',), 'withholding_pay': ('2501',), 'liquidation': ('3003',),
        'value_added': ('基金资产净值', 'EN_GZZZ',), 'cash_dividend': ('累计派现金额', 'VC_KMMC',),
        'security_deposit': ('1031',), 'interest_pay': ('2221',)
    }
    ret = []
    for name, location in mapping.items():
        r = locate_new(data, *location)
        r['attr'] = name
        ret.append(r)
    ret = pd.concat(ret)
    ret = ret.reset_index(drop=True)
    ret['value'] = ret['value'].astype('float')
    ret['date'] = ret['date'].apply(lambda x: parse(x).date())
    ret = ret.drop_duplicates(['attr', 'o32', 'date'])
    group = ret.groupby('o32')
    data = {}
    for code, g in group:
        g = g.pivot_table(index='date', columns='attr', values='value')
        columns = g.columns
        for x in mapping:
            if x not in columns:
                g[x] = 0
        data[code] = g
    return data
