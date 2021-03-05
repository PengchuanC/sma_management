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
    path('basic/announcement/', views.AnnouncementViews.as_view()),
    path('basic/quarter/', views.ProfitAttribute.quarter),
    path('basic/profit/', views.ProfitAttribute.profit),
    path('basic/pr/', views.PurchaseAndRansom.as_view()),

    path('history/summary/', views.HistoryView.as_view()),
    path('analysis/performance/', views.PerformanceView.as_view()),
    path('analysis/attribute/', views.AttributeChartView.as_view()),
    path('analysis/fundholding/', views.FundHoldingView.as_view()),
    path('analysis/fundholding/stock/', views.FundHoldingStockView.as_view()),
    path('analysis/style/', views.StyleAnalysis.as_view()),
    path('analysis/expose/', views.ExposureAnalysis.as_view()),
    path('analysis/brinson/', views.BrinsonAnalysis.as_view()),
    path('analysis/std/', views.MovingVolatility.as_view()),

    path('overview/', views.OverviewView.as_view()),
    path('overview/allocate/', views.OverviewView.asset_allocate),
    path('overview/allocate/avg/', views.OverviewView.avg_asset_allocate),
    path('overview/pos/', views.fund_position),
    path('overview/questionnairy/', views.OverviewView.question),
    path('overview/compare/', views.OverviewView.pre_valuation_compare_real),

    path('warehouse/portfolio/', views.SimpleEmuView.get_portfolio),
    path('warehouse/portfolio/cash/', views.SimpleEmuView.get_portfolio_cash),
    path('warehouse/complex/', views.ComplexEmuView.as_view()),
    path('warehouse/complex/bulk/', views.ComplexEmuBulkView.as_view()),
    path('warehouse/complex/download/', views.ComplexEmuView.download),
    path('warehouse/complex/holding/', views.ComplexEmuView.fund_holding_ratio_http),
    path('warehouse/fundlist/', views.SimpleEmuView.get_funds),
    path('warehouse/fundnav/', views.SimpleEmuView.get_fund_nav),
    path('warehouse/history/', views.SimpleEmuView.get_trading_history),
    path('warehouse/ransom/', views.SimpleEmuView.get_ransom_fee),
    path('warehouse/purchase/', views.SimpleEmuView.get_purchase_fee),

    path('test/', views.TestViews.as_view()),

    path('mvo/index/', views.IndexInfoViews.as_view()),
    path('mvo/optimize/', views.MvoViews.as_view()),
    path('backtest/', views.BackTestView.as_view()),
    path('backtest/download/', views.BackTestView.download),
    path('backtest/index/', views.BackTestIndexView.as_view()),
    path('backtest/weight/', views.BacktestWeightView.as_view()),
    path('backtest/weight/download/', views.BacktestWeightView.download),

    path('mock/date/', views.change_date),
    path('mock/detail/', views.change_detail),
    path('mock/', views.mock),

    path('capital/', views.CapitalFlowView.as_view()),
    path('capital/category/', views.CapitalFlowView.category),
]
