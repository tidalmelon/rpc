# coding=utf-8
from scrapy.http import FormRequest,Request

from scrapy.spiders import CrawlSpider

import json,re

from scrapy.selector.lxmlsel import HtmlXPathSelector

from QbSpider.utils.mobile_crypt import CryptSdmobile

class ShandongSpider(CrawlSpider):

    name = "sd_mobile"

    start_urls = ["https://sd.ac.10086.cn/login/"]

    allowed_domains = []

    def parse(self, response):

        url = "https://sd.ac.10086.cn/portal/servlet/LoginServlet"

        pay_load = {
            "mobileNum":"MTgzNTQ2NTE1NTU=",
            "servicePWD":"MTIzMTIz",
            "randCode":"请点击",
            "smsRandomCode":"",
            "submitMode":"2",
            "logonMode":"1",
            "FieldID":"1",
            "ReturnURL":"www.sd.10086.cn/eMobile/jsp/common/prior.jsp",
            "ErrorUrl":"../mainLogon.do",
            "entrance":"IndexBrief",
            "codeFlag":"0",
            "openFlag":"1",
        }

        yield FormRequest(url,formdata=pay_load,callback=self.login)

    def login(self,response):

        print response.headers

