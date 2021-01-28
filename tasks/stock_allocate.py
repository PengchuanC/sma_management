import pandas as pd
from tasks import models
from investment.views import FundHoldingStockView
from django.db.models import Max


file = 'C:/users/chuanchao.peng/Desktop/基金配置比例v2.xlsx'

data = pd.read_excel(file, engine='openpyxl', converters={'AH两地': str})
data = data[data['基金名称'].notnull()]

data['AH两地'] = data['AH两地'].apply(lambda x: x[:6])
fund = data[['AH两地', '比例']]
fund = fund.rename(columns={'AH两地': 'secucode', '比例': 'mkt_cap'})
fund = fund.to_dict(orient='records')
fund_codes = [x[:6] for x in data['AH两地']]

# 获取基金主代码
associate = models.FundAssociate.objects.filter(relate__in=fund_codes).order_by('define').values('secucode', 'relate')
associate = {x['relate']: x['secucode'] for x in associate}
na = 1
funds = {associate.get(x['secucode'], x['secucode']): x['mkt_cap'] / na for x in fund}
recent_report_date = models.FundHoldingStock.objects.values('secucode').annotate(recent=Max('date'))
recent = {x['secucode']: x['recent'] for x in recent_report_date}
query_set = []
for fund in funds:
    stocks = models.FundHoldingStock.objects.filter(
        secucode=fund, date=recent.get(fund)
    ).values('secucode', 'stockcode', 'stockname', 'ratio', 'publish')
    publish = set([x['publish'] for x in stocks])
    if '年报' in publish:
        stocks = [x for x in stocks if x['publish'] == '年报']
    query_set.extend(stocks)

data: pd.DataFrame = pd.DataFrame(query_set)
print(data)
data.to_clipboard()
data['ratio'] = data.aggregate(func=lambda x: float(x['ratio']) * funds.get(x['secucode']), axis=1)
names = dict(zip(data['stockcode'], data['stockname']))
data = data.groupby(['stockcode'])['ratio'].sum()
data = data.reset_index()
data['stockname'] = data.stockcode.apply(lambda x: names.get(x))
data = data.sort_values(by='ratio', ascending=False).reset_index(drop=True)
data['key'] = data.index + 1
print(data)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
a = data.copy()
ind = FundHoldingStockView.industry_sw(data)
print(ind)

excel = pd.ExcelWriter('C:/users/chuanchao.peng/Desktop/result.xlsx')
a.to_excel(excel, sheet_name='持股')
ind.to_excel(excel, sheet_name='行业')
excel.save()
excel.close()