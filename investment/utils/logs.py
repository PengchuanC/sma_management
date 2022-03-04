"""
@author: chuanchao.peng
@date: 2022/2/28 10:06
@file logs.py
@desc:
"""

from pathlib import Path

from loguru import logger


log = Path(__file__).parent / 'log'
logger.add(log / 'runtime.log', rotation='1 MB')
