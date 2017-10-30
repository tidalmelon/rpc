# coding=utf-8
from scrapy.http import FormRequest,Request

from scrapy.spiders import CrawlSpider

import json,re

from scrapy.selector.lxmlsel import HtmlXPathSelector

import time

import pymongo

import logging

from QbSpider.scrapy_redis.spiders import Spiders

from scrapy_redis.spiders import RedisCrawlSpider

from QbSpider.scrapy_redis.queue import SpiderPriorityQueue

from QbSpider.utils.RedisUtil import RedisConfUtil as rcu

con = rcu().get_redis()

class CpwswUrlSpider(RedisCrawlSpider):

    def __init__(self, *a, **kw):

        super(CpwswUrlSpider, self).__init__(*a, **kw)

        self.detail_queue = SpiderPriorityQueue(server=con, spider=CpwswDetailSpider(),
                                    key="%s_queue_bigdata" % "cpwswlist")

    name = "cpwsw_list"

    redis_key = "cpwsw_queue_bigdata"

    start_urlss = ["http://wenshu.court.gov.cn/List/ListContent"]

    custom_settings = {
        "COOKIES_ENABLED": False,
        "REDIRECT_ENABLED": False,
        "REFERER_ENABLED": False,
        "RETRY_TIMES":20000,
        # "USEPROXYHIGHLEVEL": False,
        # "USELOCALIP": 1
        "REDIS_START_URLS_BATCH_SIZE":150
    }

    law_case = ["行政案件","民事案件","刑事案件","赔偿案件","执行案件"]

    court_level = ["基层法院","中级法院","高级法院","最高法院"]

    key_word = ['\xe7\xa8\x8b\xe5\xba\x8f\xe5\x90\x88\xe6\xb3\x95', '\xe5\x85\xb7\xe4\xbd\x93\xe8\xa1\x8c\xe6\x94\xbf\xe8\xa1\x8c\xe4\xb8\xba', '\xe9\xa9\xb3\xe5\x9b\x9e', '\xe7\xac\xac\xe4\xb8\x89\xe4\xba\xba', '\xe4\xb8\x8d\xe5\xb1\xa5\xe8\xa1\x8c', '\xe5\x82\xac\xe5\x91\x8a', '\xe5\xb7\xa5\xe4\xbc\xa4', '\xe8\xbf\x9d\xe6\xb3\x95\xe8\xa1\x8c\xe4\xb8\xba', '\xe4\xb8\x8d\xe4\xba\x88\xe5\x8f\x97\xe7\x90\x86', '\xe6\xb3\x95\xe5\xae\x9a\xe6\x9c\x9f\xe9\x99\x90', '\xe5\x88\xa9\xe5\xae\xb3\xe5\x85\xb3\xe7\xb3\xbb', '\xe7\xae\xa1\xe8\xbe\x96', '\xe6\x88\xbf\xe5\xb1\x8b\xe5\xbe\x81\xe6\x94\xb6', '\xe6\x8b\x86\xe8\xbf\x81', '\xe6\x89\x80\xe6\x9c\x89\xe6\x9d\x83', '\xe6\x88\xbf\xe5\xb1\x8b\xe6\x8b\x86\xe8\xbf\x81', '\xe5\x8f\x98\xe6\x9b\xb4', '\xe6\x9c\xac\xe6\xa1\x88\xe4\xba\x89\xe8\xae\xae', '\xe6\x8e\x88\xe6\x9d\x83', '\xe5\x90\x88\xe5\x90\x8c', '\xe9\x89\xb4\xe5\xae\x9a', '\xe8\xa1\x8c\xe6\x94\xbf\xe8\xb5\x94\xe5\x81\xbf', '\xe4\xb8\x8d\xe5\x8a\xa8\xe4\xba\xa7', '\xe4\xba\xa4\xe9\x80\x9a\xe4\xba\x8b\xe6\x95\x85', '\xe5\xb1\xa5\xe8\xa1\x8c\xe6\xb3\x95\xe5\xae\x9a\xe8\x81\x8c\xe8\xb4\xa3', '\xe5\x9c\x9f\xe5\x9c\xb0\xe4\xbd\xbf\xe7\x94\xa8\xe6\x9d\x83', '\xe5\x85\xac\xe5\x85\xb1\xe5\x88\xa9\xe7\x9b\x8a', '\xe5\xbb\xba\xe8\xae\xbe\xe7\x94\xa8\xe5\x9c\xb0', '\xe6\x88\xbf\xe5\xb1\x8b\xe6\x89\x80\xe6\x9c\x89\xe6\x9d\x83', '\xe8\xa1\x8c\xe6\x94\xbf\xe6\x8b\x98\xe7\x95\x99', '\xe5\xbb\xba\xe8\xae\xbe\xe5\xb7\xa5\xe7\xa8\x8b', '\xe6\x92\xa4\xe5\x9b\x9e\xe8\xb5\xb7\xe8\xaf\x89', '\xe5\xa4\x84\xe5\x88\x86', '\xe5\x9c\x9f\xe5\x9c\xb0\xe7\x99\xbb\xe8\xae\xb0', '\xe5\xae\x85\xe5\x9f\xba\xe5\x9c\xb0', '\xe5\x9b\xbd\xe6\x9c\x89\xe5\x9c\x9f\xe5\x9c\xb0\xe4\xbd\xbf\xe7\x94\xa8\xe6\x9d\x83', '\xe8\xb4\xa2\xe4\xba\xa7\xe6\x9d\x83', '\xe5\x9c\x9f\xe5\x9c\xb0\xe5\xbe\x81\xe6\x94\xb6', '\xe6\xb2\xa1\xe6\x94\xb6', '\xe5\x8f\x98\xe6\x9b\xb4\xe7\x99\xbb\xe8\xae\xb0', '\xe7\xb1\xbb\xe4\xbc\xbc\xe5\x95\x86\xe5\x93\x81', '\xe7\xa1\xae\xe6\x9d\x83', '\xe6\x8a\x95\xe8\xb5\x84', '\xe4\xb8\x8d\xe4\xbd\x9c\xe4\xb8\xba', '\xe5\x88\xa9\xe5\xae\xb3\xe5\x85\xb3\xe7\xb3\xbb\xe4\xba\xba', '\xe6\xb7\xb7\xe6\xb7\x86', '\xe4\xbc\xa0\xe5\x94\xa4', '\xe6\xb3\x95\xe5\xae\x9a\xe4\xbb\xa3\xe8\xa1\xa8\xe4\xba\xba', '\xe8\xa1\x8c\xe6\x94\xbf\xe5\xbc\xba\xe5\x88\xb6\xe6\x89\xa7\xe8\xa1\x8c', '\xe7\xbb\x99\xe4\xbb\x98', '\xe9\xa9\xb3\xe5\x9b\x9e\xe8\xb5\xb7\xe8\xaf\x89', '\xe5\x9c\x9f\xe5\x9c\xb0\xe6\x89\xbf\xe5\x8c\x85\xe7\xbb\x8f\xe8\x90\xa5\xe6\x9d\x83', '\xe6\x88\xbf\xe5\xb1\x8b\xe6\x9d\x83\xe5\xb1\x9e', '\xe8\xbf\x91\xe4\xbc\xbc\xe5\x95\x86\xe6\xa0\x87', '\xe6\x8b\x86\xe8\xbf\x81\xe5\xae\x89\xe7\xbd\xae', '\xe5\x85\xac\xe5\x85\xb1\xe7\xa7\xa9\xe5\xba\x8f', '\xe4\xbf\x9d\xe9\x99\xa9\xe8\xb4\xb9', '\xe5\x8a\xb3\xe5\x8a\xa8\xe5\x90\x88\xe5\x90\x8c', '\xe5\x85\xac\xe8\xaf\x81', '\xe6\x84\x8f\xe6\x80\x9d\xe8\xa1\xa8\xe7\xa4\xba\xe7\x9c\x9f\xe5\xae\x9e', '\xe5\x80\xba\xe6\x9d\x83', '\xe4\xba\xa4\xe4\xbb\x98', '\xe8\xaf\x89\xe8\xae\xbc\xe6\xa0\x87\xe7\x9a\x84', '\xe7\xa7\x9f\xe8\xb5\x81', '\xe6\x88\xbf\xe5\xb1\x8b\xe4\xba\xa7\xe6\x9d\x83', '\xe6\x9f\xa5\xe5\xb0\x81', '\xe5\x85\xb1\xe6\x9c\x89', '\xe6\x89\xa3\xe6\x8a\xbc', '\xe5\x8a\xa8\xe4\xba\xa7', '\xe8\x82\xa1\xe4\xbb\xbd', '\xe8\xb6\x85\xe8\xb6\x8a\xe8\x81\x8c\xe6\x9d\x83', '\xe5\xa7\x94\xe6\x89\x98\xe4\xbb\xa3\xe7\x90\x86\xe4\xba\xba', '\xe6\x8a\xb5\xe6\x8a\xbc', '\xe4\xbc\xaa\xe9\x80\xa0', '\xe5\x90\x88\xe6\xb3\x95\xe8\xb4\xa2\xe4\xba\xa7', '\xe5\xbc\xba\xe5\x88\xb6\xe6\x8e\xaa\xe6\x96\xbd', '\xe6\x89\xbf\xe5\x8c\x85\xe7\xbb\x8f\xe8\x90\xa5', '\xe8\xbf\x94\xe8\xbf\x98', '\xe5\xbc\xba\xe5\x88\xb6\xe6\x80\xa7\xe8\xa7\x84\xe5\xae\x9a', '\xe8\xb5\x94\xe5\x81\xbf\xe6\x8d\x9f\xe5\xa4\xb1', '\xe4\xbb\xa3\xe7\x90\x86\xe4\xba\xba', '\xe5\x85\xa8\xe9\x9d\xa2\xe5\xb1\xa5\xe8\xa1\x8c', '\xe5\x9c\x9f\xe5\x9c\xb0\xe6\x9d\x83\xe5\xb1\x9e\xe4\xba\x89\xe8\xae\xae', '\xe6\x89\xbf\xe5\x8c\x85\xe5\x90\x88\xe5\x90\x8c', '\xe4\xb9\xa6\xe9\x9d\xa2\xe5\xbd\xa2\xe5\xbc\x8f', '\xe5\x9c\x9f\xe5\x9c\xb0\xe8\xaf\x81', '\xe7\xbb\xa7\xe6\x89\xbf', '\xe6\xbb\x9e\xe7\xba\xb3\xe9\x87\x91', '\xe8\x82\xa1\xe6\x9d\x83', '\xe6\x88\xbf\xe4\xba\xa7\xe8\xaf\x81', '\xe4\xbf\x9d\xe8\xaf\x81', '\xe6\x89\xbf\xe8\xaf\xba', '\xe5\x9f\xba\xe9\x87\x91', '\xe5\x88\x86\xe5\x85\xac\xe5\x8f\xb8', '\xe8\xbf\x9d\xe6\xb3\x95\xe6\x89\x80\xe5\xbe\x97', '\xe6\x88\xbf\xe5\xb1\x8b\xe4\xb9\xb0\xe5\x8d\x96', '\xe8\x87\xaa\xe7\x84\xb6\xe8\xb5\x84\xe6\xba\x90', '\xe5\xa9\x9a\xe5\xa7\xbb\xe7\x99\xbb\xe8\xae\xb0']

    court_area = ['\xe6\x9c\x80\xe9\xab\x98\xe4\xba\xba\xe6\xb0\x91\xe6\xb3\x95\xe9\x99\xa2', '\xe5\x8c\x97\xe4\xba\xac\xe5\xb8\x82', '\xe5\xa4\xa9\xe6\xb4\xa5\xe5\xb8\x82', '\xe6\xb2\xb3\xe5\x8c\x97\xe7\x9c\x81', '\xe5\xb1\xb1\xe8\xa5\xbf\xe7\x9c\x81', '\xe5\x86\x85\xe8\x92\x99\xe5\x8f\xa4\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', '\xe8\xbe\xbd\xe5\xae\x81\xe7\x9c\x81', '\xe8\xbe\xbd\xe5\xae\x81\xe7\x9c\x81\xe6\xb2\x88\xe9\x98\xb3\xe5\xb8\x82\xe4\xb8\xad\xe7\xba\xa7\xe4\xba\xba\xe6\xb0\x91\xe6\xb3\x95\xe9\x99\xa2', '\xe5\x90\x89\xe6\x9e\x97\xe7\x9c\x81', '\xe9\xbb\x91\xe9\xbe\x99\xe6\xb1\x9f\xe7\x9c\x81', '\xe4\xb8\x8a\xe6\xb5\xb7\xe5\xb8\x82', '\xe6\xb1\x9f\xe8\x8b\x8f\xe7\x9c\x81', '\xe6\xb5\x99\xe6\xb1\x9f\xe7\x9c\x81', '\xe5\xae\x89\xe5\xbe\xbd\xe7\x9c\x81', '\xe7\xa6\x8f\xe5\xbb\xba\xe7\x9c\x81', '\xe6\xb1\x9f\xe8\xa5\xbf\xe7\x9c\x81', '\xe5\xb1\xb1\xe4\xb8\x9c\xe7\x9c\x81', '\xe6\xb2\xb3\xe5\x8d\x97\xe7\x9c\x81', '\xe6\xb9\x96\xe5\x8c\x97\xe7\x9c\x81', '\xe6\xb9\x96\xe5\x8d\x97\xe7\x9c\x81', '\xe5\xb9\xbf\xe4\xb8\x9c\xe7\x9c\x81', '\xe5\xb9\xbf\xe8\xa5\xbf\xe5\xa3\xae\xe6\x97\x8f\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', '\xe6\xb5\xb7\xe5\x8d\x97\xe7\x9c\x81', '\xe9\x87\x8d\xe5\xba\x86\xe5\xb8\x82', '\xe5\x9b\x9b\xe5\xb7\x9d\xe7\x9c\x81', '\xe8\xb4\xb5\xe5\xb7\x9e\xe7\x9c\x81', '\xe4\xba\x91\xe5\x8d\x97\xe7\x9c\x81', '\xe8\xa5\xbf\xe8\x97\x8f\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', '\xe9\x99\x95\xe8\xa5\xbf\xe7\x9c\x81', '\xe7\x94\x98\xe8\x82\x83\xe7\x9c\x81', '\xe9\x9d\x92\xe6\xb5\xb7\xe7\x9c\x81', '\xe5\xae\x81\xe5\xa4\x8f\xe5\x9b\x9e\xe6\x97\x8f\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', '\xe6\x96\xb0\xe7\x96\x86\xe7\xbb\xb4\xe5\x90\xbe\xe5\xb0\x94\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', '\xe6\x96\xb0\xe7\x96\x86\xe7\xbb\xb4\xe5\x90\xbe\xe5\xb0\x94\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba\xe9\xab\x98\xe7\xba\xa7\xe4\xba\xba\xe6\xb0\x91\xe6\xb3\x95\xe9\x99\xa2\xe7\x94\x9f\xe4\xba\xa7\xe5\xbb\xba\xe8\xae\xbe\xe5\x85\xb5\xe5\x9b\xa2\xe5\x88\x86\xe9\x99\xa2']

    cp_year = ['2015', '2016', '2014', '2013', '2012', '2011', '2010', '2009', '2007', '2008', '2006', '2005', '2003', '2004', '2001', '2002', '2000', '1999']

    sp_producer = ['\xe4\xb8\x80\xe5\xae\xa1', '\xe4\xba\x8c\xe5\xae\xa1', '\xe5\x86\x8d\xe5\xae\xa1', '\xe9\x9d\x9e\xe8\xaf\x89\xe6\x89\xa7\xe8\xa1\x8c\xe5\xae\xa1\xe6\x9f\xa5', '\xe5\x86\x8d\xe5\xae\xa1\xe5\xae\xa1\xe6\x9f\xa5\xe4\xb8\x8e\xe5\xae\xa1\xe5\x88\xa4\xe7\x9b\x91\xe7\x9d\xa3', '\xe5\x85\xb6\xe4\xbb\x96']

    ws_type = ['\xe5\x88\xa4\xe5\x86\xb3\xe4\xb9\xa6', '\xe8\xa3\x81\xe5\xae\x9a\xe4\xb9\xa6', '\xe8\xb0\x83\xe8\xa7\xa3\xe4\xb9\xa6', '\xe5\x86\xb3\xe5\xae\x9a\xe4\xb9\xa6', '\xe9\x80\x9a\xe7\x9f\xa5\xe4\xb9\xa6', '\xe6\x89\xb9\xe5\xa4\x8d', '\xe7\xad\x94\xe5\xa4\x8d', '\xe5\x87\xbd', '\xe4\xbb\xa4', '\xe5\x85\xb6\xe4\xbb\x96']

    headers = {
        "Host": "wenshu.court.gov.cn",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6"
    }

    js_ur = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=%s"

    def start_requests(self):

        for case in self.law_case:

            for court in self.court_level:

                for w_type in self.ws_type:

                    for sp_pro in self.sp_producer:

                            for year in self.cp_year:

                                for area in self.court_area:

                                    for k_w in self.key_word:

                                        pay_load = {
                                            "Param": "案件类型:%s, 法院层级:%s, 法院地域:%s, 裁判年份:%s, 关键词:%s, 审判程序:%s, 文书类型:%s"%(case,court,area,year,k_w,sp_pro,w_type),
                                            "Index": "1",
                                            "Page": "20",
                                            "Order": "法院层级",
                                            "Direction": "asc"
                                        }

                                        #yield FormRequest(url=self.start_urlss[0],formdata=pay_load,headers=self.headers,meta={"pay_load":pay_load})
                                        yield FormRequest(url=self.start_urlss[0],formdata=pay_load,headers=self.headers)

    def parse(self, response):

        try:
            print response.body

            ws_list =  response.body.decode("utf8").replace("[","").replace("]","").replace("\\","")[1:-1].split("{")

            wss = [json.loads("{"+ws.replace("},","}")) for ws in ws_list[1:]]

            if len(wss) == 0:

                new_request = response.request.copy()

                new_request.dont_filter = True

                yield new_request

            else:

                count = int(wss[0]["Count"])

                page_nos = count/20 if count%20==0 else count/20+1

                pay_load = response.meta["pay_load"]

                for page in range(1,page_nos+1):

                    pay_load["Index"] = page

                    new_request = response.request.copy()

                    new_request.dont_filter = True

                    new_request.formadata = pay_load

                    new_request.callback=self.parse_wsid

                    yield new_request

        except Exception,e:

            new_request = response.request.copy()

            new_request.dont_filter = True

            yield new_request


    def parse_wsid(self,response):

        try:

            ws_list = response.body.decode("utf8").replace("[", "").replace("]", "").replace("\\", "")[1:-1].split("{")

            wss = [json.loads("{" + ws.replace("},", "}")) for ws in ws_list[1:]]

            if len(wss) == 0:

                new_request = response.request.copy()

                new_request.dont_filter = True

                yield new_request

            else:

                for ws in wss:

                    for k,v in ws.iteritems():

                        if k == u"文书ID":

                            #yield Request(url=self.js_ur%v,headers=self.headers,callback=self.parse_item,meta={"wsno":v})

                            self.detail_queue.push(request=Request(url=self.js_ur%v,headers=self.headers,meta={"wsno":v}))
        except Exception,e:

            new_request = response.request.copy()

            new_request.dont_filter = True

            yield new_request

