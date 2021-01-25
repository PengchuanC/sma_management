
class AuthRouter(object):
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """
    route_app_labels = {'auth', 'contenttypes', 'sessions'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to default db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to default db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'default' database.
        """
        if app_label in self.route_app_labels:
            return db == 'default'
        return None


class Router(object):
    @staticmethod
    def db_for_read(model, **hints):
        """读取使用备库"""
        return 'default'

    @staticmethod
    def db_for_write(model, **hints):
        """写入使用主库"""
        return 'default'

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        """是否运行关联操作"""
        return True
