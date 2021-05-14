from django.contrib import admin
from cta_fof import models


# 修改后台显示名称
admin.site.site_title = 'CTA'


# 组合部分
@admin.register(models.Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'port_code', 'port_name', 'manager', 'init_money', 'port_type', 'launch_date', 'valid'
    )
    list_display_links = ('port_code', )


@admin.register(models.PortfolioExpanded)
class PortfolioExpanded(admin.ModelAdmin):
    list_display = ('port_code', 'o32_code', 'valuation')


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
