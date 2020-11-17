"""
单只基金相关的功能
"""

from investment.models import Funds


def fund_names(funds):
    """获取基金名称"""
    query_ret = Funds.objects.filter(secucode__in=funds).all()
    ret = {x.secucode: x.secuname for x in query_ret}
    return ret
