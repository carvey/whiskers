import sys

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from twisted.python import log

from whiskers.publications import PubSubManager
from whiskers.context import app

from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.resource import WebSocketResource

from twisted.internet import reactor

log.startLogging(sys.stdout)

class WebServer(WebSocketServerProtocol, PubSubManager):

    def setup(self, settings):
        factory = WebSocketServerFactory(settings.host)
        factory.protocol = WebServer

        resource = WebSocketResource(factory)

        # we server static files under "/" ..
        root = File(settings.client_dir)

        # and our WebSocket server under "/ws" (note that Twisted uses
        # bytes for URIs)
        root.putChild(b"ws", resource)

        # both under one Twisted Web Site
        site = Site(root)

        port = int(settings.host.split(":")[2])
        reactor.listenTCP(8000, site)


# class ServerFactory(WebSocketServerFactory, ClientRegistration):
#     pass