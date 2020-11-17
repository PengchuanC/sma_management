import datetime
import pandas as pd

from dateutil.relativedelta import relativedelta


class PeriodData(object):
    def __init__(self, data: pd.DataFrame) -> None:
        self.d = data
        self.date = self.d.index[-1]

    def period(self, years=0, months=0, weeks=0, days=0):
        date = self.date + relativedelta(years=years, months=months, weeks=weeks, days=days)
        dates = [x for x in self.d.index if x <= date]
        if dates:
            date = dates[-1]
        return self.d[self.d.index >= date]

    def ytd(self):
        date = datetime.date(self.date.year, 1, 1)
        dates = [x for x in self.d.index if x <= date]
        date = dates[-1]
        return self.d[self.d.index >= date]


class Performance(object):
    def __init__(self, data):
        self.date = max(data.index)
        self.pd = PeriodData(data)

    def day(self):
        d = self.pd.period(days=-1)
        r = d.agg(change)
        return r

    def week(self):
        d = self.pd.period(days=-7)
        r = d.agg(change)
        return r

    def month(self):
        d = self.pd.period(months=-1)
        r = d.agg(change)
        return r

    def quarter(self):
        d = self.pd.period(months=-3)
        r = d.agg(change)
        return r

    def half_year(self):
        d = self.pd.period(months=-6)
        r = d.agg(change)
        return r

    def year(self):
        d = self.pd.period(years=-1, days=1)
        r = d.agg(change)
        return r

    def ytd(self):
        d = self.pd.ytd()
        r = d.agg(change)
        return r


def change(s: pd.Series):
    return s[-1] / s[0] - 1
