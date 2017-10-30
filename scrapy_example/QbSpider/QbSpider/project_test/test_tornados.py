#!/bin/env python
# coding=utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen
from tornado.concurrent import run_on_executor
# 这个并发库在python3自带在python2需要安装sudo pip install futures
from concurrent.futures import ThreadPoolExecutor
# coding=utf-8
#!/usr/bin/env python
import sys,os
sys.path.append(os.path.abspath("../../"))
import tornado.ioloop
import tornado.web
import urllib, uuid
import requests
import json
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
con = rcu().get_redis()
from QbSpider.spiders.jd_spider import JdSpider
import logging
import time,random

spider_cls = {"jingdong": JdSpider()}


class JsonHandler(tornado.web.RequestHandler):

    def prepare(self):

        self.json_arg = None

        t = self.request.headers.get('Content-Type', '')

        if 'application/json' in t.lower():

            self.json_arg = json.loads(self.request.body)

class MainHandler(JsonHandler):

    executor = ThreadPoolExecutor(200)

    def delaycrawl(self, pay_load,logintype):

        if logintype == 1:

            try:

                requests.post("http://localhost:10010/schedule.json", data=pay_load)

            except Exception, e:

                logging.warning(msg=e.message)

                return {"error": "spider scheduler error"}

            jobid = pay_load["jobid"]

            for x in xrange(5):

                status = con.hmget(jobid, "status")

                if status[0] in ["0","1", "2", "3", "4","5"]:

                    break

                time.sleep(1)

            return {"status": status[0], "jobid": jobid}

        else:

            requests.post("http://localhost:10010/schedule.json", data=pay_load)

    @run_on_executor
    def realtimecrawl(self, pay_load):

        try:

            requests.post("http://localhost:10010/schedule.json", data=pay_load)

        except Exception, e:

            logging.warning(msg=e.message)

            return {"error": "spider scheduler error"}

        jobid = pay_load["jobid"]

        while True:

            status = con.hmget(jobid, "status")

            if status[0] in ["1","2","3","4","5"]:

                break

            time.sleep(random.random())

        return {"status": status[0],"jobid":jobid}

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self,*args,**kwargs):

        if self.request.arguments == {}:

            body = json.loads(self.request.body)

            argss = dict((unicode(k).encode("utf8"), unicode(v).encode("utf8")) for k, v in body.iteritems())

        else:

            body = self.request.arguments

            argss = dict((k, v[0]) for k, v in body.iteritems())

        logging.info(argss)

        spider_name = argss.get("spider", None)

        logintype = argss.get("logintype",None)

        if logintype not in [1,2,"1","2"]:

            self.write({"error": "logintype must be 1 or 2"})

            return

        else:

            logintype = int(logintype)

        if not spider_name:

            self.write({"error": "spidername is None"})

            return

        if not argss.get("spidertype", None):

            self.write({"error": "spidertype is None"})

            return

        else:

            if "delay" == argss.get("spidertype", None):

                flag = False

            elif "realtime" == argss.get("spidertype", None):

                flag = True

            else:

                self.write({"error": "spidertype must be delay or realtime"})

                return

        argg = []

        for i in xrange(len(argss.keys())):

            if argss.keys()[i] != "spider":

                argg.append(argss.keys()[i].upper() + "=%s" % urllib.quote(argss[argss.keys()[i]]))

        jobid = uuid.uuid1().hex

        argg.append("JOBID=%s" % urllib.quote(jobid))

        setting = tuple(argg)

        pay_load = {"project": "QbSpider", "spider": spider_name, "jobid": jobid, "setting": setting}

        if not flag and logintype == 1:

            msg1 = yield self.delaycrawl(pay_load,logintype)

            self.write(msg1)

            return

        elif flag and logintype == 2 :

            msg = yield self.realtimecrawl(pay_load)

            self.write(msg)

            if msg["status"] == "1":

                p_l = list(pay_load["setting"])

                [p_l.remove(s) for s in p_l if "SPIDERTYPE" in s]

                p_l.append("SPIDERTYPE=%s"%urllib.quote("delay"))

                pay_load.update({"setting":p_l})

                self.delaycrawl(pay_load,logintype)

                return

            return

        else:

            self.write({"error":"spidertype not match logintype"})

        self.finish()

if __name__ == "__main__":

    app = tornado.web.Application(handlers=[
        (r"/schedule", MainHandler),])

    http_server = tornado.httpserver.HTTPServer(app)

    http_server.listen(port=9999, address="127.0.0.1")

    tornado.ioloop.IOLoop.instance().start()
