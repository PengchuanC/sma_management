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


@admin.register(models.IndexComponent)
class IndexComponentAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'stockcode', 'weight', 'date')


@admin.register(models.Vouchers)
class VouchersAdmin(admin.ModelAdmin):
    list_display = ('id', 'port_code', 'digest', 'code', 'value', 'date')
    list_filter = ('port_code', 'digest', 'code', 'date')


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
    list_per_page = 60


@admin.register(models.FundPurchaseAndRedeem)
class FundPurchaseAndRedeemAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'apply_type', 'redeem_type', 'min_apply', 'max_apply')
    search_fields = ('secucode__secucode', )


@admin.register(models.FundHoldingStock)
class FundHoldingStockAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'stockcode', 'stockname', 'serial', 'ratio', 'publish', 'date')
    search_fields = ('secucode__secucode',)


@admin.register(models.FundPurchaseFee)
class FundPurchaseFeeAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'operate', 'low', 'high', 'fee')


@admin.register(models.FundAssociate)
class FundAssociateAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'relate')


@admin.register(models.FundAssetAllocate)
class FundAssetAllocateAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'stock', 'bond', 'fund', 'metals', 'monetary', 'other', 'date')


@admin.register(models.FundAnnouncement)
class FundAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'secuabbr', 'date', 'title', 'content')


@admin.register(models.FundAdvisor)
class FundAdvisorAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'advisorcode', 'advisorname')


@admin.register(models.FundPosEstimate)
class FundPosEstimateAdmin(admin.ModelAdmin):
    list_display = ('normal_stock', 'mix_stock', 'mix_equal', 'mix_flexible', 'date')


# 组合部分
@admin.register(models.Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('id', 'port_code', 'port_name', 'port_type', 'benchmark', 't_n', 'settlemented')
    list_filter = ('port_type', 'benchmark', 't_n', 'settlemented')
    list_display_links = ('port_code',)


@admin.register(models.PortfolioExpanded)
class PortfolioExpandedAdmin(admin.ModelAdmin):
    list_display = ('id', 'port_code', 'init_money', 'activation', 'fund_id', 'launch')
    list_display_links = ('port_code',)


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'chiname', 'identify_', 'mobile_', 'gender', 'role')
    list_filter = ('gender', 'role')
    list_display_links = ('username',)

    def identify_(self, m: models.User):
        return m.real_identify_no

    def mobile_(self, m: models.User):
        return m.real_mobile

    identify_.short_description = '身份证ID'
    mobile_.short_description = '手机号码'


@admin.register(models.NomuraOISales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'telephone', 'email')
    list_display_links = ('username',)


@admin.register(models.ProductUserMapping)
class ProductUserMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'port_code', 'holder')
    list_filter = ('port_code', 'holder')


@admin.register(models.ProductSalesMapping)
class ProductSalesMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'port_code', 'sales')
    list_filter = ('port_code', 'sales')


@admin.register(models.Valuation)
class ValuationAdmin(admin.ModelAdmin):
    list_display = ('id', 'port_code', 'date', 'asset', 'debt', 'net_asset', 'unit_nav', 'accu_nav', 'nav_increment')
    list_filter = ('port_code', 'date')
    list_display_links = ('id', 'port_code')


@admin.register(models.ValuationEx)
class ValuationExAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'port_code', 'date', 'savings', 'settlement_reserve', 'deposit', 'stocks', 'bonds', 'abs', 'funds',
        'metals', 'other', 'resale_agreements', 'purchase_rec', 'ransom_pay'
    )
    list_filter = ('port_code', 'date')
    list_display_links = ('id', 'port_code')


@admin.register(models.ValuationBenchmark)
class BenchmarkAdmin(admin.ModelAdmin):
    list_display = ['port_code', 'unit_nav', 'date']
    list_filter = ('port_code', 'date')


@admin.register(models.Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'port_code', 'date', 'unit_nav', 'net_asset_chg', 'total_net_asset_chg', 'unit_nav_chg'
    )
    list_filter = ('port_code', 'date')
    list_display_links = ('id', 'port_code')


