# coding=utf-8
from twisted.internet import reactor
from twisted.web import server
from txrestapi.resource import APIResource
from txrestapi.methods import GET, POST, PUT, ALL
import requests
import uuid
import urllib
import sys, os
sys.path.append(os.path.abspath("../"))



class MyResource(APIResource):

    @GET("/realtime")
    def realtime(self, request):
        args = dict((k, v[0]) for k, v in request.args.items())
        spider_name = args.get("spider",None)
        if not spider_name:
            return {"status":"spider is None"}
        argg = []
        for i in xrange(len(args.keys())):
            if args.keys()[i] != "spider":
                if self.check.obtain_json(args[args.keys()[i]]):
                    argg.append(args.keys()[i].upper()+"=%s"%urllib.quote(args[args.keys()[i]]))
                else:
                    argg.append(args.keys()[i].upper() + "=%s" % args[args.keys()[i]])
        jobid = uuid.uuid1().hex
        argg.append("JOBID=%s"%urllib.quote(jobid))
        setting = tuple(argg)
        pay_load = {"project":"QbSpider","spider":spider_name,"jobid":jobid,"setting":setting}
        r = requests.post("http://localhost:10010/schedule.json",data=pay_load)
        return jobid





    @GET("/schedule")
    def schedule(self, request):
        args = dict((k, v[0]) for k, v in request.args.items())
        spider_name = args.get("spider",None)
        if not spider_name:
            return {"status":"spider is None"}
        argg = []
        for i in xrange(len(args.keys())):
            if args.keys()[i] != "spider":
                if self.check.obtain_json(args[args.keys()[i]]):
                    argg.append(args.keys()[i].upper()+"=%s"%urllib.quote(args[args.keys()[i]]))
                else:
                    argg.append(args.keys()[i].upper() + "=%s" % args[args.keys()[i]])
        jobid = uuid.uuid1().hex
        argg.append("JOBID=%s"%urllib.quote(jobid))
        setting = tuple(argg)
        pay_load = {"project":"QbSpider","spider":spider_name,"jobid":jobid,"setting":setting}
        r = requests.post("http://localhost:10010/schedule.json",data=pay_load)
        return jobid





if __name__ == "__main__":
    site = server.Site(MyResource())
    reactor.listenTCP(8001, site)
    reactor.run()


