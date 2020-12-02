"""
connector
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-04
@desc:
"""
from sqlalchemy import create_engine
from .configs import gil, datayes


def make_engine(user, password, host, port, database):
    uri = f'oracle+cx_oracle://{user}:{password}@{host}:{port}/{database}'
    return create_engine(uri)


oracle = make_engine(**gil)
datayes = make_engine(**datayes)


__all__ = ['oracle', 'datayes']
