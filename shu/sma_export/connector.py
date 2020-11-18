
from sqlalchemy import create_engine
from pandas import read_sql

from shu.sma_export.parse_configs import configs


def database_params():
    return configs['database']


def engine_maker(host, port, username, password, database):
    uri = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4'
    engine = create_engine(uri)
    return engine


def sql_executor(sql, conn=None):
    if not conn:
        conn = engine_maker(**database_params())
    data = read_sql(sql, con=conn)
    return data
