import datetime

import arrow
import pandas as pd

from django.http import HttpResponse, Http404, JsonResponse
from channels.db import database_sync_to_async

from sma_management.settings import RpcProxyHost
from investment.utils.calc import Formula
from investment import models
from investment.utils.download import file_dir
from services.backtest_client import Client


async def index_data():
    queryset = await database_sync_to_async(
        models.IndexQuote.objects.filter(secucode__in=['Y00001', '000906'], date__gte='2017-01-01').values
    )('secucode', 'date', 'close')
    data = await database_sync_to_async(pd.DataFrame)(queryset)
    data['close'] = data['close'].astype(float)
    data = data.pivot_table(index='date', columns='secucode', values='close')
    data /= data.iloc[0, :]
    data = data.rename(columns={'Y00001': 'zcf', '000906': 'zz800'})
    return data


def calc_performance(data: pd.DataFrame):
    ret = {}

    for item in [
        "acc_return_yield",
        "annualized_return_yield",
        "annualized_volatility",
        "max_drawback",
        "sharpe_ratio",
        "calmar_ratio",
        "sortino_ratio",
        "var",
        "cvar"
    ]:
        n = getattr(Formula, item)(data).to_dict()
        if item == 'annualized_volatility':
            for item_ in ['vol', 'downside_vol']:
                n_ = {x: y[item_] for x, y in n.items()}
                ret.update({item_: n_})
        elif item == 'max_drawback':
            n = {x: y['drawback'] for x, y in n.items()}
            ret.update({item: n})
        else:
            ret.update({item: n})
    ret = pd.DataFrame(ret)
    return ret


async def portfolio_nav(request, rpc_method: str):
    """标准基金组合数据"""
    date = request.GET.get('date', datetime.date.today())
    date = arrow.get(date).date()
    with Client(*RpcProxyHost.split(':')) as client:
        data = getattr(client, rpc_method)()
    mapping = {1: 'cash', 2: 'fix', 3: 'equal', 4: 'increase', 5: 'equity'}
    data = [{'port_name': mapping.get(x.port_code), 'date': arrow.get(x.date).date(), 'unitnv': x.unitnv} for x in data]
    data = pd.DataFrame(data).pivot_table(index='date', columns='port_name', values='unitnv')
    index = await index_data()
    data = data.merge(index, left_index=True, right_index=True)
    data = data[data.index <= date]
    data = data.fillna(method='pad')
    perf = calc_performance(data)
    perf = perf.reset_index()
    return data, perf


async def standard_portfolio(request):
    """标准基金组合数据"""
    data, perf = await portfolio_nav(request, 'standard_portfolio')
    names = {
        'cash': '现金型', 'fix': '固收型', 'equal': '平衡型', 'increase': '成长型', 'equity': '权益型',
        'zz800': '中证800', 'zcf': '中债总财富'
    }
    perf['index'] = perf['index'].apply(lambda x: names.get(x))
    with pd.ExcelWriter(file_dir / 'backtest.xlsx') as excel:
        data.rename(columns=names).to_excel(excel, sheet_name='回测净值')
        perf.to_excel(excel, sheet_name='业绩表现')
    perf = perf.to_dict(orient='records')
    nav = data.reset_index().to_dict(orient='records')
    return JsonResponse(data={'nav': nav, 'perf': perf})


def download(request):
    file_path = file_dir / 'backtest.xlsx'
    if file_path.is_file():
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + file_path.name
            return response
    raise Http404


async def fund_index_portfolio(request):
    """基金指数组合净值"""
    data, perf = await portfolio_nav(request, 'fund_index_portfolio')
    names = {
        'cash': '现金型', 'fix': '固收型', 'equal': '平衡型', 'increase': '成长型', 'equity': '权益型',
        'zz800': '中证800', 'zcf': '中债总财富'
    }
    perf['index'] = perf['index'].apply(lambda x: names.get(x))
    perf = perf.to_dict(orient='records')
    nav = data.reset_index().to_dict(orient='records')
    return JsonResponse(data={'nav': nav, 'perf': perf})


class BacktestWeightView(object):
    def get(self, request):
        w = self.process(request)
        return Response(w)

    @staticmethod
    def process(request):
        smooth = request.query_params.get('smooth', False)
        data = models.AssetWeight.objects.filter(date__gte='2014-01-01').all()
        data = [model_to_dict(x) for x in data]
        data = pd.DataFrame(data)
        data = data.drop(['id', 'annual_r', 'risk'], axis=1)
        data['date'] = data['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        w = data.set_index('date')
        w = w.fillna(0)
        w['equity'] = w['hs300'] + w['zz500'] + w['zz'] + w['hs']
        w['bond'] = w['zcf'] + w['qyz']
        w['alter'] = w['hj']
        w['cash'] = w['hb']
        if smooth:
            w = w.groupby(['target_risk']).rolling(window=3*12).mean().dropna()
            index: pd.MultiIndex = w.index
            w['target_risk'] = index.get_level_values(level=0)
            w['date'] = index.get_level_values(level=1)
            w = w.reset_index(drop=True)
        else:
            w = w.reset_index()
        w['key'] = w.index + 1

        def write_file(w_, file_dir_):
            w_.to_excel(file_dir_ / 'weight.xlsx')

        tpe.submit(write_file, w, file_dir)

        w = w.to_dict(orient='records')
        return w

    @staticmethod
    async def weight(request):
        date = request.GET.get('date', datetime.date.today())
        date = arrow.get(date).date()
        with Client(*RpcProxyHost.split(':')) as client:
            data = client.weight()
        data = [{
            'target_risk': round(x.target_risk, 2), 'date': x.date, 'equity_bound_limit': 0.5, 'equity': x.equity,
            'bond': x.fixed_income, 'alter': x.alternative, 'cash': x.monetary, 'hs300': x.hs300, 'zz500': x.zz500,
            'zz': x.zz, 'hs': x.hs, 'zcf': x.llz, 'qyz': x.xyz, 'hb': x.hb, 'hj': x.hj, 'key': idx + 1
        } for idx, x in enumerate(data) if arrow.get(x.date).date() <= date]
        df = pd.DataFrame(data)
        df.to_excel(file_dir / 'weight.xlsx', index=False)
        return JsonResponse(data, safe=False)

    @staticmethod
    def download(request):
        file_path = file_dir / 'weight.xlsx'
        if file_path.is_file():
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + file_path.name
                return response
        raise Http404
