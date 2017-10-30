# coding=utf-8
import StringIO
import json
import logging
import time
import os
import urllib
import urllib2
from base64 import b64decode,b64encode
from os.path import join,dirname
import rsa
from Crypto.PublicKey import RSA
from scrapy.exceptions import DontCloseSpider
from scrapy.http import Request,FormRequest
from scrapy.selector.lxmlsel import HtmlXPathSelector
from scrapy.spiders import Spider
from scrapy.spider import CrawlSpider
from QbSpider.utils.utils import Util
from QbSpider.scrapy_redis.spiders import Spiders
import random
from scrapy import signals
from urlparse import urljoin
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
from QbSpider.scrapy_redis.queue import SpiderPriorityQueue
from QbSpider.scrapy_redis.spiders import RedisSpider
import sys
from os.path import extsep
from Crypto.Cipher import AES
from Crypto.Hash import MD5
import requests
import base64

reload(sys)
sys.setdefaultencoding("utf-8")


class dianxinSpider(Spiders):

    name = "dianxin"

    redis_key = "dianxinqueue_bigdata"

    custom_settings = {
        "COOKIES_ENABLED": True,
        "REDIRECT_ENABLED": True,#支不支持302跳转
        "LOGIN_TYPE": True,
        "DOWNLOAD_DELAY": 0,
        "DOWNLOAD_TIMEOUT": 120,
        "USELOCALIP": 1,
        "DOWNLOADER_MIDDLEWARES" : {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': None,
            'QbSpider.middleware.RandomUserAgentMiddleware.RotateUserAgentMiddleware': 500,
            #'QbSpider.middleware.RandomProxyMiddleware.ProxyMiddleware': 750,
        }
    }
    #handle_httpstatus_list = [302,301] #不用scrapy自己的302处理机制
    allowed_domains = []

    start_urlss = ["http://login.189.cn/login"]
    login_url = "http://login.189.cn/login"
    # "http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10001&toStUrl=http://bj.189.cn/iframe/custservice/modifyUserInfo.action"


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):

        spider = super(dianxinSpider, cls).from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.spider_closed, signals.spider_closed)

        return spider

    def __init__(self, *a, **kw):

        super(dianxinSpider, self).__init__(*a, **kw)

        self.utils = Util()

        self.con = rcu().get_redis()

        self.con.ping()

        self.myhome_url = "http://www.189.cn/dqmh/my189/initMy189home.do"
        self.huafei_url = "http://www.189.cn/dqmh/order/getHuaFei.do"
        self.taocan_url = "http://www.189.cn/dqmh/order/getTaoCan.do"
        self.start_huafei_url = "/iframe/feequery/billQuery.action"
        self.duanxinyanzheng_1_url = "/iframe/feequery/smsRandCodeSend.action"
        self.duanxinyanzheng_url ="/iframe/feequery/detailValidCode.action"
        self.tonghuajilu_url = "/iframe/feequery/billDetailQuery.action"
        self.huafeizhangdan_url = "/iframe/feequery/billQuery.action"
        self.kehuziliao_url = "/iframe/custservice/modifyUserInfo.action"
        self.start_url = "http://www.189.cn"

        self.ti = 0

    # def start_requests(self):
    #     meta = {}
    #
    #     yield Request(self.login_url,meta=meta)

    def parse(self, response):
        self.ti = 1

        self.meta = response.meta
        self.tel = response.meta["USERNAME"]#urllib.unquote(self.settings.get("TEL", None))

        self.password = response.meta["PASSWORD"]#urllib.unquote(self.settings.get("PASSWORD", None))

        self.jobid = response.meta["JOBID"]#urllib.unquote(self.settings.get("JOBID", None))

        # self.tel = '13301162389'
        # self.password = '198616'
        # self.tel = '18910211125'
        # self.password = '235277'
        # self.tel = '15332188167'
        # self.password = '379189'
        # self.jobid = 'dianxin_jobid_3'

        # self.item_status["status"] = 0
        # self.con.hmset(self.jobid, self.item_status)  ##0代表正在爬取

        self.sess = {}
        self.sesss = {}
        self.int_retry = 0

        self.items = []
        self.status = 0
        self.item_status = {}
        self.items = {
            "flowsBalanceAmount": "",  # 剩余流量M
            "flowsUseAmount": "",  # 使用流量M
            "yvyinUsePercent": "",  # 语音使用百分比
            "duanxinUsePercent": "",  # 短信使用百分比
            "flowsUsePercent": "",  # 流量使用百分比
            "callBalanceAmount": "",  # 剩余语音
            "msgBalanceAmount": "",  # 剩余短信数量
            "month_charge": "",  # 本月话费
            "myjifen": "",  # 积分
            "comm": [],
        }

        global null
        null = None

        n = self.password
        t = MD5.new("login.189.cn").hexdigest()
        i = t.encode("utf8")
        u = AES.new(i, AES.MODE_CBC, b'1234567812345678')
        length = 16 - (len(n) % 16)
        n += chr(length) * length
        self.crypt_password = base64.b64encode(u.encrypt(n))

        cookie = [i.split(";")[0] for i in response.headers.getlist('Set-Cookie')]

        for cook in cookie:
            self.sesss.update({cook[:cook.index("=")]: cook[cook.index("=") + 1:]})

        from_data = {
            "m": "checkphone",
            "phone": self.tel
            }
        html = HtmlXPathSelector(response)
        data_guid = ''.join(html.xpath("//img[@id='imgCaptcha']/@data-guid").extract())
        meta = {"data_guid":data_guid}

        yield FormRequest(url="http://login.189.cn/login/ajax",dont_filter=True,formdata=from_data,callback=self.parse_post_ajax,meta=meta)

    def parse_post_ajax(self, response):

        if len(response.body) == 0:
            self.item_status["status"] = 3

            self.con.hmset(self.jobid, self.item_status)  ##3代表爬虫内部解析错误##6代表

            logging.warning("formRequest login_189_cn_login_ajax error##############")
            return

        meta = response.meta

        html = response.body.decode("utf-8")

        htmls = json.dumps(html)

        hjson = json.loads(htmls)

        d = eval(hjson)
        # ProvinceID = hjson["ProvinceID"]
        ProvinceID = d["ProvinceID"]

        self.form_data_login = {
            "Account": self.tel,
            "UType": "201",
            "ProvinceID": ProvinceID,
            "AreaCode": "",
            "CityNo": "",
            "RandomFlag": "0",
            "Password": self.crypt_password,
            "Captcha": ""
        }
        from_data = {
            "m": "loadlogincaptcha",
            "Account": self.tel,
            "UType": "201",
            "ProvinceID": ProvinceID,
            "AreaCode":"",
            "CityNo":"",
        }
        yield FormRequest(url="http://login.189.cn/login/ajax", dont_filter=True, formdata=from_data,
                          callback=self.parse_post_ajax_captcha,meta=meta)
    def parse_post_ajax_captcha(self, response):
        if len(response.body) == 0:
            self.item_status["status"] = 3

            self.con.hmset(self.jobid, self.item_status)  ##3代表爬虫内部解析错误##6代表

            logging.warning("formRequest parse_post_ajax_captcha error##############")
            return
        meta = response.meta
        html = response.body.decode("utf-8")

        htmls = json.dumps(html)

        hjson = json.loads(htmls)

        d = eval(hjson)
        # ProvinceID = hjson["ProvinceID"]
        CaptchaFlag = int(d["CaptchaFlag"])
        FailTimes = int(d["FailTimes"])
        if FailTimes >= 5:
            self.item_status["status"] = 3
            self.con.hmset(self.jobid, self.item_status)  ##3
            self.con.hmset(self.jobid, {"status_value": u"登陆密码错误次数大于等于5次，账号已锁定，今日无法登陆"})
            return
        if CaptchaFlag == 1:

            random_a=  random.random()
            random_int = random.randint(100, 999)
            random_18 = "%s%s"%(random_a,random_int)

            url_captcha = "http://login.189.cn/captcha?%s&source=login&width=100&height=37&%s"%(meta["data_guid"],random_18)

            yield Request(url=url_captcha, callback=self.parsecode, dont_filter=True, cookies=self.sesss)
        else:

            yield FormRequest(url=self.login_url, dont_filter=True, formdata=self.form_data_login, callback=self.parse_homepage)

    def parsecode(self, response):

        self.con.hmset(self.jobid, {"status_value": u"正在获取验证码"})

        imgBuf = StringIO.StringIO(response.body)

        params = {
            'user': '**************',
            'pass': '**************',
            'softid': '402f5b2a3709ded763bf48819cae6c51',
            'codetype': '1004',
            'file_base64': base64.b64encode(imgBuf.getvalue()),
            'str_debug': '4',
        }

        headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

        code_url = "http://upload.chaojiying.net/Upload/Processing.php"

        yield FormRequest(url=code_url, formdata=params, headers=headers, callback=self.get_codes, dont_filter=True,
                              meta={'dont_merge_cookies': True}, cookies={})

    def get_codes(self,response):

        self.sess = {}

        cookie = [i.split(";")[0] for i in response.headers.getlist('Set-Cookie')]

        for cook in cookie:
            self.sess.update({cook[:cook.index("=")]: cook[cook.index("=") + 1:]})

        ti = int(time.time() * 1000)

        re_str = json.loads(response.body)

        if 'OK' not in re_str['err_str']:

            self.con.hmset(self.jobid, {"status_value": u"验证码服务器出现问题或者本地服务器出现问题"})

            logging.warning(msg=re_str['err_str'])

            self.con.hmset(self.jobid, {"status": 7})

            return

        else:

            key = [i for i in re_str.keys() if u'pic_s' in i ]

            self.authcode = re_str[key[0]]

            if self.authcode == "" or self.authcode is None:

                self.con.hmset(self.jobid, {"status_value": u"获取验证码内容为空"})

                yield Request(url=self.login_url, meta=self.meta, dont_filter=True, callback=self.parse)
            else:

                self.con.hmset(self.jobid, {"status_value": u"成功获取验证码"})
                self.form_data_login["Captcha"] = self.authcode

                yield FormRequest(url=self.login_url, dont_filter=True, formdata=self.form_data_login,
                                  callback=self.parse_homepage)

    def parse_homepage(self, response):

        if "http://www.189.cn" in response.body and "/login/other" in response.body and self.int_retry < 3:

            logging.warning(msg="Login dianxin error")

            self.int_retry += 1

            yield Request(url=self.login_url, meta=self.meta, dont_filter=True,callback=self.parse)
            return
        elif self.int_retry >= 3:
            self.item_status["status"] = 3
            self.con.hmset(self.jobid, self.item_status)  ##3代表重试3次登陆失败，密码错误
            # self.con.hmset(self.jobid, {"login_status": "3"})  ##1代表登陆成功
            self.con.hmset(self.jobid, {"status_value":u"登陆失败,密码错误"})
            logging.warning(msg="Login dianxin >= 3,password error##########")
            return
        else:
            self.item_status["status"] = 0

            self.con.hmset(self.jobid, self.item_status) ##0代表登陆成功，并且正在爬取
            self.con.hmset(self.jobid, {"status_value": u"登陆成功"})
            # self.con.hmset(self.jobid, {"login_status": "1"})  ##1代表登陆成功
            logging.warning(msg="Login dianxin success")


        html = HtmlXPathSelector(response)

        xiangdanchaxun_url = ''.join(html.xpath(u"//*[text()='详单查询']/@href").extract())

        #zhangdanchaxun_url = ''.join(html.xpath(u"//*[text()='账单查询']/@href").extract())

        yield Request(url=xiangdanchaxun_url, dont_filter=True,callback=self.parse_tongxin)

    def parse_tongxin(self, response):

        html = HtmlXPathSelector(response)

        huafeizhangdan_url = ''.join(html.xpath(u"//*[text()='话费账单']/@href").extract()).split("'")[1]

        self.huafeizhangdan_id = ''.join(html.xpath(u"//*[text()='话费账单']/@id").extract())

        tongxinxiangdan_url = ''.join(html.xpath(u"//*[text()='通信详单']/@href").extract()).split("'")[1]

        self.tongxinxiangdan_id = ''.join(html.xpath(u"//*[text()='通信详单']/@id").extract())

        kehuziliaoxiugai_url = ''.join(html.xpath(u"//*[text()='客户资料修改']/@href").extract()).split("'")[1]

        self.kehuziliao_id = ''.join(html.xpath(u"//*[text()='客户资料修改']/@id").extract())

        self.city_id = kehuziliaoxiugai_url.split("http://")[1].split(".")[0]

        self.tongxinxiangdan_url = urljoin(response.url, tongxinxiangdan_url)+"?fastcode=%s&cityCode=%s"%(self.tongxinxiangdan_id,self.city_id)

        self.kehuziliaoxiugai_url = urljoin(response.url, kehuziliaoxiugai_url) + "?fastcode=%s&cityCode=%s" % (self.kehuziliao_id, self.city_id)

        self.huafeizhangdan_url_2 = urljoin(response.url, huafeizhangdan_url) + "?fastcode=%s&cityCode=%s" % (self.huafeizhangdan_id, self.city_id)

        yield Request(url=self.kehuziliaoxiugai_url, dont_filter=True, callback=self.parse_ziliaoxiugai)

        yield Request(url=self.taocan_url, dont_filter=True, callback=self.parse_taocan_json)

        yield Request(self.huafei_url, dont_filter=True, callback=self.parse_huafei_json)

    def parse_huafei_json(self, response):

        if u"系统异常" in response.body.decode("utf-8"):
            self.item_status["status"] = 3
            self.con.hmset(self.jobid, self.item_status)  ##3代表爬虫内部解析错误

            logging.warning("parse_huafei_json  error!!!##############")

            return

        html = response.body.decode("utf-8")

        htmls = json.dumps(html)

        hjson = json.loads(htmls)

        try:
            hjson = eval(hjson)

            self.items["month_charge"] = hjson["obj"]["month_charge"]

            self.items["myjifen"] = hjson["obj"]["myjifen"]

        except Exception,e:
            self.item_status["status"] = 3
            self.con.hmset(self.jobid, self.item_status)  ##3代表爬虫内部解析错误

            logging.warning("parse_huafei_json error ################%s"%e.message)

            return

    def parse_taocan_json(self, response):

        if u"系统异常" in response.body.decode("utf-8"):
            self.item_status["status"] = 3
            self.con.hmset(self.jobid, self.item_status)  ##3代表爬虫内部解析错误

            logging.warning("parse_taocan_json  error!!!#################")

            return

        html = response.body.decode("utf-8")

        htmls = json.dumps(html)

        hjson = json.loads(htmls)

        try:

            hjson = eval(hjson)

            self.items["flowsBalanceAmount"] = hjson["obj"]["my189datarebean"]["flowsBalanceAmount"]

            self.items["flowsUseAmount"] = hjson["obj"]["my189datarebean"]["flowsUseAmount"]

            self.items["yvyinUsePercent"] = hjson["obj"]["my189datarebean"]["yvyinUsePercent"]

            self.items["duanxinUsePercent"] = hjson["obj"]["my189datarebean"]["duanxinUsePercent"]

            self.items["flowsUsePercent"] = hjson["obj"]["my189datarebean"]["flowsUsePercent"]

            self.items["callBalanceAmount"] = hjson["obj"]["my189datarebean"]["callBalanceAmount"]

            self.items["msgBalanceAmount"] = hjson["obj"]["my189datarebean"]["msgBalanceAmount"]

        except Exception, e:
            self.item_status["status"] = 3
            self.con.hmset(self.jobid, self.item_status)  ##3代表爬虫内部解析错误

            logging.warning("parse_taocan_json error ################%s" % e.message)

            return

    def parse_ziliaoxiugai(self, response):
        self.con.hmset(self.jobid, {"status_value": u"抓取客户个人信息"})

        html = HtmlXPathSelector(response)

        self.items["customer_name"] = ''.join(html.xpath(u"//*[text()='客户名称：']/../td[1]/text()").extract())

        self.items["customer_type"] = ''.join(html.xpath(u"//*[text()='客户类型：']/../td[2]/text()").extract())

        self.items["contact_num"] = ''.join(html.xpath(u"//*[text()='联系电话1：']/../td[1]/descendant::span/text()").extract())

        self.items["custAddress_new"] = ''.join(html.xpath(u"//*[text()='通讯地址：']/../td[2]/descendant::span/text()").extract())

        self.items["postcode"] = ''.join(html.xpath(u"//*[text()='邮政编码：']/../td[1]/descendant::span/text()").extract())

        self.items["email"] = ''.join(html.xpath(u"//*[text()='E-mail：']/../td[2]/descendant::span/text()").extract())

        self.items["network_time"] = ''.join(html.xpath(u"//*[text()='入网时间：']/../td[1]/text()").extract())

        yield Request(self.huafeizhangdan_url_2, dont_filter=True,callback=self.parse_huafeizhangdan)

    def parse_huafeizhangdan(self, response):
        self.con.hmset(self.jobid, {"status_value": u"抓取客户话费账单信息"})

        url = urljoin(response.url, self.start_huafei_url)

        form_data = {
            "accNum":self.tel,
            "requestFlag":"synchronization",
        }

        yield FormRequest(url=url, formdata=form_data, dont_filter=True, callback=self.parse_huafeizhangdan_2)

        yield Request(url=self.tongxinxiangdan_url, dont_filter=True, callback=self.parse_tongxinxiangdan)

    def parse_huafeizhangdan_2(self, response):

        html = HtmlXPathSelector(response)

        consumer_huafei = []

        for html_items in html.xpath("//*[@id='userBill']/tr"):

            htmlitems = {}

            htmlitems["consumer_month"] = ''.join(html_items.xpath(".//td[1]/text()").extract())

            htmlitems["consumer_amount"] = ''.join(html_items.xpath(".//td[2]/text()").extract())

            consumer_huafei.append(htmlitems)

        self.items["consumer_huafei"] = consumer_huafei

    def parse_tongxinxiangdan(self, response):
        self.con.hmset(self.jobid, {"status_value": u"抓取客户通话详单"})

        gethalfyearmonth = Util().gethalfyearmonth()

        self.int_tongxinxiangdan = 1

        for yearmonths in gethalfyearmonth:

            yearmonth = json.dumps(yearmonths)

            yearmonth = json.loads(yearmonth)

            start_day = yearmonth.keys()[0]

            end_day = yearmonth[yearmonth.keys()[0]]

            start_year = start_day.split("-")[0]

            start_month = start_day.split("-")[1]

            nums = ["01", "02", "03", "04", "05", "06", "07", "08", "09"]
            for num in nums:
                if start_month in num:
                    start_month = num.split("0")[1]

            #qryMonth = start_year + "%E5%B9%B4" + start_month + "%E6%9C%88"

            qryMonth = start_year + u"年" + start_month + u"月"

            startTime = start_day.split("-")[2]

            endTime = end_day.split("-")[2]

            req_url = urljoin(response.url,self.tonghuajilu_url) + "?requestFlag=synchronization&billDetailType=1&qryMonth=%s&startTime=%s&accNum=%s&endTime=%s" % (qryMonth, startTime, self
.tel, endTime)
            item_comm = {
                "comm_list": [],
                "int_page": "1",
                "tongxin_url": req_url,
                "requestFlag": "synchronization",
                "billDetailType": "1",
                "qryMonth": qryMonth,
                "startTime": startTime,
                "accNum": self.tel,
                "endTime": endTime,
                "int_tongxinxiangdan":"1",
            }

            form_data = {
                "requestFlag": "synchronization",
                "billDetailType": "1",
                "qryMonth": qryMonth,
                "startTime": startTime,
                "accNum": self.tel,
                "endTime": endTime,
            }
            yield FormRequest(urljoin(response.url, self.tonghuajilu_url),formdata=form_data, dont_filter=True,
                             callback=self.parse_tongxinxiangdan_4, meta={"item_comm": item_comm})
            #time.sleep(0.0001 * random.randint(5100, 14300))

    def parse_pass(self, response):

        html = HtmlXPathSelector(response)

    def parse_tongxinxiangdan_4(self,response):

        yield Request(url="http://www.189.cn/dqmh/web/zhidao/proxy.html?ran=%s" % int(time.time() * 1000),callback=self.parse_pass,dont_filter=True)

        f = open("parse_tongxinxiangdan_4.html", "w")
        f.write(response.body)
        f.close()

        item_comm = response.meta["item_comm"]

        if "系统正忙，请稍后再试" in response.body and "查询失败" in response.body:

            form_data = {
                "requestFlag": item_comm["requestFlag"],
                "billDetailType": item_comm["billDetailType"],
                "qryMonth": item_comm["qryMonth"],
                "startTime": item_comm["startTime"],
                "accNum": item_comm["accNum"],
                "endTime": item_comm["endTime"],
            }
            if "1" not in item_comm["int_page"]:

                form_data["int_page"] = item_comm["int_page"]

            int_tongxinxiangdan = int(item_comm["int_tongxinxiangdan"])
            int_tongxinxiangdan += 1
            item_comm["int_tongxinxiangdan"] = str(int_tongxinxiangdan)

            if int_tongxinxiangdan <= 5:

                #time.sleep(0.0001 * random.randint(15100, 34300))

                yield FormRequest(response.url, formdata=form_data,dont_filter=True,callback=self.parse_tongxinxiangdan_4, meta={"item_comm": item_comm})
            else:

                logging.warning(u"tongxinxiangdan error!#########重试5次后########系统正忙，请稍后再试")

            return

        # print response.body.decode("utf8","ignore").encode("gbk")
        html = HtmlXPathSelector(response)

        for comm_items in html.xpath("//*[@class='ued-table']/descendant::tr[position()>1]"):

            commitems ={}

            commitems["order_number"] = ''.join(comm_items.xpath(".//td[1]/text()").extract())

            commitems["call_type"] = ''.join(comm_items.xpath(".//td[2]/text()").extract())

            commitems["data_call_type"] = ''.join(comm_items.xpath(".//td[3]/text()").extract())

            commitems["call_site"] = ''.join(comm_items.xpath(".//td[4]/text()").extract())

            commitems["each_other_number"] = ''.join(comm_items.xpath(".//td[5]/text()").extract())

            commitems["call_start_time"] = ''.join(comm_items.xpath(".//td[6]/text()").extract())

            commitems["call_charge"] = ''.join(comm_items.xpath(".//td[7]/text()").extract())

            commitems["toll_call_fee"] = ''.join(comm_items.xpath(".//td[8]/text()").extract())

            commitems["call_time_seconds"] = ''.join(comm_items.xpath(".//td[9]/text()").extract())

            commitems["cost"] = ''.join(comm_items.xpath(".//td[10]/text()").extract())

            item_comm["comm_list"].append(commitems)

        next_page = ''.join(html.xpath(u"//*[text()='下一页']/@href").extract())

        if next_page:
            int_page = int(item_comm["int_page"])
            int_page += 1
            item_comm["int_page"] = str(int_page)

            int_tongxinxiangdan = 1
            item_comm["int_tongxinxiangdan"] = str(int_tongxinxiangdan)

            form_data = {
                "requestFlag": item_comm["requestFlag"],
                "billDetailType": item_comm["billDetailType"],
                "qryMonth": item_comm["qryMonth"],
                "startTime": item_comm["startTime"],
                "accNum": item_comm["accNum"],
                "endTime": item_comm["endTime"],
                "billPage": item_comm["int_page"],
            }
            #time.sleep(0.0001 * random.randint(15100, 54300))
            yield FormRequest(response.url, formdata=form_data, dont_filter=True, callback=self.parse_tongxinxiangdan_4, meta={"item_comm": item_comm})
        else:
            self.items["comm"].append(item_comm)

        del response

    def spider_idle(self):

        if self.ti == 1:
            self.con.hmset(self.jobid, {"status_value": u"抓取完毕"})

            if self.items == {}:

                self.con.hmset(self.jobid, {"status": 3})

                logging.warning(msg="dianxin spider is error!")

            elif self.item_status["status"] == 0:

                self.con.hmset(self.jobid, {"status": 1})

                self.con.hmset(self.jobid, {"item": self.items})
                logging.warning(msg="dianxin spider is OK!")
            else:

                item = {"item": self.items}

                self.con.hmset(self.jobid, item)
                logging.warning(msg="dianxin spider is error!")

            logging.warning(msg="{%s} spider idle" % self.name)

            if self.items:

                del self.items

                self.items = {}
        self.schedule_next_requests()

        self.ti = 0

        raise DontCloseSpider

    def spider_closed(self, spider):

        self.con.hmset(self.jobid, {"status_value": u"抓取完毕"})

        if self.item_status["status"] == 0:

            self.item_status["status"] = 1
            self.con.hmset(self.jobid, self.item_status)  ##1代表爬取完毕

            logging.warning(msg="dianxin spider is OK!")
        else:
            #self.con.hmset(self.jobid, self.item_status)

            logging.warning(msg="dianxin spider is error!")

        if self.items != {}:
            item = {"item": self.items}
            self.con.hmset(self.jobid, item)

            line = None
            for key in self.items:
                if line != None:
                    line += ","
                else:
                    line = "{"
                line += "'" + key + "':" + str(self.items[key])
            line += "}"
            print line

        logging.warning(msg="dianxin spider closed")
