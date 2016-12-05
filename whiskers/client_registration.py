import rethinkdb as r
from twisted.internet.defer import inlineCallbacks, Deferred

from whiskers.client import Client


class ClientRegistration:
    """
    To be used along with any other class that needs to manage clients
    """
    def register_client(self, client_proto, connection_args):
        client = Client(client_proto)
        client.proto = client_proto

        if not hasattr(self, 'clients'):
            self.clients = {}

        if client_proto not in self.clients:
            conn = r.connect(**connection_args)
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
