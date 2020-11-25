from django.urls import path

from investment.views import prev_valuation

websocket_urlpatterns = [
    path(r'ws/prevaluation/', prev_valuation.PreValuationConsumer.as_asgi()),
]
