from django.contrib import admin
from questionnaire.models import Questions, Choices


class ChoicesInline(admin.StackedInline):
    model = Choices


@admin.register(Questions)
class QuestionsAdmin(admin.ModelAdmin):
    inlines = (ChoicesInline, )
    list_display = ('question_id', 'subject', 'text', 'date')
    list_display_links = ('text',)


@admin.register(Choices)
class ChoicesAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'choice_id', 'text', 'point')
    list_display_links = ('text',)
