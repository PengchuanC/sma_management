"""
announcement
~~~~~~~~~~~~
公募基金公告
"""

from rest_framework.views import APIView, Response
from investment import models


class AnnouncementViews(APIView):

    @staticmethod
    def get(request):
        num = request.query_params.get('num')
        page = request.query_params.get('page')
        if num:
            num = int(num)
        else:
            num = 20
        if page:
            page = int(page)
        else:
            page = 1
        m = models.FundAnnouncement
        ret = m.objects.order_by('-date').values('id', 'secucode', 'secuabbr', 'title', 'date')
        need = ret[(page-1)*num: page*num]
        return Response(need)

    @staticmethod
    def post(request):
        data = request.data
        _id = data.get('id')
        announce = models.FundAnnouncement.objects.get(id=_id)
        content = announce.content
        return Response(content)
