import sys

import rethinkdb as r
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from autobahn.twisted.websocket import listenWS
from twisted.internet.defer import inlineCallbacks, Deferred

from PythonDDPClient.src.message import *
from whiskers.client import Client
from whiskers.ddp import DDPHandlers
from whiskers.publications import PubSubManager

# log.startLogging(sys.stdout)

class DDPProtocol(WebSocketServerProtocol, PubSubManager, DDPHandlers):

    def onConnect(self, request):
        # print("Client connecting: %s" % request.peer)
        pass

    # @inlineCallbacks
    def onOpen(self):
        # self.sendMessage("Welcome!".encode("utf8"))
        # self.factory.register_client(self)
        #
        # yield self.factory.connectionReady(self)
        # yield self.notice_changes(self.factory.clients[self], 'a', 'b')
        pass

    def onMessage(self, payload, isBinary):
        """
        Can be used to respond to requests from client -> DDP or WAMP maybe
        :param payload:
        :param isBinary:
        :return:
        """

        # detect message type and offload to the appropriate message handlers
        payload = Message.resolve_message(payload.decode('utf8'))

        # if there is a msg present, determine the type
        if hasattr(payload, "msg"):
            msg = payload.msg

            if msg == 'connect':
                self.handle_connect(payload, db_connection_args=DDPProtocol.db_connection_args)

            elif msg == 'sub':
                self.handle_sub(payload)

        print("TXT: %s" % payload)

    def onClose(self, wasClean, code, reason):
        # print("Websocket connection closed: %s" % reason)
        self.factory.unregister_client(self)


class DDPServerFactory(WebSocketServerFactory):

    def __init__(self, settings, *args, **kwargs):
        url = self.build_url(settings)
        super(DDPServerFactory, self).__init__(url, *args, **kwargs)

        self.protocol = DDPProtocol
        self.setProtocolOptions(autoPingInterval=15, autoPingTimeout=3)

    # @inlineCallbacks
    def listen(self):
        listenWS(self)

    def build_url(self, settings):
        host = "localhost"
        port = settings.port

        return "ws://%s:%s" % (host, port)

    def register_client(self, client_proto, db_connection_args):
        client = Client(client_proto)
        client.proto = client_proto

        if not hasattr(self, 'clients'):
            self.clients = {}

        if client_proto not in self.clients:
            conn = r.connect(**db_connection_args)
            client.conn = conn
            self.clients[client_proto] = client

            print("Registered client: %s" % client.proto.peer)

    def unregister_client(self, client_proto):
        if hasattr(self, 'clients'):
            if client_proto in self.clients:
                self.clients[client_proto].conn.close()
                del self.clients[client_proto]

            print("Unregistered client: %s" % client_proto)

    @inlineCallbacks
    def connectionReady(self, client_proto):
        client = self.clients[client_proto]

        if isinstance(client.conn, Deferred):
            client.conn = yield client.conn


