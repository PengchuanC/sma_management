import sqlalchemy as sa
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


def async_database(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        status = database.is_connected
        if not status:
            await database.connect()
        ret = await func(*args, **kwargs)
        return ret
    return inner
