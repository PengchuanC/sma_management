"""
__init__.py
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-11-11
@desc:
"""
import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sma_management.settings")
django.setup()


from investment import models