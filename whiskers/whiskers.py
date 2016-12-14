import importlib
import os
import sys

import rethinkdb as r
from rethinkdb.errors import ReqlRuntimeError
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.python import log

from whiskers.context import ApplicationContext
from whiskers.data import DBManager
from whiskers.options import CommandLineOptions
from whiskers.ws_ddp_server import WsDDPServer
from whiskers.ws_web_server import WebServer

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
        # self.server_classes = [WsDDPServer, WebServer]
        self.servers = [WsDDPServer(), WebServer()]
        self.options = CommandLineOptions()

        self.settings = ApplicationContext()

        self.db = DBManager()
        self.db_conn = None

        self.project_path = None


    @inlineCallbacks
    def setup(self, name, host):
        self.gather_options()

        self.settings.add('name', name)
        self.setup_parse_host(host)

        # import the settings file specified by the user
        settings_module = self.options.get("settings")
        settings = importlib.import_module(settings_module)

        # get a default project directory based on the location of the settings.py file
        # and assume this is the top level dir of the project.
        # This can be specified and overridden in the settings file
        # use this assumption to import necessary files/dirs
        settings_path = os.path.abspath(settings_module)
        project_dir = os.path.dirname(settings_path)
        project_home = getattr(settings, 'project_home', project_dir)
        self.setup_project_files(project_home)

        # add project_home to this whiskers instance settings context
        self.settings.add('project_home', project_home)

        # set up the db connection between this whiskers instance and rethink
        # not associated with the client connection pool
        connection_host = settings.db['host']
        connection_port = settings.db['port']
        yield self.setup_db_conn(name, connection_host, connection_port)


    @inlineCallbacks
    def setup_db_conn(self, name, host, port):
        # connection_args will hold the key, value pairs that all db connections will use. If changes are necessary, they
        # can be made on a per use basis
        connection_args = {'host': host, 'port': port}
        connection_args.update({'db': name})
        self.settings.add('connection_args', connection_args)

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

    def setup_project_files(self, project_home):

        # TODO make this client stuff dynamic eventually
        # client folder will hold all types of files sent to the client
        client_folder = os.path.join(project_home, 'client')
        self.settings.add('client_dir', client_folder)

    def setup_parse_host(self, host):
        port = 8000

        if ':' in host:
            port = int(host.split(":")[-1])
            host = host.replace(":%s" % port, "")

        self.settings.add('host', host)
        self.settings.add('port', port)

        # could change later
        self.settings.add("ddp_port", 8030)


    def run(self, name, host=u"127.0.0.1"):
        self.setup(name, host)

        log.startLogging(sys.stdout)

        for server in self.servers:
            # server = server_cls()
            server.setup(self.settings)

        reactor.run()

    def gather_options(self):
        """
        These will setup the default options and default values that whiskers will look for to use.
        Current options are:
            - settings (-s or --settings)
        """
        self.options.parser.add_argument("--settings",
                                         type=str,
                                         default="settings.py",
                                         help="Specifies the settings file for whiskers to use"
                                         )


    def publish(self, name):
        """
        All data that users can access should only be accessible if published here first.
        :param name:
        :return:
        """
        pass

    def add_tables(self, table_list):
        """
        This method hides the DB manager from the user.

        Still need to get *args, **kwargs passed through

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