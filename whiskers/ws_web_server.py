import sys

from autobahn.twisted.resource import WebSocketResource
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from whiskers.publications import PubSubManager

log.startLogging(sys.stdout)

class WebServer(WebSocketServerProtocol, PubSubManager):

    def setup(self, settings):
        # factory = WebSocketServerFactory(settings.host)
        # factory.protocol = WebServer
        #
        # resource = WebSocketResource(factory)
        #
        # # we server static files under "/" ..
        root = File(settings.client_dir)
        #
        # # and our WebSocket server under "/ws" (note that Twisted uses
        # # bytes for URIs)
        # root.putChild(b"ws", resource)

        # both under one Twisted Web Site
        site = Site(root)

        reactor.listenTCP(8000, site)


# class ServerFactory(WebSocketServerFactory, ClientRegistration):
#     pass