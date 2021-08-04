"""
投资分析模块
包含业绩表现、业绩归因、风格分析等内容
"""

import datetime
from decimal import Decimal

import pandas as pd
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from django.db.models import Max
from django.http.response import JsonResponse
from rest_framework.views import APIView, Response
from asgiref.sync import sync_to_async

from investment.models import (
    Income, IncomeAsset, ValuationBenchmark as VB, Holding, Balance, FundAdjPrice as FAP, TradingDays,
    FundPurchaseAndRedeem as FAR, StockIndustrySW as SISW, FundAssetAllocate as FAA, FundAssociate
)

from investment import models

from investment.utils.calc import Formula, capture_return
from investment.utils import fund, period_change as pc
from investment.utils.holding import fund_holding_stock, index_holding_sw, fund_top_ten_scale
from rpc.client import Client


class PerformanceView(APIView):
    """业绩表现视图"""

    @staticmethod
    def get(request):
        date = request.query_params.get('date')
        port_code = request.query_params.get('portCode')
        if not date:
            date = datetime.date.today().strftime('%Y-%m-%d')
        p_nav = Income.objects.filter(
            port_code=port_code, date__lte=date).values('date', 'unit_nav')
        b_nav = VB.objects.filter(
            port_code=port_code, date__lte=date).values('date', 'unit_nav')
        p_nav = pd.DataFrame(p_nav).rename(columns={'unit_nav': 'p'})
        b_nav = pd.DataFrame(b_nav).rename(columns={'unit_nav': 'b'})
        data = pd.merge(p_nav, b_nav, on='date', how='inner').set_index('date')
        data = data.astype('float')
        ret = PerformanceView.calc_performance(data)
        ucr = capture_return(data.p, data.b, mode=1)
        dcr = capture_return(data.p, data.b, mode=0)
        ret.update({'ucr': {'p': ucr, 'b': None},
                   'dcr': {'p': dcr, 'b': None}})
        return Response(ret)

    @staticmethod
    def calc_performance(data: pd.DataFrame):
        ret = {}

        for item in [
            "acc_return_yield",
            "annualized_return_yield",
            "daily_change",
            "trading_day_count",
            "annualized_volatility",
            "max_drawback",
            "sharpe_ratio",
            "calmar_ratio",
            "sortino_ratio",
            "var",
            "cvar"
        ]:
            n = getattr(Formula, item)(data).to_dict()
            ret.update({item: n})
        return ret


