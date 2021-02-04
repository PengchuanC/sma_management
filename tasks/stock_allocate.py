import pandas as pd
from django.db.models import Max
from django.forms.models import model_to_dict

from tasks import models


def industry_sw(data: pd.DataFrame) -> pd.DataFrame:
    """接受基金组合中股票市值占比的DataFrame"""
    funds = list(data.stockcode)
    ind = models.StockIndustrySW.objects.filter(secucode__in=funds).values('secucode', 'firstindustryname')
    ind = pd.DataFrame(ind)
    ind = pd.merge(ind, data, left_on='secucode', right_on='stockcode', how='outer')
    ind.firstindustryname = ind.firstindustryname.fillna('港股')
    ind = ind.groupby(['firstindustryname']).sum()
    ind = ind.reset_index()
    ind = ind.sort_values(['ratio'], ascending=False)
    ind['ratioinequity'] = ind['ratio'] / ind['ratio'].sum()
    ind = ind.reset_index(drop=True)
    ind['key'] = ind.index + 1
    return ind


file = 'C:/users/chuanchao.peng/Desktop/建仓-宜和.xlsx'

data = pd.read_excel(file, engine='openpyxl', converters={'基金代码': str}, skiprows=[0], sheet_name='建仓计划行业分布')
data = data[data['基金代码'].notnull()]
data = data[['基金代码', '配置比例']]

data['基金代码'] = data['基金代码'].apply(lambda x: x[:6])
fund = data[['基金代码', '配置比例']]
fund = fund.rename(columns={'基金代码': 'secucode', '配置比例': 'mkt_cap'})
fund = fund.to_dict(orient='records')
fund_codes = [x[:6] for x in data['基金代码']]

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

equity_ratio = models.FundAssetAllocate.objects.filter(secucode__in=funds.keys()).order_by('date', 'secucode')
equity_ratio = [model_to_dict(x) for x in equity_ratio]
equity_ratio = pd.DataFrame(equity_ratio)
equity_ratio = equity_ratio.drop_duplicates(['secucode'], keep='last')
equity_ratio = dict(zip(equity_ratio['secucode'], equity_ratio['stock'].astype('float')))

data: pd.DataFrame = pd.DataFrame(query_set)
data.ratio = data.ratio.astype('float')

# 计算前十大占比
top = data[['secucode', 'ratio']].groupby('secucode').sum().reset_index()
top = dict(zip(top.secucode, top.ratio))

data['ratio'] = data.aggregate(func=lambda x: float(x['ratio']) * funds.get(x['secucode']), axis=1)
data['ratio_est'] = data.aggregate(
    func=lambda x: float(x['ratio']) / top.get(x['secucode']) * equity_ratio.get(x['secucode'])
    if equity_ratio.get(x['secucode']) else None,
    axis=1
)
data.to_clipboard()
names = dict(zip(data['stockcode'], data['stockname']))
data = data.groupby(['stockcode']).sum()
data = data.reset_index()
data['stockname'] = data.stockcode.apply(lambda x: names.get(x))
data = data.sort_values(by='ratio', ascending=False).reset_index(drop=True)
data['key'] = data.index + 1

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
a = data.copy()
ind = industry_sw(data)
print(ind)

excel = pd.ExcelWriter('C:/users/chuanchao.peng/Desktop/result.xlsx')
a.to_excel(excel, sheet_name='持股')
ind.to_excel(excel, sheet_name='行业')
excel.save()
excel.close()
