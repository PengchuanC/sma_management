"""
run
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""

from threading import Thread

from shu.sma_export.dataset import export, last_trading_day, TABLES, whole_trading_days
from shu.sma_export.shu import concat_path, mk_dirs
from shu.sma_export.parse_configs import special_table_en


class Export(Thread):
    def __init__(self, name, table):
        super().__init__()
        self.name = name
        self.table = table

    def export(self):
        if self.table in special_table_en:
            data = export(self.table)
            file = concat_path(self.name, f'{self.table}.xlsx')
            data.to_excel(file, index=False)
        else:
            latest = last_trading_day()
            dates = whole_trading_days(self.table)
            dates = [x for x in dates if x > latest]
            for date in dates:
                data = export(self.table, date)
                file = concat_path(self.name, f'{self.table}-{date.strftime("%Y%m%d")}.xlsx')
                data.to_excel(file, index=False)

    def run(self):
        self.export()


def execute():
    mk_dirs()
    tasks = []
    for name, table in TABLES.items():
        e = Export(name, table)
        e.start()
        tasks.append(e)

    for e in tasks:
        e.join()
