"""
@author: chuanchao.peng
@date: 2022/1/10 10:35
@file userprofile.py
@desc: SMA人员信息登记
"""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from investment.models.portfolio import Portfolio
from investment.utils import encrypt


class User(models.Model):
    username = models.CharField(verbose_name='用户昵称', max_length=50, unique=True)
    password = models.CharField(verbose_name='用户密码', max_length=250)
    chiname = models.CharField(verbose_name='用户姓名', max_length=20)
    identify_no = models.CharField(verbose_name='身份证号码', max_length=256)
    mobile = models.CharField(verbose_name='手机号码', max_length=256)
    gender = models.BooleanField(verbose_name='性别', choices=((0, '男性'), (1, '女性')))
    role = models.IntegerField(verbose_name='用户角色', choices=((0, '管理员'), (1, '员工'), (2, '客户')), default=2)

    class Meta:
        db_table = 'user_userprofile'
        verbose_name = '2.1 用户信息登记表（手工增加）'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.chiname

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.password = make_password(self.password, None, 'pbkdf2_sha256')
        self.identify_no = encrypt.encrypt(self.identify_no)
        self.mobile = encrypt.encrypt(self.mobile)
        super(User, self).save(force_insert=force_insert, force_update=force_update, using=using)

    def is_superuser(self):
        return self.role == 0

    def is_employee(self):
        return self.role == 1

    def is_client(self):
        return self.role == 2

    def check_password(self, password: str):
        """校验密码"""
        return check_password(password, self.password)

    @property
    def real_identify_no(self):
        return encrypt.decrypt(self.identify_no)

    @property
    def real_mobile(self):
        return encrypt.decrypt(self.mobile)


class NomuraOISales(models.Model):
    username = models.CharField(verbose_name='销售姓名', max_length=20)
    telephone = models.CharField(verbose_name='联系电话', max_length=20)
    email = models.CharField(verbose_name='电子邮箱', max_length=100)

    class Meta:
        db_table = 'user_sales'
        verbose_name = '2.2 销售人员登记表（手工增加）'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class ProductUserMapping(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='产品代码')
    holder = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE, verbose_name='持有人')

    class Meta:
        db_table = 'sma_user_product_mapping'
        verbose_name = '2.3 用户产品关联表（手工增加）'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


class ProductSalesMapping(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='产品代码')
    sales = models.ForeignKey(NomuraOISales, to_field='id', on_delete=models.CASCADE, verbose_name='FA')

    class Meta:
        db_table = 'sma_sales_product_mapping'
        verbose_name = '2.4 销售产品关联表（手工增加）'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


class UserSmsVerify(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name='用户名称')
    code = models.CharField(max_length=12, verbose_name="验证码", null=False)
    expire = models.DateTimeField(null=False, verbose_name="超时时间")
    tried = models.IntegerField(verbose_name="剩余尝试次数", default=3)

    class Meta:
        db_table = 'user_sms_code'
        verbose_name = '2.5 用户短信验证'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.chiname


class UserLoginLog(models.Model):
    username = models.ForeignKey(User, to_field='username', on_delete=models.CASCADE, verbose_name='用户名称')
    datetime = models.DateTimeField(verbose_name='登陆时间', auto_now_add=True)

    class Meta:
        db_table = 'user_login_log'
        verbose_name = '2.6 用户登陆日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username.chiname