class CpwswDetailSpider(Spiders):

    name = "cpwsw_detail"

    redis_key = "cpwswlist_queue_bigdata"

    custom_settings = {
        "COOKIES_ENABLED": False,
        "REDIRECT_ENABLED": False,
        "REFERER_ENABLED": False,
        "RETRY_TIMES": 20000,
        # "USEPROXYHIGHLEVEL": False,
        # "USELOCALIP": 1
        "REDIS_START_URLS_BATCH_SIZE": 150
    }

    MONGO_URI = "mongodb://root:Qbbigdata@0.0.0.0:27017"

    MONGO_DATABASE = "admin"

    client = pymongo.MongoClient(MONGO_URI)

    db = client[MONGO_DATABASE]

    comm_ur = "http://wenshu.court.gov.cn/content/content?DocID=%s"

    def parse(self,response):

        wsid = response.meta["wsno"]

        item = {}

        body = re.findall(re.compile(r'jsonHtmlData\s+=\s+"([\s\S]+?)";',re.I),response.body.decode("utf8").replace("\\",""))

        if len(body) > 0 :

            j_read = json.loads(body[0])

            item["spidertime"] = ti = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

            item["title"] = j_read["Title"]

            item["pubdate"] = j_read["PubDate"]

            hxs = HtmlXPathSelector(text=j_read["Html"])

            item["courtname"] = "@#$".join(hxs.xpath("//a[@name='WBSB']/following-sibling::div[1]/text()").extract())

            item["wsid"] = wsid

            item["wsurl"] = self.comm_ur%wsid

            item["wstype"] = "@#$".join(hxs.xpath("//a[@name='WBSB']/following-sibling::div[2]/text()").extract())

            item["wswordsize"] = "@#$".join(hxs.xpath("//a[@name='WBSB']/following-sibling::div[3]/text()").extract())

            relate_peoples = re.findall(re.compile(r"name='DSRXX'></a>([\s\S]+?)<a\s+type='dir'\s+name='SSJL'></a>",re.I),j_read["Html"])

            if len(relate_peoples)>0:

                peoples_hxs = HtmlXPathSelector(text=relate_peoples[0])

                item["wsrelatepeople"] = "@#$".join(peoples_hxs.xpath("//div/text()").extract())

            else:

                item["wsrelatepeople"] = ""

            facts = re.findall(re.compile(r"name='SSJL'></a>([\s\S]+?)<a\s+type='dir'\s+name='CPYZ'></a>",re.I),j_read["Html"])

            if len(facts)>0:

                facts_hxs = HtmlXPathSelector(text=facts[0])

                item["wsfacts"] = "@#$".join(facts_hxs.xpath("//div/text()").extract())

            else:

                item["wsfacts"] = ""

            reasons = re.findall(re.compile(r"name='CPYZ'></a>([\s\S]+?)<a\s+type='dir'\s+name='PJJG'></a>",re.I),j_read["Html"])

            if len(reasons) > 0:

                reasons_hxs = HtmlXPathSelector(text=reasons[0])

                item["wsreasons"] = "@#$".join(reasons_hxs.xpath("//div/text()").extract())

            else:

                item["wsreasons"] = ""

            results = re.findall(re.compile(r"name='PJJG'></a>([\s\S]+?)<a\s+type='dir'\s+name='WBWB'></a>", re.I),j_read["Html"])

            if len(results) > 0:

                results_hxs = HtmlXPathSelector(text=results[0])

                item["wsresults"] = "@#$".join(results_hxs.xpath("//div/text()").extract())

            else:

                item["wsresults"] = ""

            item["wsend"] = "@#$".join(hxs.xpath("//a[@name='WBWB']/following-sibling::div/text()").extract())

            ti = time.strftime('%Y%m%d000000', time.localtime(time.time()))

            try:

                self.db["cpwsw"].insert(dict(item))

            except Exception,e:

                logging.warning(msg=e.message)

        else:

            new_request = response.request.copy()

            new_request.dont_filter = True

            yield new_request









