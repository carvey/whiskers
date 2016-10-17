from PythonDDPClient.src.message import *
from twisted.internet.defer import inlineCallbacks

class DDPServer:
    """
    Class to hold all logic related to handling DDP messages in Whiskers
    """

    @inlineCallbacks
    def handle_connect(self, message):
        """
        handles the DDP 'connect' message

        Per spec:
        "If the server is willing to speak the version of the protocol specified in the connect message,
        it sends back a connected message."

        connect (client -> server)
            session: string (if trying to reconnect to an existing DDP session)
            version: string (the proposed protocol version)
            support: array of strings (protocol versions supported by the client, in order of preference)

        Send back one of the following:

        connected (server->client)
            session: string (an identifier for the DDP session)

        failed (server->client)
            version: string (a suggested protocol version to connect with)

        :param message: the parsed ConnectionMessage Object
        :return:
        """

        self.factory.register_client(self)
        yield self.factory.connectionReady(self)

        welcome = WelcomeMessage(server_id=0)
        welcome_serialized = welcome.serialize(encoding='utf8')
        self.sendMessage(welcome_serialized)

        connected = ConnectedMessage(session="0")
        connected_serialized = connected.serialize(encoding='utf8')
        self.sendMessage(connected_serialized)

    @inlineCallbacks
    def handle_sub(self, message):
        """
        Handles the ddp 'sub' message

        sub (client -> server):
            id: string (an arbitrary client-determined identifier for this subscription)
            name: string (the name of the subscription)
            params: optional array of EJSON items (parameters to the subscription)

        :param message: the parsed SubMessage Object
        :return:
        """
        id = message.id
        name = message.name

        # still need to send all initial data
        # subscribe to new changes
        client = self.factory.clients[self]

        yield self.factory.connectionReady(self)

        yield self.initial_data(client.conn, name)
        ready = ReadyMessage(subs=[name, ])
        self.sendMessage(ready.serialize(encoding="utf8"))

        yield self.notice_changes(client.conn, name)

