"""
@author: chuanchao.peng
@date: 2021/12/16 13:53
@file logger.py
@desc:
"""

from pathlib import Path

from loguru import logger


download = Path(__file__).parent / 'download'
log = download / 'history.log'

logger.add(log, rotation='512 KB')
