import json

import rethinkdb as r
from twisted.internet.defer import inlineCallbacks, Deferred, gatherResults
from whiskers.rethink_ddp import rethink_to_ddp

class PubSubManager:
    """
    To be used on protocols that should allow clients to subscribe to published data feeds

    To be used with protocol factories that additionally extend ClientRegistration
    """

    @inlineCallbacks
    def print_feed(self, conn, table, ready, cancel):
        def errback_feed(feed, err):
            feed.close()
            return err

        feed = yield r.table(table).changes().run(conn)
        cancel.addErrback(lambda err: errback_feed(feed, err))
        ready.callback(None)
        while (yield feed.fetch_next()):
            item = yield feed.next()
            ddp_message = rethink_to_ddp(table, item)
            self.sendMessage(ddp_message.serialize(encoding='utf8'))

    @inlineCallbacks
    def notice_changes(self, conn, *tables):

        readies = [Deferred() for t in tables]
        cancel = Deferred()
        feeds = [self.print_feed(conn, table, ready, cancel) for table, ready in zip(tables, readies)]

        # Wait for the feeds to become ready
        yield gatherResults(readies)

        # cancel.addErrback(lambda err: None)
        # cancel.cancel()
        # yield DeferredList(feeds)

    @inlineCallbacks
    def initial_data(self, conn, table):
        cursor = yield r.table(table).run(conn)
        while (yield cursor.fetch_next()):
            item = yield cursor.next()
            # item is the plain dict, so transform into changefeed format for rethink_to_ddp
            item_dict = {"old_val": None, "new_val": item}
            ddp_message = rethink_to_ddp(table, item_dict)
            self.sendMessage(ddp_message.serialize(encoding="utf8"))