from django.db import connections
from django.db.backends.postgresql import base
from django.db.backends.utils import CursorWrapper

from django_rds_iam_auth.middleware.jwt_exposer import local


class DatabaseWrapper(base.DatabaseWrapper):

    def get_connection_params(self):
        self.settings_dict = connections.databases[local.user_id]
        return super().get_connection_params()

    def make_cursor(self, cursor):
        """Create a cursor without debug logging."""
        return CursorWrapper(cursor, self)

    def pre_connection_trigger(self, connection):
        """Run some logic before connection opening"""
        pass

    def post_connection_trigger(self, connection):
        """Run some logic on just opened connection"""
        pass

    def get_new_connection(self, conn_params):
        self.pre_connection_trigger(conn_params)
        connection = super(DatabaseWrapper, self).get_new_connection(conn_params)
        self.post_connection_trigger(connection)
        return connection
