"""
url
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-07
@desc:
"""

from django.urls import path

from investment import views


urlpatterns = [
    path('test/', views.TestViews.as_view()),
    path('mvo/index/', views.IndexInfoViews.as_view()),
    path('mvo/optimize/', views.MvoViews.as_view()),
]
