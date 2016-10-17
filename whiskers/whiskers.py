import importlib
import sys

import rethinkdb as r
from rethinkdb.errors import ReqlRuntimeError
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.python import log

from whiskers.context import app
from whiskers.data import DBManager
from whiskers.wsocketserver import WebSocketServer

r.set_loop_type('twisted')

class WhiskersServer():

    def __init__(self):
        """
        By default, whiskers will start with the following servers activated:
            - A DDP server with a live rethinkdb backend
            - web server?

            How to best dynamic servers to work together?
        :return:
        """
        self.servers = [WebSocketServer()]
        self.db = DBManager()

        self.db_conn = None


    @inlineCallbacks
    def setup(self, name):

        settings = importlib.import_module('settings')
        connection_host = settings.db['host']
        connection_port = settings.db['port']

        # connection_args will hold the key, value pairs that all db connections will use. If changes are necessary, they
        # can be made on a per use basis
        connection_args = {'host': connection_host, 'port': connection_port}

        conn = r.connect(**connection_args)
        conn = yield conn

        # set this as the default connection to use
        conn.repl()

        # add this connection to the context
        self.db_conn = conn

        # set up the database for this app
        try:
            yield r.db_create(name).run()
        except ReqlRuntimeError:
            pass

        conn.use(name)
        connection_args.update({'db': name})
        # connection_args is set on 'app' to avoid circular imports with client_registration and this file
        app.add('connection_args', connection_args)


    def run(self, name, host=u"ws://127.0.0.1:9000"):
        self.setup(name)

        log.startLogging(sys.stdout)

        for server in self.servers:
            server.setup(host)

        reactor.run()

    def publish(self, name):
        """
        All data that users can access should only be accessible if published here first.
        :param name:
        :return:
        """
        pass

    def add_tables(self, table_list):
        """
        This method hides the DB manager from the user,
        :param table_list:
        :return:
        """
        self.db.add_tables(table_list)

    def methods(self, methods):
        """
        this should define RPC methods
        :param methods:
        :return:
        """
        pass

Whiskers = WhiskersServer()