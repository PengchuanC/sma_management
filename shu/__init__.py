"""
__init__.py
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""
import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sma_management.settings")
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
django.setup()


from investment import models
