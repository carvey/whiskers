import importlib
import sys

import rethinkdb as r
from rethinkdb.errors import ReqlRuntimeError

from whiskers.context import app

r.set_loop_type('twisted')

from twisted.python import log
from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def setup(name):

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
    app.add('db_conn', conn)

    # set up the database for this app
    try:
        yield r.db_create(name).run()
    except ReqlRuntimeError:
        pass

    conn.use(name)
    connection_args.update({'db': name})

    # ensure the db tables are set up
    data = importlib.import_module('data')
    db_manager = data.db

    app.add('db_manager', db_manager)
    app.add('connection_args', connection_args)

    importlib.import_module('main')


def run(name, host=u"ws://127.0.0.1:9000"):
    setup(name)

    log.startLogging(sys.stdout)

    from whiskers.wsocketserver import ServerProtocol, ServerFactory
    from autobahn.twisted.websocket import listenWS
    from twisted.internet import reactor

    factory = ServerFactory(host)
    factory.protocol = ServerProtocol
    factory.setProtocolOptions(autoPingInterval=15, autoPingTimeout=3)

    listenWS(factory)
    reactor.run()

