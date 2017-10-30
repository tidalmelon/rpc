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
import sys,os
sys.path.append(os.path.abspath("../../"))
import tornado.ioloop
import tornado.web
import urllib, uuid
import requests
import json
import logging
import time,random
import redis
from QbSpider.scrapy_redis.queue import SpiderPriorityQueue
from QbSpider.spiders.jd_spider import JdSpider
from QbSpider.spiders.unicom_spider import UnicomSpider
from QbSpider.spiders.dianxin_spider import dianxinSpider
from scrapy.http import Request
import requests
from scrapyd.launcher import log

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"}

spider_url = {"jingdong":"https://passport.jd.com/new/login.aspx",
              "unicom":"https://uac.10010.com/portal/mallLogin.jsp?redirectURL=http://www.10010.com",
              "dianxin":"http://login.189.cn/login"}

spider_cls = {"jingdong":JdSpider,"unicom":UnicomSpider,"dianxin":dianxinSpider}

spider_names = [{"name":"jingdong","value":"京东"},{"name":"unicom","value":"联通"},{"name":"dianxin","value":"电信"}]

status_values = {"1":"爬取完成","0":"登陆成功","2":"需要手机验证码","3":"登陆密码错误(联通/电信每天只有五次密码输入错误的机会)","4":"手机验证码错误","5":"未找到相匹配的商家","6":"已达到5次最大登陆次数,今天无法登陆","7":"验证码服务器挂掉了"}

con = redis.Redis(host="127.0.0.1",port=6379,password="Qbbigdata")

url = "http://127.0.0.1:10010/schedule.json"

class JsonHandler(tornado.web.RequestHandler):

    def prepare(self):

        self.json_arg = None

        t = self.request.headers.get('Content-Type', '')

        if 'application/json' in t.lower():

            self.json_arg = json.loads(self.request.body)

class MainHandler(JsonHandler):

    executor = ThreadPoolExecutor(300)

    @run_on_executor
    def delaycrawl(self, pay_load):

        #if logintype == 1:

        try:

            requests.post(url, data=pay_load)

        except Exception, e:

            logging.warning(msg=e.message)

            return {"error": "spider scheduler error"}

        jobid = pay_load["jobid"]

        while True:

            status = con.hmget(jobid, "status")

            if status[0] in ["0","1", "2", "3", "4","5","6"]:

                break

            time.sleep(random.random())

        return {"status": status[0], "jobid": jobid}

        # else:
        #
        #     requests.post(url, data=pay_load)

    @run_on_executor
    def realtimecrawl(self, pay_load):

        # try:
        #
        #     requests.post(url, data=pay_load)
        #
        # except Exception, e:
        #
        #     logging.warning(msg=e.message)
        #
        #     return {"error": "spider scheduler error"}

        jobid = pay_load["jobid"]

        while True:

            status = con.hmget(jobid, "status")

            if status[0] in ["2", "0", "3", "4", "5", "6"]:

                break

            time.sleep(random.random())

        return {"status": status[0],"jobid":jobid}

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self,*args,**kwargs):

        if self.request.arguments == {}:


            try:

                body = json.loads(self.request.body)

            except Exception,e:

                self.write({"Error":e.message})

                return

            argss = dict((unicode(k).encode("utf8"), unicode(v).encode("utf8")) for k, v in body.iteritems())

        else:

            body = self.request.arguments

            argss = dict((k, v[0]) for k, v in body.iteritems())

        logging.info(argss)

        spider_name = argss.get("spider", None)

        #logintype = argss.get("logintype",None)

        # if logintype not in [1,2,"1","2"]:
        #
        #     self.write({"error": "logintype must be 1 or 2"})
        #
        #     return
        #
        # else:
        #
        #     logintype = int(logintype)

        if not spider_name:

            self.write({"error": "spidername is None"})

            return

        if not argss.get("spidertype", None):

            self.write({"error": "spidertype is None"})

            self.write({"error": "spidertype must be delay or realtime"})

            return

        else:

            if "delay" == argss.get("spidertype", None):

                flag = False

            elif "realtime" == argss.get("spidertype", None):

                flag = True

            else:

                self.write({"error": "spidertype must be delay or realtime"})

                return
        jobid = uuid.uuid1().hex

        argg = []

        queue_meta = {"JOBID":jobid}

        for k,v in argss.iteritems():

            queue_meta[k.upper()]=v

        for i in xrange(len(argss.keys())):

            if argss.keys()[i] != "spider":

                argg.append(argss.keys()[i].upper() + "=%s" % urllib.quote(argss[argss.keys()[i]]))

        argg.append("JOBID=%s" % urllib.quote(jobid))

        setting = tuple(argg)

        pay_load = {"project": "QbSpider", "spider": spider_name, "jobid": jobid, "setting": setting}

        print pay_load

        #if not flag and logintype == 1:
        if not flag:

            msg1 = yield self.delaycrawl(pay_load)

            self.write(msg1)

            return

        elif flag :
        #elif flag:

            print queue_meta

            queuess = SpiderPriorityQueue(server=con, spider=spider_cls[spider_name],
                                      key="%squeue_bigdata"%spider_name)

            queuess.push(Request(url=spider_url[spider_name],headers=headers,meta=queue_meta,dont_filter=True))

            msg = yield self.realtimecrawl(pay_load)

            self.write(msg)

            # if msg["status"] == "1":
            #
            #     p_l = list(pay_load["setting"])
            #
            #     [p_l.remove(s) for s in p_l if "SPIDERTYPE" in s]
            #
            #     p_l.append("SPIDERTYPE=%s"%urllib.quote("delay"))
            #
            #     pay_load.update({"setting":p_l})
            #
            #     self.delaycrawl(pay_load,logintype)

            #    return

            return

        else:

            self.write({"error":"spidertype not match logintype"})

        self.finish()


class LoginHandler(JsonHandler):
    executor = ThreadPoolExecutor(300)

    @run_on_executor
    def _getstatus(self, pay_load):

        # try:
        #
        #     requests.post(url, data=pay_load)
        #
        # except Exception, e:
        #
        #     logging.warning(msg=e.message)
        #
        #     return {"error": "spider scheduler error"}

        url = "http://172.28.40.23:9999/schedule"

        r = requests.post(url, data=pay_load)

        while r.text:

            return json.loads(r.text)


    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):

        self.render("login.html",messages=spider_names)

        self.flush()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):

        site = self.get_body_argument("sites")

        if site not in [x["value"] for x in spider_names]:

            self.render("error.html",messages="网站选择出错.....")

            return

        else:

            for x in spider_names:

                if site == x["value"]:

                    spider_name = x["name"]

            username = self.get_body_argument("username")

            password = self.get_body_argument("password")

            pay_load = {"spider": spider_name, "username": username, "password": password, "vercode": "",
                        "spidertype": "realtime"}

            r = yield self._getstatus(pay_load)

            if r["status"] == 0:

                self.render("success.html", messages="登陆成功......")

            else:

                self.render("error.html", messages=status_values[r["status"]])

if __name__ == "__main__":

    app = tornado.web.Application([
        (r"/schedule", MainHandler),
        (r"/login",LoginHandler),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
    )

    http_server = tornado.httpserver.HTTPServer(app)

    http_server.listen(port=9999, address="0.0.0.0")

    tornado.ioloop.IOLoop.instance().start()
