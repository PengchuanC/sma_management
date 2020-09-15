from django.contrib import admin
from questionnaire.models import Questions, Choices, Client, ResultInfo, Result


class ChoicesInline(admin.StackedInline):
    model = Choices


class ResultInline(admin.StackedInline):
    model = Result


@admin.register(Questions)
class QuestionsAdmin(admin.ModelAdmin):
    inlines = (ChoicesInline, )
    list_display = ('question_id', 'subject', 'text', 'date')
    list_display_links = ('text',)


@admin.register(Choices)
class ChoicesAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'choice_id', 'text', 'point')
    list_display_links = ('text',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'account', 'associate_name', 'associate_account')
    list_display_links = ('name',)


@admin.register(ResultInfo)
class ResultInfoAdmin(admin.ModelAdmin):
    list_display = ('client', 'sales', 'date')
    inlines = (ResultInline, )
