import sys

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from twisted.python import log

from PythonDDPClient.src.message import *
from whiskers.client_registration import ClientRegistration
from whiskers.ddp import DDPServer
from whiskers.publications import PubSubManager

log.startLogging(sys.stdout)

class WsDDPServer(WebSocketServerProtocol, PubSubManager, DDPServer):

    def setup(self, settings):
        """
        Setup
        :param host:
        :return:
        """
        from autobahn.twisted.websocket import listenWS

        # register_client call will need the connection args setting
        self.connection_args = settings.connection_args

        factory = ServerFactory(settings.host)
        factory.protocol = WsDDPServer
        factory.setProtocolOptions(autoPingInterval=15, autoPingTimeout=3)

        listenWS(factory)

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
        # if isBinary:
        #     print("BIN: %s bytes" % len(payload))
        # else:
        #     print("TEXT: %s" % payload.decode("UTF-8"))

        # detect message type and offload to the appropriate message handlers
        payload = Message.resolve_message(payload.decode('utf8'))

        # if there is a msg present, determine the type
        if hasattr(payload, "msg"):
            msg = payload.msg

            if msg == 'connect':
                self.handle_connect(payload, connection_args=self.connection_args)

            elif msg == 'sub':
                self.handle_sub(payload)

        print("TXT: %s" % payload)


    def onClose(self, wasClean, code, reason):
        # print("Websocket connection closed: %s" % reason)
        self.factory.unregister_client(self)

class ServerFactory(WebSocketServerFactory, ClientRegistration):
    pass


