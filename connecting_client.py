import sys

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS
from twisted.internet import reactor
from twisted.python import log

from PythonDDPClient.src.message import *


class BroadcastClientProtocol(WebSocketClientProtocol):

    """
    Simple client that connects to a WebSocket server, send a HELLO
    message every 2 seconds and print everything it receives.
    """

    def sendHello(self):
        print("sending welcome message")
        connect_msg = ConnectionMessage(version='1', support=['1'])
        self.sendMessage(connect_msg.serialize(encoding='utf8'))

        import time
        time.sleep(1)
        self.sub()

    def sub(self):
        print("send sub request")
        sub_msg = SubMessage(id=2, name="kittens", params=[])
        self.sendMessage(sub_msg.serialize(encoding="utf8"))

    def onOpen(self):
        self.sendHello()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("TXT: {}".format(payload.decode('utf8')))
        else:
            print(payload)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Need the WebSocket server address, i.e. ws://127.0.0.1:9000")
        sys.exit(1)

    log.startLogging(sys.stdout)

    factory = WebSocketClientFactory(sys.argv[1])
    factory.protocol = BroadcastClientProtocol
    connectWS(factory)

    reactor.run()