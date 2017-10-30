# coding=utf-8
from scrapy.http import FormRequest,Request

from scrapy.spiders import CrawlSpider

import json,re

from scrapy.selector.lxmlsel import HtmlXPathSelector

import time

import json

import random

import urllib

class CompanySpider(CrawlSpider):

    name = "companyinfo"

    start_urls = []

    allowed_domains = []

    custom_settings = {
        "COOKIES_ENABLED": False,
        "REDIRECT_ENABLED": False,
        "REFERER_ENABLED": False,
        "RETRY_TIMES": 20000,
        # "USEPROXYHIGHLEVEL": False,
        # "USELOCALIP": 1
        "REDIS_START_URLS_BATCH_SIZE": 150
    }

    def start_requests(self):

        url = "http://www.gsxt.gov.cn/SearchItemCaptcha?v=%s"%(str(time.time()).split(".")[0]+"000")

        yield Request(url)

    def parse(self, response):

        j_read = json.loads(response.body)

        status = j_read["success"]

        if status != 1:

            new_request = response.request.copy()

            new_request.don_filter = True

            yield new_request

        else:

            gt = j_read["gt"]

            challenge = j_read["challenge"]

            url = "http://api.geetest.com/get.php?gt=%s&challenge=%s&product=popup&offline=false&protocol=&path=/static/js/geetest.5.7.0.js&type=slide&callback=geetest_%s"

            yield Request(url%(gt,challenge,time.time()*1000),callback=self.parse_otherinfo)

    def parse_otherinfo(self,response):

        reg = re.findall(re.compile(r'[\S\s]+?\(([\S\s]+)\)',re.I),response.body)

        if len(reg) >0:

            j_read = json.loads(reg[0])

            code_refresh_url = "http://api.geetest.com/refresh.php?challenge=%s&gt=%s&callback=geetest_%s"%(j_read["gt"],j_read["challenge"],str(time.time()*1000))

            data_array_url = "http://www.gsxt.gov.cn/corp-query-geetest-validate-input.html?token=%s"%(random.randrange(10000000,99999999))

            search_url_validate = "http://www.gsxt.gov.cn/corp-query-search-test.html?searchword=%s"%(urllib.quote('百度'))

            code_validate_url = ""

            # userresponse:7e777e7eee77795
            # passtime:4480
            # imgload:816
            # a:G(!!Btttsstssssssstsstttsstssttsysytstssssstssstssss(!!($)S111111111920911202011111E91919111112011119MEEM$mK
            # callback:geetest_1484029621673

            print j_read

        else:

            new_request = response.request.copy()

            new_request.don_filter = True

            yield new_request

