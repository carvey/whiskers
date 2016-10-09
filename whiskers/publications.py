import json

import rethinkdb as r
from twisted.internet.defer import inlineCallbacks, Deferred, gatherResults

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
            # print("Seen on table %s: %s" % (table, str(item)))
            # self.write(b"<p>Seen on table %s: %s</p>" % (bytes(table, encoding="UTF-8"), bytes(json.dumps(item), "UTF-8")))
            self.sendMessage(json.dumps(item).encode('utf8'))

    @inlineCallbacks
    def notice_changes(self, conn, *tables):

        readies = [Deferred() for t in tables]
        cancel = Deferred()
        feeds = [self.print_feed(conn, table, ready, cancel) for table, ready in zip(tables, readies)]

        # Wait for the feeds to become ready
        yield gatherResults(readies)
        # yield gatherResults([self.table_write(conn, table) for table in tables])

        # yield self.table_write(conn, 'a')
        # yield r.table('a').insert({'kitten': 'furry'}).run(conn)

        # for i in range(5):
        #     yield sleep(5)
        #     yield r.table('a').insert({'count': i, 'table': 'a'}).run(conn)

        # cancel.addErrback(lambda err: None)
        # cancel.cancel()
        # yield DeferredList(feeds)