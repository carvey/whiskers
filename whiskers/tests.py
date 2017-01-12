from twisted.trial import unittest
from twisted.test import proto_helpers

class TestRethinkToDDP(unittest.TestCase):
    # added, changed, removed conversions.
    # Need both DDP format -> RethinkDB and RethinkDB -> DDP Format
    pass

class TestDDPServer(unittest.TestCase):
    # pubs, methods, settings
    pass

class TestClientManagement(unittest.TestCase):
    """
    ** important **
    Clients who have successfully sent a DDP connect message should be registered with the factory.
    Needs lots of testing
    Need to ensure that:
        - clients do not get connected without sending the DDP connect msg
        - clients properly connect after sending the DDP msg
        - clients properly get unregistered after they disconnect

        - clients receive all initial data upon subscribing to a published table
        - clients receive all new additions/changes/removals to tables they are subscribed to
        - clients only receive updates from tables they are subscribed to
    """
    pass