from twisted.internet import reactor, protocol
import time

PORT = 9000


class MyServer(protocol.Protocol):
    time.sleep(10)
    print "*"*66


class MyServerFactory(protocol.Factory):
    protocol = MyServer

if __name__ == "__main__":
    factory = MyServerFactory()
    reactor.listenTCP(PORT, factory)
    reactor.run()