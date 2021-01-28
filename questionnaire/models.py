from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


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

    @property
    def choices(self):
        return Choices.objects.filter(question_id=self.question_id).all()


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


# 客户信息
class Client(models.Model):
    name = models.CharField(verbose_name="客户名称", max_length=20)
    account = models.CharField(verbose_name="客户账号", max_length=30, unique=True)
    associate_name = models.CharField(verbose_name="关联账户名称", max_length=20, null=True, blank=True)
    associate_account = models.CharField(verbose_name="关联账号", max_length=30, null=True, blank=True)
    mobile = models.CharField(verbose_name='手机号码', max_length=11, null=True, blank=True)

    class Meta:
        db_table = 'questionnaire_clients'
        verbose_name = '客户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 问卷答案信息
class ResultInfo(models.Model):
    client = models.ForeignKey(Client, to_field='account', on_delete=models.CASCADE)
    date = models.DateField(verbose_name="签署日期", null=False)
    sales = models.CharField(verbose_name="销售人员", max_length=20, null=False)

    class Meta:
        db_table = 'questionnaire_result_info'
        verbose_name = '问卷回答信息'
        verbose_name_plural = verbose_name
        unique_together = ('client', 'date')

    def __str__(self):
        return self.client.name

    def score(self):
        results = Result.objects.filter(info=self).all()
        points = 0
        for r in results:
            point = Choices.objects.get(question_id=r.question_id, choice_id=r.choice_id).point
            points += point
        return points

    def rank(self):
        point = self.score()
        if point <= 23:
            r = 'S1'
        elif 24 <= point <= 32:
            r = 'S2'
        elif 33 <= point <= 45:
            r = 'S3'
        elif 46 <= point <=56:
            r = 'S4'
        else:
            r = 'S5'
        return r


# 问卷答案
class Result(models.Model):
    info = models.ForeignKey(ResultInfo, related_name='info', on_delete=models.CASCADE)
    question_id = models.IntegerField(verbose_name='问题ID', null=False)
    choice_id = models.IntegerField(verbose_name='选项ID', null=False)

    class Meta:
        db_table = 'questionnaire_result'
        verbose_name = '问卷回答选项'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.info.client.name

    def question(self):
        return Questions.objects.get(question_id=self.question_id)

    def choice(self):
        return Choices.objects.get(question_id=self.question_id, choice_id=self.choice_id)
