
# coding=utf-8
#!/usr/bin/env python
import sys,os
sys.path.append(os.path.abspath("../../"))
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import urllib, uuid
import requests
import json
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
import logging
con = rcu().get_redis()
from QbSpider.spiders.jd_spider import JdSpider
import logging
import time,random


class StartServices(object):
    def start(self):

        print "-"*66


if __name__ == "__main__":

    print "&"*66

    reactor.run()

    print "*"*66

    StartServices().start()


