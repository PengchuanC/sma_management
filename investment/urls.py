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
    path('basic/all/', views.BasicInfo.as_view()),
    path('basic/capital/', views.Capital.as_view()),
    path('history/summary/', views.HistoryView.as_view()),
    path('analysis/performance/', views.PerformanceView.as_view()),
    path('analysis/attribute/', views.AttributeChartView.as_view()),
    path('analysis/fundholding/', views.FundHoldingView.as_view()),
    path('analysis/fundholding/stock/', views.FundHoldingStockView.as_view()),
    path('overview/', views.OverviewView.as_view()),

    path('test/', views.TestViews.as_view()),
    path('mvo/index/', views.IndexInfoViews.as_view()),
    path('mvo/optimize/', views.MvoViews.as_view()),
    path('backtest/', views.BackTestView.as_view()),
    path('backtest/download/', views.BackTestView.download),
    path('backtest/weight/', views.BacktestWeightView.as_view()),
    path('backtest/weight/download/', views.BacktestWeightView.download),
]
