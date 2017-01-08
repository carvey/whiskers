import rethinkdb as r
from rethinkdb.errors import ReqlOpFailedError
from rethinkdb.errors import ReqlRuntimeError

from twisted.internet.defer import inlineCallbacks

class RethinkBasic:

    def __init__(self, settings):
        # this should be the application's db connection and not a user's
        # self.conn = app.db_conn

        # list of registered tables associated with this manager
        self.tables = {}

    @inlineCallbacks
    def db_connect(self, settings):
        conn = r.connect(**settings.db_connection_args)
        conn = yield conn

        # set this as the default connection to use
        conn.repl()

        # add this connection to the context
        settings.add('db_conn', conn)

        # set up the database for this app
        try:
            yield r.db_create('ddp_server').run()
        except ReqlRuntimeError:
            pass

        conn.use('ddp_server')

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
