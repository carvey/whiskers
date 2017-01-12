from whiskers.whiskers import DDPServer

server = DDPServer()

server.publish('testTable')


def test(num):
    return num + 1

server.methods = {
    'test': test
}


server.run()
