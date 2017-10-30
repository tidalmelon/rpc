# coding=utf-8

import sys, os

sys.path.append(os.path.abspath("../"))
from scrapy.http import FormRequest,Request

from scrapy.spiders import CrawlSpider

import json,re

from scrapy.selector.lxmlsel import HtmlXPathSelector

import time

import json

import random

import urllib

import pymongo



class Law66(CrawlSpider):

    name = "law66"

    allowed_domains = []

    start_urls = []

    MONGO_URI = "mongodb://root:Qbbigdata@0.0.0.0:27017"

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
        "RETRY_HTTP_CODES":[500, 501, 502, 503, 504, 408, 403, 400, 405, 407, 307, 404],
        "REDIS_START_URLS_BATCH_SIZE":150,
        "DOWNLOADER_MIDDLEWARES":{
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': None,
        'QbSpider.middleware.RandomUserAgentMiddleware.RotateUserAgentMiddleware': 500,
        'QbSpider.middleware.RandomProxyMiddleware.ProxyMiddleware': 750,
    }
    }

    def start_requests(self):

        yield Request(url="http://www.66law.cn/help/allAreaLawyer.aspx")

    def parse(self, response):

        hxs = HtmlXPathSelector(response)

        ur = [x.replace("http://www.66law.cn/","").replace("/","") for x in hxs.xpath(u"//h4[contains(text(),'省份直达：')]/following-sibling::div[1]/a/@href").extract() if 'bj.aspx' not in x]+["beijing"]

        url = "http://www.66law.cn/%s/lawyer/page_1.aspx"

        for pro in ur:

            yield Request(url=url%pro,callback=self.parse_pro,meta={"pro":pro})

    def parse_pro(self,response):

        pro = response.meta["pro"]

        hxs = HtmlXPathSelector(response)

        ur = hxs.xpath('//a[@id="seemore"]/@href').extract()

        if ur == []:

            ur = hxs.xpath('//a[@class="m-page-next"]/@href').extract()

        for li in hxs.xpath('//ul[@class="find-list find-list5"]/li'):

            item = {}

            item["name"] = li.xpath('./p[1]/a[1]/text()').re(ur'([\S\s]+?)律师')

            item["phone"] = li.xpath('./p[1]/b[1]/text()').re(r'\d+')

            item["lawer_desc"] = li.xpath('./p[3]/span[1]/text()').extract()

            item["lawer_addr"] = li.xpath('./p[4]/text()').re(ur'联系地址：([\S\s]+)')

            for k,v in item.iteritems():

                item[k] = "".join(v)

            self.db["law66_new"].insert(dict(item))
        if ur != []:

            url = "http://www.66law.cn/%s/lawyer/%s"%(pro,ur[0])

            yield Request(url=url,callback=self.parse_pro,meta={"pro":pro})





