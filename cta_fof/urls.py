from django.urls import path

from cta_fof import views


urlpatterns = [
    path('', views.cta_info),
    path('holding', views.holding)
]
