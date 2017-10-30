from twisted.internet import reactor, protocol

HOST = 'localhost'
PORT = 9000

class MyClient(protocol.Protocol):
    def connectionMade(self):
        print "connected!"

class MyClientFactory(protocol.ClientFactory):
    protocol = MyClient

if __name__ == "__main__":

    factory = MyClientFactory()
    reactor.connectTCP(HOST, PORT, factory)
    reactor.run()