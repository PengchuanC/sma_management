"""
run
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc: 导出数据
@desc: 已废弃
"""

# from shu.sma_export.run import execute
# from shu.to_database import run
from shu.local_files import transaction
from shu.from_sma import commit_sma


def shu_commit():
    commit_sma()
    transaction.commit_transaction()
    transaction.commit_holding()
