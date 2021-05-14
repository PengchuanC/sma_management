import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sma_management.settings")
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
django.setup()


from cta_fof import models
