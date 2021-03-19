from rpc import models

from rpc.services import funds_pb2 as pb


def fund_category(request: pb.FundCategoryRequest, context):
    funds = request.fund
    funds = [f+'.OF' for f in funds]
    latest = models.Classify.objects.latest('update_date').update_date
    funds = models.Classify.objects.filter(update_date=latest, windcode__in=funds)
    data = [pb.FundCategory(secucode=x.windcode.windcode[:6], category=x.classify) for x in funds]
    return pb.FundCategoryResponse(status_code=0, data=data)
