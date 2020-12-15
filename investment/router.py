
class Router(object):
    @staticmethod
    def db_for_read(model, **hints):
        """读取使用备库"""
        return 'slave'

    @staticmethod
    def db_for_write(model, **hints):
        """写入使用主库"""
        return 'default'

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        """是否运行关联操作"""
        return True
