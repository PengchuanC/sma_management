
class Router(object):
    @staticmethod
    def db_for_read(model, **hints):
        return 'slave'

    @staticmethod
    def db_for_write(model, **hints):
        return 'default'
