"""
run
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc: 导出数据
"""

from shu.sma_export.run import execute
from shu.to_database import run


def shu_commit():
    execute()
    run()
