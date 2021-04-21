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
