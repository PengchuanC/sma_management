import datetime
import pandas as pd

from concurrent.futures import ThreadPoolExecutor
from dateutil.parser import parse
from django.forms import model_to_dict
from django.http import HttpResponse, Http404
from rest_framework.views import APIView, Response
from investment.utils.backtest import BackTest, BTConfig
from investment.utils.calc import Formula
from investment import models
from investment.utils.download import file_dir


tpe = ThreadPoolExecutor(2)

fund_date = None


class BackTestView(APIView):

    date = None

    def get(self, request):
        date = request.query_params.get('date')
        if not date:
            date = datetime.date.today()
        else:
            date = parse(date).date()
        btc = BTConfig()
        btc.end = date
        bt = BackTest(btc)
        bt.init()
        port = {'cash': 0.02, 'fix': 0.05, 'equal': 0.10, 'increase': 0.15, 'equity': 0.18}
        data = []
        for name, risk in port.items():
            ret = bt.run(risk)
            ret.columns = [name]
            data.append(ret)
        data = pd.concat(data, axis=1)
        index = BackTestView.get_index()
        data = pd.merge(data, index, left_index=True, right_index=True)
        data = data[data.index < date]
        perf = data.copy()
        perf = self.calc_performance(perf)
        perf = perf.reset_index()
        names = {
            'cash': '现金型', 'fix': '固收型', 'equal': '平衡型', 'increase': '成长型', 'equity': '权益型',
            'zz800': '中证800', 'zcf': '中债总财富'
        }
        perf['index'] = perf['index'].apply(lambda x: names.get(x))

        # 子线程生成文件
        def write_file(data_, perf_, file_dir_):
            excel = pd.ExcelWriter(file_dir_ / 'backtest.xlsx')
            nav = data_.rename(columns=names).copy()
            nav.to_excel(excel, sheet_name='回测净值')
            perf_.to_excel(excel, sheet_name='业绩表现')
            excel.save()
            excel.close()

        global fund_date
        if date != fund_date:
            tpe.submit(write_file, data, perf, file_dir)

        perf['key'] = perf.index + 1
        data = data.reset_index()
        data['key'] = data.index + 1
        data = data.to_dict(orient='records')
        perf = perf.to_dict(orient='records')
        fund_date = date
        return Response({'nav': data, 'perf': perf})

    @staticmethod
    def get_index():
        """获取指数回测业绩"""
        codes = {'000906': 'zz800', 'Y00001': 'zcf'}
        data = models.IndexQuote.objects.filter(
            secucode__in=codes.keys(), date__gte='2017-01-01'
        ).values('secucode', 'date', 'close')
        data = pd.DataFrame(data)
        data.close = data.close.astype('float')
        data = pd.pivot_table(data, columns='secucode', index='date', values='close')
        data = data.fillna(method='pad')
        data = data.rename(columns=codes)
        data = data / data.iloc[0, :]
        return data

    @staticmethod
    def download(request):
        file_path = file_dir / 'backtest.xlsx'
        if file_path.is_file():
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + file_path.name
                return response
        raise Http404

    @staticmethod
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


class BacktestWeightView(APIView):
    @staticmethod
    def get(request):
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
        return Response(w)

    @staticmethod
    def download(request):
        file_path = file_dir / 'weight.xlsx'
        if file_path.is_file():
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + file_path.name
                return response
        raise Http404
