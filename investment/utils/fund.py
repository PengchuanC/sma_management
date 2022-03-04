"""
单只基金相关的功能
"""
import re

from asgiref.sync import sync_to_async

from investment.models import Funds, Security
from rpc.fund_screen_client import Client


def fund_names(funds):
    """获取基金名称"""
    query_ret = Funds.objects.filter(secucode__in=funds).all()
    ret = {x.secucode: x.secuname for x in query_ret}
    query_ret = Security.objects.filter(secucode__in=funds).all()
    ret.update({x.secucode: re.sub(r'[(私募基金)|(私募证券投资基金)|(集合资产管理计划)]', '', x.secuabbr) for x in query_ret})
    return ret


def fund_is_monetary(fund: str) -> bool:
    """判断基金是否是货币基金

    Args:
        fund: 基金代码

    Returns:
        bool: 是否是货币基金
    """
    fund_type = Client.simple('fund_category', [fund])
    fund_type = fund_type[0]['first']
    return fund_type == '货币型'


async def fund_name_async(funds):
    query_ret = await sync_to_async(Security.objects.filter(secucode__in=funds).all)()
    query_ret = await sync_to_async(list)(query_ret)
    diy = {x.secucode: re.sub(r'[(私募基金)|(私募证券投资基金)|(集合资产管理计划)]', '', x.secuabbr) for x in query_ret}
    query_ret = await sync_to_async(Funds.objects.filter(secucode__in=funds).all)()
    query_ret = await sync_to_async(list)(query_ret)
    ret = {x.secucode: x.secuname for x in query_ret}
    diy.update(ret)
    return diy


def fund_classify(funds: list) -> dict:
    """判断基金是否是货币基金

    Args:
        funds: 基金代码
    """
    fund_type = Client.simple('fund_category', funds)
    ret = {x['secucode']: x['first'] for x in fund_type}
    return ret