class AttributeChartView(APIView):
    """收益贡献图"""

    @staticmethod
    def get(request):
        date = request.query_params.get('date')
        port_code = request.query_params.get('portCode')
        if not date:
            date = datetime.date.today().strftime('%Y-%m-%d')
        d: IncomeAsset = IncomeAsset.objects.filter(
            port_code=port_code, date__lte=date).last()
        date = d.date.strftime('%Y-%m-%d')
        cp = float(Income.objects.filter(port_code=port_code,
                   date__lte=date).last().unit_nav) - 1
        a = d.total_profit
        data = {
            'total_profit': round(cp * 100, 2), 'equity': round(cp * float(d.equity/a) * 100, 2),
            'bond': round(cp*float(d.bond/a)*100, 2), 'alter': round(cp*float(d.alter/a)*100, 2),
            'money': round(cp*float(d.money/a)*100, 2)
        }
        # 周度区间
        week = AttributeChartView.last_trading_day_of_last_week(date)
        month = AttributeChartView.last_trading_day_of_last_month(date)
        ret = []
        for ltw in [week, month]:
            sd: IncomeAsset = IncomeAsset.objects.get(
                port_code=port_code, date=ltw)
            scp = float(Income.objects.filter(
                port_code=port_code, date=ltw).last().unit_nav)
            scp = (cp + 1) / scp - 1
            a = d.total_profit - sd.total_profit
            change = {}
            for attr in ['total_profit', 'equity', 'bond', 'alter', 'money']:
                change[attr] = round(
                    scp * float((getattr(d, attr) - getattr(sd, attr)) / a) * 100, 2)
            ret.append(change)
        return Response({'data': data, 'week': ret[0], 'month': ret[1]})

    @staticmethod
    def monthly_attribute(request):
        """月度收益归因"""
        port_code = request.GET.get('portCode')
        date = request.GET.get('date')
        if not date:
            date = datetime.date.today().strftime('%Y-%m-%d')
        d: IncomeAsset = IncomeAsset.objects.filter(port_code=port_code, date__lte=date).last()
        date = d.date.strftime('%Y-%m-%d')
        launch = models.Income.objects.filter(port_code=port_code).first().date
        week = AttributeChartView.last_trading_day_of_last_week(date)
        month = AttributeChartView.last_trading_day_of_last_month(date)
        ret = []
        for start in [launch, week, month]:
            if start < launch:
                start = launch
            changes = models.Income.objects.filter(
                port_code=port_code, date__range=(start, date)).values('date', 'unit_nav', 'change')
            changes = [x for x in changes]
            total = float(sum([x['change'] for x in changes[1:]]))
            columns = ['equity', 'bond', 'alter', 'money']
            fee = models.DetailFee.objects.filter(
                port_code=port_code, date__gt=start, date__lte=date).values('management')
            fee = float(sum(x['management'] for x in fee))
            asset = models.IncomeAsset.objects.filter(
                port_code=port_code, date__in=(start, date)).values('date', *columns)
            asset = pd.DataFrame(asset).set_index('date')
            asset = asset.diff(1).dropna().astype(float)
            asset /= asset.sum(axis=1).sum()
            change = float(changes[-1]['unit_nav'] / changes[0]['unit_nav']) - 1
            fee_ratio = - fee / total * change
            asset *= (change - fee_ratio)
            asset['fee'] = fee_ratio
            asset['change'] = change
            asset = asset.to_dict(orient='records')[0]
            asset['total_profit'] = change
            asset = {x: round(y*100, 2) for x, y in asset.items()}
            ret.append(asset)
        return JsonResponse({'data': ret[0], 'week': ret[1], 'month': ret[2]})

    @staticmethod
    def last_trading_day_of_last_week(date: str):
        """上周最后一个交易日"""
        date = parse(date).date()
        sunday = date - datetime.timedelta(days=date.weekday()+1)
        prev = Balance.objects.filter(date__lt=sunday).latest('date').date
        return prev

    @staticmethod
    def last_trading_day_of_last_month(date: str):
        """上月最后一个交易日"""
        date = parse(date).date()
        begin = datetime.date(date.year, date.month, 1) - \
            datetime.timedelta(days=1)
        prev = Balance.objects.filter(date__lte=begin).latest('date').date
        return prev


