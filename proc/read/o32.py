import pandas as pd

from proc.read.collect import VF


position_wanted = {
    '证券代码': 'secucode', '持仓': 'holding_value', '市值': 'mkt_cap', '当前成本': 'current_cost',
    '含费用成本': 'total_cost', '费用合计': 'fee', '浮动盈亏': 'flow_profit', '总体盈亏': 'total_profit',
    '当日红利': 'dividend', '累计红利': 'total_dividend', '日期': 'date', '基金编号': 'port_code',
    '证券类别': 'category'
}


transaction_wanted = {
    '证券代码': 'secucode', '发生金额': 'amount', '发生后余额': 'balance', '委托价格': 'order_price',
    '委托数量': 'order_value', '发生数量': 'deal_value', '科目发生额': 'operation_amount',
    '发生业务': 'operation', '其他费用': 'fee', '发生日期': 'date', '科目名称': 'subject_name',
    '基金编号': 'port_code'
}


def read_holding(vf: VF):
    data = pd.read_html(vf.absolute)[0]
    data = data.rename(columns=position_wanted)
    data = data.where(data.notnull(), None)
    return data


def read_transaction(vf: VF):
    data = pd.read_html(vf.absolute)[0]
    data = data.rename(columns=transaction_wanted)
    data = data.where(data.notnull(), None)
    return data
