# coding=utf-8
from scrapy.http import FormRequest,Request

from scrapy.spiders import CrawlSpider

import json,re

from scrapy.selector.lxmlsel import HtmlXPathSelector

from QbSpider.utils.mobile_crypt import CryptSdmobile

class JingsuSpider(CrawlSpider):

    name = "js_mobile"

    start_urls = ["http://service.js.10086.cn/login.html?url=index.html"]

    allowed_domains = []

    def parse(self, response):

        url = "http://service.js.10086.cn/actionDispatcher.do"

        pay_load = {
            "userLoginTransferProtocol":"https",
            "redirectUrl":"index.html",
            "reqUrl":"login",
            "busiNum":"LOGIN",
            "operType":"0",
            "passwordType":"1",
            "isSavePasswordVal":"0",
            "isSavePasswordVal_N":"1",
            "currentD":"1",
            "loginFormTab":"http",
            "loginType":"1",
            "phone-login":"on",
            "mobile":"18354651555",
            "city":"NJDQ",
            "password":"789456",
            "verifyCode":"",
        }

        yield FormRequest(url,formdata=pay_load,callback=self.login)

    def login(self,response):

        print response.headers

