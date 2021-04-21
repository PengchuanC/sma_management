import sqlalchemy as sa
import datetime
from dateutil.relativedelta import relativedelta
from databases import Database
from functools import wraps

from fund_back_django.settings import DATABASES


def get_uri(name: str = None):
    name = name or 'default'
    c = DATABASES[name]
    uri_ = f"mysql://{c['USER']}:{c['PASSWORD']}@{c['HOST']}:{c['PORT']}/{c['NAME']}?charset=utf8mb4"
    return uri_


uri = get_uri()
database = Database(uri)
metadata = sa.MetaData()
engine = sa.create_engine(uri)
time_record = datetime.datetime.now()


def async_database(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        now = datetime.datetime.now()
        global time_record
        delta = relativedelta(now, time_record)
        status = database.is_connected
        if delta.hours >= 2:
            if status:
                print('重启数据库连接')
                await database.disconnect()
                await database.connect()
                time_record = now
        if not status:
            print('数据库连接已断开')
            await database.connect()
            time_record = now
        ret = await func(*args, **kwargs)
        return ret
    return inner
