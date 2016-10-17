

class Client:
    """

    """

    def __init__(self, proto):
        self.proto = proto
        self.conn = None
        self.subs = {}

    def __str__(self):
        return self.proto.peer

    def __repr__(self):
        return self.__str__()