class FundHoldingView(APIView):
    """持有基金分析
    """

    def get(self, request):
        port_code, date = self.parse_request(request)

        holding = self.fund_ratio(port_code, date)
        holding['key'] = holding.index + 1

        funds = list(set(list(holding.secucode)))
        names = fund.fund_names(funds)

        # rpc获取基金分类
        try:
            category = self.fund_category(funds)
            holding = holding.merge(category, on='secucode', how='left')
        except Exception as e:
            holding['category'] = [None] * len(holding)

        perf = FundHoldingView.fund_performance(port_code, date)
        holding['secuname'] = holding.secucode.apply(lambda x: names.get(x))
        holding = pd.merge(holding, perf, on='secucode', how='left')

        limit = FundHoldingView.fund_limit(funds)
        holding = pd.merge(holding, limit, how='left', on='secucode')
        holding = holding.where(holding.notnull(), None)

        holding = holding.to_dict(orient='records')
        return Response(holding)

    @staticmethod
    def parse_request(request):
        date = request.query_params.get('date')
        port_code = request.query_params.get('portCode')
        if not date:
            date = datetime.date.today().strftime('%Y-%m-%d')
        date = Holding.objects.filter(
            port_code=port_code, date__lte=date).latest('date').date
        return port_code, date

    @staticmethod
    def etf_profit(request):
        """etf每日收益，取最近5个交易日"""
        port_code = request.GET['portCode']
        date = request.GET.get('date')
        if not date:
            date = models.Holding.objects.filter(port_code=port_code).latest('date').date
        else:
            date = models.Holding.objects.filter(port_code=port_code, date__lte=date).latest('date').date
        holdings = models.Holding.objects.filter(
            port_code=port_code, date__lte=date, trade_market__in=(1, 2), category='开放式基金'
        ).values()
        holdings = pd.DataFrame(holdings)
        holdings = holdings.drop_duplicates(['holding_value', 'mkt_cap', 'total_profit'])
        holdings['key'] = holdings.index
        funds = list(set(list(holdings.secucode)))
        names = fund.fund_names(funds)
        holdings['secuabbr'] = holdings['secucode'].apply(lambda x: names.get(x))
        need = ['key', 'secucode', 'secuabbr', 'date', 'total_profit', 'fee', 'mkt_cap', 'holding_value']
        holdings = holdings[need]

        ret = []
        count = 1
        for _, g in holdings.groupby('secucode'):
            g_max = g[g.date == g.date.max()]
            g_max = g_max.to_dict(orient='records')[0]
            g_max['key'] = len(holdings) + count
            for attr in ['total_profit', 'fee']:
                g[attr] = g[attr].diff()
            g = g[g['total_profit'].notnull()].sort_values('date', ascending=False)
            g = g.to_dict(orient='records')
            g_max['children'] = g
            ret.append(g_max)
            count += 1
        return JsonResponse(ret, safe=False)

    @staticmethod
    def etf_transaction_analysis(request):
        """分析etf每笔买入的持仓收益"""
        port_code = request.GET['port_code']
        secucode = request.GET['secucode']
        ret = FundHoldingView._etf_transaction_analysis(port_code, secucode)
        ret = pd.DataFrame(ret)
        total = ret['profit'].sum()
        win = len(ret[ret.r >= 0]) / len(ret)
        data = ret.to_dict(orient='records')
        return JsonResponse({'total': total, 'win': win, 'data': data})

    @staticmethod
    def etf_transaction_whole(request):
        port_code = request.GET['port_code']
        funds = models.Transactions.objects.filter(port_code=port_code, operation='证券买入').values('secucode')
        funds = set(x['secucode'] for x in funds)
        ret = []
        for etf in funds:
            r = FundHoldingView._etf_transaction_analysis(port_code, etf)
            ret.extend(r)
        ret = pd.DataFrame(ret)
        win = len(ret[ret.r >= 0]) / len(ret)
        total = ret['profit'].sum()
        data = ret.to_dict(orient='records')
        return JsonResponse({'total': total, 'win': win, 'data': data})

    @staticmethod
    def _etf_transaction_analysis(port_code, secucode):
        """分析etf每笔买入的持仓收益"""
        last = models.FundQuote.objects.filter(secucode=secucode).latest('date')
        price = round(last.closeprice, 4)
        date = last.date
        trans = models.Transactions.objects.filter(
            port_code=port_code, secucode=secucode, operation__in=('证券买入', '证券卖出')
        ).values('secucode', 'date', 'operation', 'order_price', 'order_value', 'fee').order_by('date')
        buy = [x for x in trans if x['operation'] == '证券买入']
        buy = pd.DataFrame(buy)
        buy = buy.groupby(['secucode', 'date', 'operation', 'order_price']).sum().reset_index()
        sell = [x for x in trans if x['operation'] == '证券卖出']
        sell = pd.DataFrame(sell)
        if not sell.empty:
            sell = sell.groupby(['secucode', 'date', 'operation', 'order_price']).sum().reset_index()

        ret = []
        for idx1, b in buy.iterrows():
            b_value = b['order_value']
            b_price = b['order_price']
            b_fee = b['fee']
            b_date = b['date']
            secucode = b['secucode']
            while b_value > 0:
                if sell.empty or sell['order_value'].sum() == 0:
                    s_price = round(Decimal(price), 4)
                    r = s_price / b_price - 1
                    value = b_value
                    b_value = 0
                    profit = (s_price * value) - b_price * value - b_fee
                    ret.append({
                        'buy_date': b_date.strftime('%Y-%m-%d'), 'sell_date': date.strftime('%Y-%m-%d'),
                        'buy_price': b_price, 'sell_price': s_price, 'value': value, 'r': r, 'profit': profit,
                        'fee': b_fee, 'note': '预估', 'secucode': secucode

                    })
                    continue
                for idx2, s in sell.iterrows():
                    s_value = s['order_value']
                    s_price = s['order_price']
                    s_date = s['date']
                    s_fee = s['fee']
                    r = s_price / b_price - 1
                    if s_value == 0:
                        continue
                    if b_value <= s_value:
                        real_s_fee = s_fee * b_value / s_value
                        profit = (b_value * s_price - real_s_fee - b_fee) - (b_value * b_price)
                        fee = real_s_fee + b_fee
                        sell.loc[idx2, 'order_value'] = s_value - b_value
                        sell.loc[idx2, 'fee'] = s_fee - real_s_fee
                        value = b_value
                        b_value = 0
                    else:
                        real_b_fee = b_fee * s_value / b_value
                        profit = (s_value * s_price - s_fee - real_b_fee) - b_price * s_value
                        fee = real_b_fee + s_fee
                        b_fee -= real_b_fee
                        b_value -= s_value
                        value = s_value
                        sell.loc[idx2, 'order_value'] = 0

                    ret.append({
                        'buy_date': b_date.strftime('%Y-%m-%d'), 'sell_date': s_date.strftime('%Y-%m-%d'),
                        'buy_price': b_price, 'sell_price': s_price, 'value': value, 'r': r, 'profit': profit,
                        'fee': fee, 'note': '已实现', 'secucode': secucode
                    })
        return ret

    @staticmethod
    def fund_ratio(port_code: str, date: datetime.date, otc=False):
        """组合持有基金的比例"""
        cannot_resolve = ['国债标准券']
        if otc:
            market = [6]
        else:
            market = (1, 2, 6)
        holding = Holding.objects.filter(
            port_code=port_code, date=date, trade_market__in=market
        ).exclude(category__in=cannot_resolve).values(
            'secucode', 'mkt_cap', 'total_profit')
        na = Balance.objects.get(port_code=port_code, date=date).net_asset
        holding = pd.DataFrame(holding)

        holding['ratio'] = holding.mkt_cap / na
        holding = holding[holding['ratio'] >= 0]
        holding = holding.sort_values(
            by=['ratio'], ascending=False).reset_index(drop=True)
        return holding

    @staticmethod
    def fund_performance(port_code, date):
        holding = models.Holding.objects.filter(
            port_code=port_code, date=date, category='开放式基金').values('secucode', 'trade_market')
        cw = [x['secucode'] for x in holding if x['trade_market'] == 6]
        cn = [x['secucode'] for x in holding if x['trade_market'] in (1, 2)]
        cw_data = FundHoldingView.period_return(cw, date, 6)
        cn_data = FundHoldingView.period_return(cn, date, 1)
        data = cw_data.append(cn_data)
        return data

    @staticmethod
    def period_return(funds: list, date: datetime.date, market=6):
        start = date - relativedelta(years=1, months=1)
        if market == 6:
            data = FAP.objects.filter(
                secucode__in=funds, date__range=[start, date]).values('secucode', 'adj_nav', 'date')
            data = pd.DataFrame(data)
        else:
            data = models.FundQuote.objects.filter(
                secucode__in=funds, date__range=[start, date]).values('secucode', 'closeprice', 'date')
            data = pd.DataFrame(data)
            if data.empty:
                return data
            data = data.rename(columns={'closeprice': 'adj_nav'})
        data.adj_nav = data.adj_nav.astype('float')
        data = pd.pivot_table(data, index='date', columns='secucode', values=[
                              'adj_nav'])['adj_nav']
        data = data.sort_index()
        tradingdays = TradingDays.objects.filter(
            date__range=[start, date]).values('date')
        tradingdays = [x['date'] for x in tradingdays]
        data = data[data.index.isin(tradingdays)]
        p = pc.Performance(data)
        col = ['day', 'week', 'month', 'quarter', 'half_year', 'year', 'ytd']
        ret = []
        for attr in col:
            ret.append(getattr(p, attr)())
        ret = pd.concat(ret, axis=1)
        ret.columns = col
        ret = ret.reset_index()
        return ret

    @staticmethod
    def fund_limit(funds):
        """基金当日申赎限制"""
        date = FAR.objects.aggregate(mdate=Max('date'))['mdate']
        limit = FAR.objects.filter(secucode__in=funds, date=date).values(
            'secucode', 'apply_type', 'redeem_type', 'min_apply', 'max_apply'
        )
        limit = pd.DataFrame(limit)
        return limit

    @staticmethod
    def fund_category(funds):
        """获取基金分类"""
        category = Client.simple('fund_category_full', funds)
        category = pd.DataFrame(category)
        return category

    @staticmethod
    def asset_allocate(port_code: str, date: datetime.date, otc=True):
        """获取组合的资产配置情况
        :return: {'stock': 0, 'bond': 0, 'fund': 0, 'metals': 0, 'monetary': 0}
        """
        holding = FundHoldingView.fund_ratio(port_code, date, otc)
        holding = holding[holding.ratio > 0]
        funds = list(holding.secucode)
        relate = FundAssociate.objects.filter(
            relate__in=funds).order_by('define').all()
        relate = {x.relate: x.secucode.secucode for x in relate}
        dates = FAA.objects.filter(secucode__in=funds).values(
            'secucode').annotate(max_date=Max('date'))
        data = []
        dates = {x['secucode']: x['max_date'] for x in dates}
        for x in funds:
            secucode = x
            date = dates.get(secucode)
            if not date:
                # 处理联接基金及LOF
                try:
                    date = FAA.objects.filter(secucode=relate.get(x)).latest().date
                except FAA.DoesNotExist:
                    continue
                d = FAA.objects.filter(secucode=relate.get(secucode), date=date).values(
                    'secucode', 'stock', 'bond', 'fund', 'metals', 'monetary', 'other'
                )[0]
                d['secucode'] = secucode
            else:
                d = FAA.objects.filter(secucode=secucode, date=date).values(
                    'secucode', 'stock', 'bond', 'fund', 'metals', 'monetary', 'other'
                )[0]
            data.append(d)
        data = pd.DataFrame(data).set_index('secucode')
        data = data.merge(holding[['secucode', 'ratio']],
                          left_index=True, right_on='secucode').set_index('secucode')
        columns = ['stock', 'bond', 'fund', 'metals', 'monetary', 'other']
        for col in columns:
            data[col] *= data['ratio']
        data = data[columns]
        return data.sum().to_dict()

    @staticmethod
    def holding_yx(request):
        """宜信普泽份额"""
        port_code = request.GET.get('portCode')
        date = request.GET.get('date')
        if not date:
            date = datetime.date.today().strftime('%Y-%m-%d')
        date = Holding.objects.filter(port_code=port_code, date__lte=date).aggregate(
            mdate=Max('date'))['mdate']
        holding = models.Holding.objects.filter(
            port_code=port_code, date=date).values('secucode', 'mkt_cap', 'holding_value')
        holding = pd.DataFrame(holding)
        holding = holding[holding['holding_value'] != 0]
        holding_yx = models.HoldingYX.objects.filter(
            port_code=port_code, date=date).values('secucode', 'shares')
        holding_yx = pd.DataFrame(holding_yx)
        if holding_yx.empty:
            holding['shares'] = 0
            data = holding
        else:
            data = holding.merge(holding_yx, how='left', on='secucode')
            data['shares'] = data['shares'].fillna(0)
        data['ratio'] = data['shares'] / data['holding_value']
        funds = list(set(list(data.secucode)))
        names = fund.fund_names(funds)
        data['secuname'] = data.secucode.apply(lambda x: names.get(x))
        data = data.sort_values(
            'ratio', ascending=False).reset_index(drop=True)
        data['key'] = data.index + 1
        ret = data.to_dict(orient='records')
        return JsonResponse({'data': ret})


