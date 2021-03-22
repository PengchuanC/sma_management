"""
run
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc: 导出数据
"""

from shu.sma_export.run import execute
from shu.to_database import run
from shu.local_files import transaction


def shu_commit():
    execute()
    run()
    transaction.commit_transaction()
    transaction.commit_holding()
