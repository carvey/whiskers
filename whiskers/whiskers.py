import importlib
import sys

import rethinkdb as r
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.python import log

from whiskers.context import ApplicationContext
from whiskers.data import RethinkBasic
from whiskers.ws_ddp_server import DDPProtocol, DDPServerFactory
r.set_loop_type('twisted')

class DDPServer():

    def __init__(self, *args, **kwargs):
        """
        By default, whiskers will start with the following servers activated:
            - A DDP server with a live rethinkdb backend
            - web server?

            How to best dynamic servers to work together?
        :return:
        """
        self.methods = {}

        # settings object for this instance
        self.settings = ApplicationContext()

        # add necessary settings
        port = kwargs.pop('port', 3000)
        self.settings.add('port', port)

        db_host = kwargs.pop('db_host', 'localhost')
        db_port = kwargs.pop('db_port', '28015')
        self.settings.add('db_connection_args', {
            'host': db_host,
            'port': db_port
        })


        self.db = RethinkBasic(self.settings)

        self.factory = DDPServerFactory(self.settings, self.methods)

    # @inlineCallbacks
    def run(self):
        log.startLogging(sys.stdout)

        self.db.db_connect(self.settings)
        self.factory.methods = self.methods
        self.factory.listen()

        reactor.run()

    def publish(self, collections):
        """
        All data that users can access should only be accessible if published here first.
        :param collections: Can be a string or list of the collections to publish
        :return:
        """
        if isinstance(collections, list):
            for collection in collections:
                self.factory.pubs.append(collection)

        else:
            self.factory.pubs.append(collections)

    def add_tables(self, table_list):
        """
        This method hides the DB manager from the user.

        Still need to get *args, **kwargs passed through

        :param table_list:
        :return:
        """
        self.db.add_tables(table_list)