class FundHoldingStockView(APIView):
    """持有股票分析"""
    @staticmethod
    def get(request):
        port_code = request.query_params.get('portCode')
        date = request.query_params.get('date')
        if not date:
            date = Balance.objects.filter(
                port_code=port_code).last().date.strftime('%Y-%m-%d')
        else:
            date = Balance.objects.filter(
                port_code=port_code, date__lte=date).last().date.strftime('%Y-%m-%d')
        ret = fund_holding_stock(port_code, date)
        ind = FundHoldingStockView.industry_sw(ret)
        ratio = FundHoldingView.asset_allocate(port_code, date)
        index = FundHoldingStockView.industry_index_top_ten(port_code)
        equity = ratio.get('stock')
        ind['ratio'] = ind['ratio'].astype('float')
        ind['ratioinequity'] = ind['ratio'] / float(equity)
        ind = ind.merge(index, on='firstindustryname', how='outer').fillna(0)
        ind = ind.sort_values(
            ['ratio'], ascending=False).reset_index(drop=True)
        ind['key'] = ind.index + 1
        ret['ofnv'] = ret['ratio'] / ret['ratio'].sum()
        ret['cumsum'] = ret['ratio'].cumsum()
        ret = ret.to_dict(orient='records')
        ind = ind.to_dict(orient='records')
        return Response({'stock': ret, 'industry': ind})

    @staticmethod
    def industry_sw(data: pd.DataFrame) -> pd.DataFrame:
        """接受基金组合中股票市值占比的DataFrame"""
        funds = list(data.stockcode)
        ind = SISW.objects.filter(secucode__in=funds).values(
            'secucode', 'firstindustryname')
        ind = pd.DataFrame(ind)
        ind = pd.merge(ind, data, left_on='secucode',
                       right_on='stockcode', how='outer')
        ind.firstindustryname = ind.firstindustryname.fillna('港股')
        ind = ind.groupby(['firstindustryname'])['ratio'].sum()
        ind: pd.DataFrame = ind.reset_index()
        ind['ratioinequity'] = ind['ratio'] / ind['ratio'].sum()
        ind = ind.reset_index(drop=True)
        return ind

    @staticmethod
    def industry_index_top_ten(port_code: str):
        """组合100%化后与中证800对比

        Args:
            port_code:

        Returns:
               firstindustryname scaled_ratio   weight      diff
            0               交通运输  0.045806  0.02636  0.019446
            1               休闲服务  0.021357  0.01320  0.008157
            2                 传媒  0.009180  0.02111 -0.011930
            3               农林牧渔  0.013617  0.02025 -0.006633
            4                 化工  0.056625  0.04776  0.008865
            5               医药生物  0.095320  0.09882 -0.003500

        """
        latest = Holding.objects.filter(
            port_code=port_code).latest('date').date
        holding = Holding.objects.filter(
            port_code=port_code, date=latest).values('secucode', 'mkt_cap')
        holding = pd.DataFrame(holding)
        holding = holding[holding['mkt_cap'] != 0]

        stocks = []
        for fund_ in holding['secucode']:
            stock = fund_top_ten_scale(fund_)
            if stock is None:
                continue
            stocks.append(stock)
        stocks = pd.concat(stocks, axis=0)
        data = stocks.merge(holding, on='secucode', how='left')
        mkt_cap = data.drop_duplicates(['secucode'])['mkt_cap'].sum()
        data['ratio'] = data['ratio']*data['mkt_cap'] / mkt_cap
        data = data.groupby(['stockcode'])['ratio'].sum().reset_index()

        sw = SISW.objects.filter(secucode__in=list(data.stockcode)).values(
            'secucode', 'firstindustryname')
        sw = {x['secucode']: x['firstindustryname'] for x in sw}
        data['firstindustryname'] = data['stockcode'].apply(
            lambda x: sw.get(x, '港股'))
        data = data.groupby(['firstindustryname'])['ratio'].sum().reset_index()

        index = index_holding_sw('000906')
        index = index.groupby(['firstindustryname'])[
            'weight'].sum().reset_index()
        data = data.merge(index, on='firstindustryname', how='outer')
        data['ratio'] = data['ratio'].astype('float')
        data['weight'] = data['weight'].astype('float')
        data['diff'] = data['ratio'] - data['weight']
        data = data.fillna(0)
        data = data.rename(columns={'ratio': 'scaled_ratio'})
        return data


