import pandas as pd

from rpc import models

from rpc.services import funds_pb2 as pb


@models.async_database
async def fund_category_new(request: pb.FundCategoryRequest, context):
    """新的基金分类"""
    funds = request.fund
    kind = request.kind
    c = models.Classify
    kind = c.c.classify if kind == '2' else c.c.branch
    if funds:
        sql = models.sa.select([c.c.secucode_id, kind]).where(c.c.secucode_id.in_(funds)).distinct()
    else:
        sql = models.sa.select([c.c.secucode_id, kind])
    funds = await models.database.fetch_all(sql)
    data = [pb.FundCategory(secucode=x[0], category=x[1]) for x in funds]
    return pb.FundCategoryResponse(status_code=0, data=data)


@models.async_database
async def fund_basic_info(request: pb.FundBasicInfoRequest, context):
    bi = models.BasicInfo
    sql = models.sa.select([bi.c.secucode_id, bi.c.launch_date]).distinct()
    query = await models.database.fetch_all(sql)
    ret = [pb.BasicInfo(secucode=x[0], launch_date=x[1].strftime('%Y-%m-%d')) for x in query]
    return pb.FundBasicInfoResponse(data=ret)


@models.async_database
async def portfolio_core(request, context):
    """获取筛选系统核心池"""
    m = models.PortfolioExpand
    max_date = models.sa.select([models.sa.func.max(m.c.update_date)])
    sql = models.sa.select(
        [m.c.secucode]).where(m.c.update_date == max_date).where(m.c.port_type.in_([2, 3, 4])).distinct()
    funds = await models.database.fetch_all(sql)
    funds = [f[0] for f in funds]
    resp = pb.FundsResponse(funds=funds)
    return resp
