# coding=utf-8

import sys, os

sys.path.append(os.path.abspath("../../"))
from scrapy.http import Request

from scrapy.selector.lxmlsel import HtmlXPathSelector

import pymongo

from QbSpider.scrapy_redis.spiders import Spiders

from QbSpider.scrapy_redis.queue import SpiderPriorityQueue
import redis

con = redis.Redis(host="127.0.0.1",port=6379,password="Qbbigdata")


class Qiyehuangye(Spiders):

    name = "qyhy"

    redis_key = "qyhyqueue_bigdata"

    allowed_domains = []

    start_urls = []

    MONGO_URI = "mongodb://root:Qbbigdata@127.0.0.1:27017"

    MONGO_DATABASE = "admin"

    client = pymongo.MongoClient(MONGO_URI)

    db = client[MONGO_DATABASE]

    custom_settings = {
        "COOKIES_ENABLED": False,
        "REDIRECT_ENABLED": False,
        "REFERER_ENABLED": False,
        "USEPROXYHIGHLEVEL": False,
        "RETRY_ENABLED" :True,
        "DOWNLOAD_TIMEOUT":180,
        "USELOCALIP": 1,
        "RETRY_HTTP_CODES":[500, 501, 502, 503, 504, 408, 403, 400, 405, 407, 307],
        "REDIS_START_URLS_BATCH_SIZE":150,
        "DOWNLOADER_MIDDLEWARES":{
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        #'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': None,
        'QbSpider.middleware.RandomUserAgentMiddleware.RotateUserAgentMiddleware': 500,
        # 'QbSpider.middleware.RandomProxyMiddleware.ProxyMiddleware': 750,
    }
    }

    def parse(self, response):

        hxs = HtmlXPathSelector(response)

        if hxs.xpath(u"//li[contains(text(),'企　业：')]/b/text()").extract() == []:

            item = {}

            item["url"] = response.url

            item["name"] = hxs.xpath(u"//li[contains(text(),'企　业：')]/b/text()").extract()

            item["phone"] = hxs.xpath(u'//dt[contains(text(),"联系我们")]/../dd[contains(text(),"手机：")]/text()').re('\d+')

            if item["phone"] == []:

                item["phone"] = hxs.xpath(u"//ul[@class='con-txt']/li/label[contains(text(),'电话：')]/../text()").extract()

            if item["phone"] == []:

                item["phone"] = hxs.xpath(u'//dt[contains(text(),"联系我们")]/../dd[contains(text(),"电话：")]/text()').re(ur'电话：([\S\s]+)')

            item["company_name"] = hxs.xpath(u'//dt[contains(text(),"联系我们")]/../dd[contains(text(),"名称：")]/text()').re(ur'名称：([\S\s]+)')

            item["company_addr"] = hxs.xpath(u'//dt[contains(text(),"联系我们")]/../dd[contains(text(),"地址：")]/text()').re(ur'地址：([\S\s]+)')

            item["company_sale"] = hxs.xpath(u'//dt[contains(text(),"主营产品")]/../dd/text()').extract()

            for k,v in item.iteritems():

                item[k] = "".join(v)

            self.db["huangye88_new"].insert(dict(item))









class Huangye88Queue(object):

    def gen_queue(self):

        queuess = SpiderPriorityQueue(server=con, spider=Qiyehuangye(),
                                     key="qyhyqueue_bigdata")

        for x in xrange(10000000):

            ur = "http://www.soudh.com/cshow-1.html" % x

            queuess.push(Request(url=ur))


if __name__ == "__main__":

    Huangye88Queue().gen_queue()






