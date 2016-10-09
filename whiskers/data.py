import rethinkdb as r
from rethinkdb.errors import ReqlOpFailedError

from twisted.internet.defer import inlineCallbacks

class DBManager:

    def __init__(self):
        # this should be the application's db connection and not a user's
        # self.conn = app.db_conn

        # list of registered tables associated with this manager
        self.tables = {}

    @inlineCallbacks
    def add_table(self, name, **kwargs):

        try:
            yield r.table_create(name, **kwargs).run()
        except ReqlOpFailedError:
            pass

        self.tables[name] = r.table(name)
        self.__dict__.update(self.tables)

    def add_tables(self, names):
        for name in names:
            self.add_table(name)

db = DBManager()