class FundHoldingNomuraOIView(object):
    """根据野村东方分类对基金类型进行汇总"""
    @staticmethod
    def holding_by_NOI_classify(request):
        date = request.GET.get('date')
        port_code = request.GET.get('portCode')
        if not date:
            date = Balance.objects.filter(port_code=port_code)
        else:
            date = Balance.objects.filter(port_code=port_code, date__lte=date)
        date = date.latest('date').date
        data = FundHoldingView.fund_ratio(port_code, date)
        data.mkt_cap = data.mkt_cap.astype('float')
        data.ratio = data.ratio.astype('float')
        funds = list(data.secucode)
        category = FundHoldingView.fund_category(funds)
        data = data.merge(category, how='left', on='secucode')

        names = models.Funds.objects.filter(
            secucode__in=funds).values('secucode', 'secuname')
        names = {x['secucode']: x['secuname'] for x in names}
        data['secuname'] = data['secucode'].apply(lambda x: names.get(x))
        ret = []
        allocate = []
        key = 1
        for category in ['股票型', '债券型', '另类', 'QDII型', '货币型']:
            d = data[data.branch == category]
            allocate.append(
                {'name': category, 'mkt_cap': d.mkt_cap.sum(), 'ratio': d.ratio.sum()})
            d = d.sort_values('ratio', ascending=False)
            children = []
            for _, r in d.iterrows():
                children.append(
                    {'key': key, 'secucode': r.secucode, 'secuname': r.secuname,
                        'mkt_cap': r.mkt_cap, 'ratio': r.ratio}
                )
                key += 1
            ret.append({'key': key, 'secucode': None, 'secuname': category, 'mkt_cap': d.mkt_cap.sum(),
                        'ratio': d.ratio.sum(), 'children': children})
            key += 1

        return JsonResponse({'holding': ret, 'allocate': allocate})
