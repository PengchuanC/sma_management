from django.contrib import admin
from . import models


# 修改后台显示名称
admin.site.site_header = 'SMA投资管理系统'
admin.site.site_title = 'SMA'


# 指数部分
@admin.register(models.Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = ('id', 'secucode', )
    list_display_links = ('secucode',)


@admin.register(models.IndexBasicInfo)
class IndexBasicInfoAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'secuabbr', 'chiname', 'category', 'component', 'source', 'basedate')
    list_filter = ('category', 'source')


@admin.register(models.IndexQuote)
class IndexQuoteAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'pre_close', 'close', 'change', 'date')
    list_filter = ('secucode', )


@admin.register(models.DetailFee)
class DetailFeeAdmin(admin.ModelAdmin):
    list_display = ['port_code', 'management', 'custodian', 'audit', 'interest', 'date']
    list_filter = ['port_code', 'date']


# 基金部分
@admin.register(models.Funds)
class FundsAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'secuname')


@admin.register(models.FundStyle)
class FundStyleAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'fundstyle', 'fundtype')


@admin.register(models.FundPrice)
class FundPriceAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'nv', 'nav', 'acc_nav', 'dailyprofit', 'date')


@admin.register(models.FundAdjPrice)
class FundAdjPriceAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'nav', 'adj_nav', 'date')


@admin.register(models.FundPurchaseAndRedeem)
class FundPurchaseAndRedeemAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'apply_type', 'redeem_type', 'min_apply', 'max_apply')
    search_fields = ('secucode__secucode', )


@admin.register(models.FundHoldingStock)
class FundHoldingStockAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'stockcode', 'stockname', 'serial', 'ratio', 'date')


@admin.register(models.FundPurchaseFee)
class FundPurchaseFeeAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'operate', 'low', 'high', 'fee')


# 组合部分
@admin.register(models.Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'port_code', 'port_name', 'manager', 'init_money', 'purchase_fee', 'redemption_fee', 'base', 'describe',
        'port_type', 'launch_date'
    )
    list_display_links = ('port_code', )


@admin.register(models.Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = (
        'port_code', 'asset', 'debt', 'net_asset', 'shares', 'unit_nav', 'acc_nav', 'savings', 'fund_invest',
        'liquidation', 'value_added', 'profit_pay', 'cash_dividend', 'date'
    )
    list_filter = ('port_code', 'date')


@admin.register(models.BalanceExpanded)
class BalanceExpandedAdmin(admin.ModelAdmin):
    list_display = (
        'port_code', 'dividend_rec', 'purchase_rec', 'redemption_pay', 'redemption_fee_pay', 'management_pay',
        'custodian_pay', 'withholding_pay', 'date'
    )
    list_filter = ('port_code', 'date')


@admin.register(models.Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('port_code', 'unit_nav', 'net_asset', 'change', 'change_pct', 'date')
    list_filter = ('port_code', 'date')


@admin.register(models.IncomeAsset)
class IncomeAssetAdmin(admin.ModelAdmin):
    list_display = ('port_code', 'total_profit', 'equity', 'bond', 'alter', 'money', 'date')
    list_filter = ('port_code', 'date')


@admin.register(models.Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = (
        'port_code', 'secucode', 'holding_value', 'mkt_cap', 'current_cost', 'total_cost', 'fee', 'flow_profit',
        'dividend', 'total_dividend', 'date'
    )
    list_filter = ('port_code', 'secucode', 'date')


@admin.register(models.Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = (
        'port_code', 'secucode', 'amount', 'balance', 'order_price', 'order_value', 'deal_value', 'fee',
        'operation_amount', 'operation', 'subject_name', 'date'
    )
    list_filter = ('port_code', 'secucode', 'operation', 'date')


@admin.register(models.ValuationBenchmark)
class BenchmarkValuationAdmin(admin.ModelAdmin):
    list_display = ('port_code', 'unit_nav', 'date')
    list_filter = ('port_code', 'date')


@admin.register(models.PortfolioStyle)
class PortfolioStyleAdmin(admin.ModelAdmin):
    list_display = (
        'port_code', 'small_value', 'small_growth', 'mid_value', 'mid_growth',
        'large_growth', 'bond', 'r_square', 'date'
    )
    list_filter = ('port_code', 'date')


# 回测部分
@admin.register(models.AssetWeight)
class AssetWeightAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'equity_bound_limit', 'target_risk', 'annual_r', 'risk', 'sharpe', 'hs300', 'zcf', 'qyz', 'hb',
        'zz500', 'hs'
    )
    list_filter = ('date', 'target_risk')


# 股票部分
@admin.register(models.StockIndustrySW)
class StockIndustrySWAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'firstindustryname', 'secondindustryname')


@admin.register(models.StockRealtimePrice)
class StockRealtimePriceAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'prev_close', 'price', 'date', 'time')
