from django.db import models


# 问题
class Questions(models.Model):
    question_id = models.IntegerField(primary_key=True, verbose_name='问题ID')
    subject = models.CharField(verbose_name='主题', null=True, max_length=30)
    text = models.TextField(verbose_name='问题描述', null=False, blank=False)
    date = models.DateTimeField(verbose_name='问题发布日期', null=False, blank=False)

    class Meta:
        db_table = 'questionnaire_questions'
        verbose_name = '问题列表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.question_id}.{self.text}'


# 选项
class Choices(models.Model):
    question_id = models.ForeignKey(Questions, to_field='question_id', on_delete=models.CASCADE)
    choice_id = models.IntegerField(verbose_name='选项ID', null=False, blank=False)
    text = models.TextField(verbose_name='选项描述', null=False, blank=False)
    point = models.IntegerField(verbose_name='选项得分', null=False, blank=False)

    class Meta:
        db_table = 'questionnaire_choices'
        verbose_name = '选项列表'
        verbose_name_plural = verbose_name
        unique_together = ('question_id', 'choice_id')

    def __str__(self):
        return self.text
