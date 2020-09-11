"""
commit
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-07
@desc:
"""

from django.db.transaction import atomic
from sql.commit.index import commit_basic_info, commit_index_quote, commit_basic_info_wind, commit_index_quote_wind


def commit_index_gil():
    """指数数据-聚源"""
    with atomic():
        commit_basic_info()
        commit_index_quote()


def commit_index_wind():
    """指数数据-万得"""
    with atomic():
        commit_basic_info_wind()
        commit_index_quote_wind()


def commit_index():
    """指数数据-聚源、万得"""
    with atomic():
        commit_basic_info()
        commit_index_quote()
        commit_basic_info_wind()
        commit_index_quote_wind()


__all__ = ['commit_index', 'commit_index_gil', 'commit_index_wind']
