import sys

from autobahn.twisted.websocket import WebSocketServerProtocol
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from whiskers.publications import PubSubManager

log.startLogging(sys.stdout)

class WebServer(WebSocketServerProtocol):

    def setup(self, settings):
        root = File(settings.client_dir)
        root.putChild("static", File('.'))
        root.putChild("static", File('./whiskers/node_modules'))
        site = Site(root)

        reactor.listenTCP(8000, site)


# class ServerFactory(WebSocketServerFactory, ClientRegistration):
#     pass