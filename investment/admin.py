from django.contrib import admin
from . import models


# 修改后台显示名称
admin.site.site_header = 'SMA投资管理系统'
admin.site.site_title = 'SMA'


@admin.register(models.Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = ('id', 'secucode', )
    list_display_links = ('secucode',)


@admin.register(models.IndexBasicInfo)
class IndexBasicInfoAdmin(admin.ModelAdmin):
    list_display = ('secucode', 'secuabbr', 'chiname', 'category', 'component', 'source', 'basedate')
    list_filter = ('category', 'source')


@admin.register(models.IndexQuote)
class IndexQuote(admin.ModelAdmin):
    list_display = ('secucode', 'pre_close', 'close', 'change', 'date')
    list_filter = ('secucode', )


@admin.register(models.DetailFee)
class DetailFeeAdmin(admin.ModelAdmin):
    list_display = ['port_code', 'management', 'custodian', 'audit', 'date']
    list_filter = ['port_code', 'date']
