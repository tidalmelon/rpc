from twisted.internet import reactor
#from twisted.internet.interfaces import

class Count(object):

    i = 5

    def hello(self):

        if self.i == 0:

            reactor.stop()

        else:

            print self.i

            self.i-=1

            reactor.callLater(0,self.hello)



        # print "running"
reactor.callWhenRunning(Count().hello)
reactor.addReader()
reactor.run()