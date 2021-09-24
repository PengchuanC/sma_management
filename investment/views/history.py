"""
history
~~~~~~~
查看调仓历史和计算历史调仓费用

@modify: 2021-03-03
@desc: 加入换手率
"""

import datetime

from django.db.models import Sum, Max, Min, Avg
from rest_framework.views import APIView, Response

from investment.models.portfolio import Transactions as ta
from investment.models.portfolio import Balance as bl
from investment.utils import fund


class HistoryView(APIView):

    def get(self, request):
        today = datetime.date.today().strftime('%Y-%m-%d')
        port_code = request.query_params.get('portCode')
        date = request.query_params.get('date')
        if not date:
            date = today
        net_asset = bl.objects.filter(port_code=port_code, date__lte=date).last().net_asset
        # 全部调仓费用
        total = ta.objects.filter(port_code=port_code, date__lte=date).aggregate(total=Sum('fee'))['total']

        # 最近调仓日期
        last = ta.objects.filter(
            port_code=port_code, date__lte=date, operation__icontains='成交确认'
        ).aggregate(date=Max('date'))['date']
        exact = ta.objects.filter(port_code=port_code, date=last).aggregate(total=Sum('fee'))['total']

        turn_over = self.turn_over(port_code)
        return Response({
            'total': {'fee': total, 'ratio': total / net_asset},
            'last': {'fee': exact, 'ratio': exact / net_asset},
            'date': last,
            'turn_over': turn_over
        })

    @staticmethod
    def post(request):
        """组合交易记录，只保留成交记录"""
        finish = ['开放式基金申购成交确认', '开放式基金赎回成交确认', '开放式基金转换转出成交确认', '开放式基金转换转入成交确认']
        port_code = request.data.get('portCode')
        records = ta.objects.filter(port_code=port_code, operation__in=finish).order_by('date').all()
        funds = list(set([x.secucode for x in records]))
        names = fund.fund_names(funds)
        ret = []
        count = 1
        date_filter = []
        name_filter = []
        operation_filter = ['申购', '赎回', '转入', '转出']
        for r in records:
            if r.operation == '开放式基金申购成交确认':
                h = {'operation': '申购', 'cap': - r.operation_amount}
            elif r.operation == '开放式基金赎回成交确认':
                h = {'operation': '赎回', 'cap': r.operation_amount + r.fee}
            elif r.operation == '开放式基金转换转出成交确认':
                h = {'operation': '转出', 'cap': r.order_value * r.order_price}
            else:
                h = {'operation': '转入', 'cap': r.order_value * r.order_price + r.fee}
            name = names.get(r.secucode)
            h.update({
                'secucode': r.secucode, 'date': r.date, 'price': r.order_price, 'amount': r.order_value,
                'fee': r.fee, 'secuname': name, 'key': count
            })
            ret.append(h)
            name_filter.append(name)
            date_filter.append(r.date)
            count += 1
        name_filter = [{'text': x, 'value': x} for x in sorted(set(name_filter))]
        date_filter = [{'text': x, 'value': x} for x in sorted(set(date_filter))]
        operation_filter = [{'text': x, 'value': x} for x in operation_filter]

        return Response(
            {'data': ret, 'filter': {'operation': operation_filter, 'name': name_filter, 'date': date_filter}}
        )

    @staticmethod
    def turn_over(port_code):
        """计算换手率"""
        finish = ['开放式基金申购成交确认', '开放式基金赎回成交确认', '开放式基金转换转出成交确认', '开放式基金转换转入成交确认']
        records = ta.objects.filter(port_code=port_code, operation__in=finish).order_by('date').all()
        cap = 0
        for r in records:
            if r.operation == '开放式基金申购成交确认':
                cap += - r.operation_amount
            elif r.operation == '开放式基金赎回成交确认':
                cap += r.operation_amount
            elif r.operation == '开放式基金转换转出成交确认':
                cap += r.order_value * r.order_price
            else:
                cap += r.order_value * r.order_price + r.fee
        # 获取期初和期末平均资产
        dates = bl.objects.filter(port_code=port_code).aggregate(min=Min('date'), max=Max('date'))
        dates = [dates['min'], dates['max']]
        asset = bl.objects.filter(port_code=port_code, date__in=dates).aggregate(avg=Avg('net_asset'))['avg']
        turn_over = cap / asset
        return turn_over
