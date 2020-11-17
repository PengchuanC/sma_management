from django.db.models import Max
from typing import Any


def latest_trading_day(m: Any):
    date = m.objects.latest().date
    return date
