from twisted.internet import reactor
from twisted.internet.defer import Deferred

def sleep(delay):
    d = Deferred()
    reactor.callLater(delay, d.callback, None)
    return d