@admin.register(models.IncomeEx)
class IncomeExAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'port_code', 'date', 'total', 'today_total', 'equity', 'today_equity', 'fix_income', 'today_fix_income',
        'alternative', 'today_alternative', 'monetary', 'today_monetary', 'fare', 'today_fare', 'other', 'today_other'
    )
    list_filter = ('port_code', 'date')
    list_display_links = ('id', 'port_code')


@admin.register(models.Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'port_code', 'date', 'secucode', 'market', 'begin_shares', 'current_shares', 'mkt_cap', 'today_fare',
        'fare', 'today_dividend', 'dividend', 'today_profit', 'profit'
    )
    list_filter = ('port_code', 'date', 'secucode', 'market')
    list_display_links = ('id', 'port_code')


@admin.register(models.Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'port_code', 'date', 'operation', 'operation_flag', 'secucode', 'entrust_quantity', 'entrust_price',
        'busin_quantity', 'occur_amount', 'subject_amount', 'fare', 'note', 'market'
    )
    list_filter = ('port_code', 'date', 'operation', 'secucode')
    list_display_links = ('id', 'port_code')


@admin.register(models.PurchaseAndRansom)
class PurchaseAndRansomAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'port_code', 'date', 'confirm', 'pr_quantity', 'pr_amount', 'rs_quantity', 'rs_amount', 'pr_fee_backend',
        'rs_fee', 'rs_fee_org', 'org_name'
    )
    list_filter = ('port_code', 'date', 'confirm', 'org_name')
    list_display_links = ('id', 'port_code')


@admin.register(models.PortfolioStyle)
class PortfolioStyleAdmin(admin.ModelAdmin):
    list_display = (
        'port_code', 'small_value', 'small_growth', 'mid_value', 'mid_growth',
        'large_growth', 'bond', 'r_square', 'date'
    )
    list_filter = ('port_code', 'date')


@admin.register(models.PortfolioBrinson)
class PortfolioBrinsonAdmin(admin.ModelAdmin):
    list_display = ('port_code', 'index', 'date', 'industry', 'q1', 'q2', 'q3', 'q4')


@admin.register(models.ClientQ)
class ClientQAdmin(admin.ModelAdmin):
    list_display = (
        'port_code', 'risk', 'maturity', 'arr', 'volatility', 'fluidity', 'age', 'experience', 'plan', 'tolerance',
        'alter_limit', 'cross_border_limit'
    )


@admin.register(models.PreValuedNav)
class PreValueNavAdmin(admin.ModelAdmin):
    list_display = ('port_code', 'date', 'value')


@admin.register(models.ClientPR)
class ClientPRAdmin(admin.ModelAdmin):
    list_display = (
        'port_code', 'purchase_amount', 'ransom_share', 'p_open_date'
        , 'r_open_date', 'p_confirm', 'r_confirm', 'complete'
    )


@admin.register(models.PortfolioAssetAllocate)
class PortfolioAllocateAdmin(admin.ModelAdmin):
    list_display = ('port_code', 'equity', 'fix_income', 'alter', 'money', 'other', 'date')
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


@admin.register(models.StockExpose)
class StockExposeAdmin(admin.ModelAdmin):
    list_display = (
        'secucode', 'date', 'beta', 'momentum', 'size', 'earnyild', 'resvol', 'growth', 'btop',
        'leverage', 'liquidty', 'sizenl'
    )


@admin.register(models.StockDailyQuote)
class StockDailyQuoteAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'closeprice', 'prevcloseprice', 'date')


@admin.register(models.CapitalFlow)
class CapitalFlowAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'date', 'buyvalue', 'sellvalue', 'netvalue')


@admin.register(models.ObservePool)
class ObservePoolAdmin(admin.ModelAdmin):
    list_display = ('secucode', )


@admin.register(models.ImportantHolding)
class ImportantHoldingAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'secuname', 'important', 'style', 'flag')
    list_filter = ('important', 'style', 'flag')


@admin.register(models.SecurityDividend)
class SecurityDividend(admin.ModelAdmin):
    list_display = ('secucode', 'date', 'dividend')
