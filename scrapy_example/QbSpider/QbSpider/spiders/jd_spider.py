# coding=utf-8
import sys,os
sys.path.append(os.path.abspath("../"))
import logging
import time
from base64 import b64decode,b64encode
# from os.path import join,dirname
import rsa
from Crypto.PublicKey import RSA
from scrapy.http import Request,FormRequest
from scrapy.selector.lxmlsel import HtmlXPathSelector
#from scrapy.spider import CrawlSpider
# from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from QbSpider.utils.utils import Util
import random
from scrapy import signals
from urlparse import urljoin
import StringIO
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
from QbSpider.utils.chaojiying import Chaojiying_Client
from QbSpider.scrapy_redis.spiders import Spiders
from scrapy.spiders import Spider
from scrapy.exceptions import DontCloseSpider
#lpush 先进后出
import urllib
import json
import base64

# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
price_re = "[0-9]\\d*\\.?\\d*"

'''
        # try:
        #     dcap = dict(DesiredCapabilities.PHANTOMJS)
        #     dcap["phantomjs.page.settings.userAgent"] = (
        #         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
        #     )
        #     self.browser = webdriver.PhantomJS(executable_path=join(dirname(__file__),"phantomjs.exe"), desired_capabilities=dcap)
        #     logging.warning('Phantomjs initialize successed')
        # except Exception, e:
        #     logging.warning('Phantomjs initialize failed : %s'%e)
        # self.queuess = SpiderPriorityQueue(server=self.con, spider=JdItemSpider(),
        #                               key="jingdong_queue_producer")
        # #self.browser.get(self.login_url)
        #
        # for cookie in self.browser.get_cookies():
        #
        #     sess[cookie['name']] = str(cookie['value'])

        #hxs = HtmlXPathSelector(text=self.browser.page_source)

        # class JdItemSpider(RedisSpider):
        #
        #     name = "jingdong_detail"
        #
        #
        #     allowed_domains = []
        #
        #     custom_settings = {
        #         "SCHEDULER_QUEUE_KEY": "jingdong_queue_producer",
        #         "REFERER_ENABLED": True
        #     }
        #
        #     ur = "https://www.jd.com/"
        #
        #     def __init__(self, *a, **kw):
        #         super(JdItemSpider, self).__init__(*a, **kw)
        #         self.con = rcu().get_redis()

        #self.queuess.push(Request(url=urljoin(self.start_urls[0],order_url),headers=response.request.headers,meta={"jobid":self.jobid}))
'''

class JdSpider(Spiders):

    name = "jingdong"

    redis_key = "jingdongqueue_bigdata"

    # queue_key = redis_key

    allowed_domains = []

    start_urlss = ["https://www.jd.com/"]

    logins_url = "https://passport.jd.com/new/login.aspx"

    custom_settings = {
        "COOKIES_ENABLED":True,
        "REDIRECT_ENABLED":False,
        "REFERER_ENABLED":True,
        "USEPROXYHIGHLEVEL":False,
        "USELOCALIP":1
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(JdSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def __init__(self, *a, **kw):
        super(JdSpider, self).__init__(*a, **kw)
        self.utils = Util()
        self.con = rcu().get_redis()
        self.con.ping()
        self.code_url = "https://passport.jd.com/uc/showAuthCode?r=%s&version=%s"
        self.login_url = 'https://passport.jd.com/uc/loginService?uuid=%s&&r=%s&version=2015'
        self.authcode_url = "https://authcode.jd.com/verify/image?a=1&acid=%s&uid=%s&yys=%s"
        self.dangerurl = "https://safe.jd.com/dangerousVerify/index.action?username=%s"
        self.sendcodeurl = "https://safe.jd.com/findPwd/getCode.action?k=%s"
        self.validatecodeurl = "https://safe.jd.com/findPwd/validFindPwdCode.action?code=%s&k=%s&eid=undefined&fp=undefined"
        self.homeurl = "https://home.jd.com/"
        self.logouturl = "https://passport.jd.com/uc/login?ltype=logout"
        #self.queues = SpiderPriorityQueue(server=self.con,spider=JdItemSpider(),key="%s_queue"%self.name.split("_")[0])
        self.ti = 0



    # def start_requests(self):
    #
    #     yield Request(self.logins_url)

    def parse(self,response):

        self.item = {}

        self.meta = response.meta

        self.ti = 1

        #self.passwd = urllib.unquote(self.settings.get("PASSWD", None))  # .decode("ascii").encode("utf8")

        self.passwd = response.meta["PASSWORD"]

        #self.username = urllib.unquote(self.settings.get("USERNAME", None))  # .decode("ascii").encode("utf8")

        self.username = response.meta["USERNAME"]

        #self.jobid = urllib.unquote(self.settings.get("JOBID", None))  # .decode("ascii").encode("utf8")

        self.jobid = response.meta["JOBID"]

        #self.vercode = urllib.unquote(self.settings.get("VERCODE", None))  # .decode("ascii").encode("utf8")

        self.vercode = response.meta["VERCODE"]

        self.spidertype = response.meta["SPIDERTYPE"]

        #self.con.hmset(self.jobid, {"status": 0})

        self.con.hmset(self.jobid,{"status_value":u"京东爬虫爬行中"})

        hxs = HtmlXPathSelector(response)

        pubKey = "".join(hxs.xpath('//input[@name="pubKey"]/@value').extract())

        keyDER = b64decode(pubKey)

        keyPub = RSA.importKey(keyDER)

        nloginpwd = b64encode(rsa.encrypt(b"%s" % self.passwd, keyPub))

        self.uuid = "".join(hxs.xpath('//input[@name="uuid"]/@value').extract())

        fp = "".join(hxs.xpath('//input[@name="fp"]/@value').extract())

        _t = "".join(hxs.xpath('//input[@name="_t"]/@value').extract())

        loginType = "".join(hxs.xpath('//input[@name="loginType"]/@value').extract())

        eid = "".join(hxs.xpath('//input[@name="eid"]/@value').extract())

        self.authcode = ""

        self.post_data = {

            "uuid": self.uuid,
            "eid": eid,
            "fp": fp,
            "_t": _t,
            "loginType": loginType,
            "loginname": "%s" % self.username,
            "nloginpwd": nloginpwd,
            "chkRememberMe": "on",
            "authcode": self.authcode,
        }

        auth_dat = {
            'loginName': self.username,
        }

        self.sess = {}

        cookie = [i.split(";")[0] for i in response.headers.getlist('Set-Cookie')]

        for cook in cookie:

            self.sess.update({cook[:cook.index("=")]: cook[cook.index("=")+1:]})

        code_url = self.code_url % (random.random(), 2015)

        yield FormRequest(url=code_url, cookies=self.sess, formdata=auth_dat, callback=self.checkauthcode,dont_filter=True)

    def checkauthcode(self,response):

        js = self.utils.obtain_json(response.body)

        if js.get('verifycode',None) is False:

            self.con.hmset(self.jobid, {"status_value": u"京东当前登录账户无需验证码,开始登陆"})

            login_url = self.login_url % (self.uuid, random.random())

            yield FormRequest(url=login_url, formdata=self.post_data, cookies=self.sess, callback=self.parse_item,dont_filter=True)

        else:

            self.con.hmset(self.jobid, {"status_value": u"京东当前登录账户需要验证码,获取验证码"})

            logging.warning(msg="Jd login need checkcode")

            yys = int(time.time() * 1000)

            authcode_url =  self.authcode_url % (self.uuid, self.uuid, yys)

            yield Request(authcode_url,callback=self.parsecode,dont_filter=True,cookies=self.sess)

    def parsecode(self, response):

        self.con.hmset(self.jobid, {"status_value": u"正在获取验证码"})

        imgBuf = StringIO.StringIO(response.body)

        params = {
            'user': '**********',
            'pass': '**********',
            'softid': '402f5b2a3709ded763bf48819cae6c51',
            'codetype': '1004',
            'file_base64':base64.b64encode(imgBuf.getvalue()),
            'str_debug':'4',
        }

        headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

        code_url = "http://upload.chaojiying.net/Upload/Processing.php"

        yield FormRequest(url=code_url,formdata=params,headers=headers,callback=self.get_codes,dont_filter=True,meta={'dont_merge_cookies':True},cookies={})

    def get_codes(self,response):

        #re_str = chaojiying.PostPic(imgBuf, 1004)

        re_str = json.loads(response.body)

        if 'OK' not in re_str['err_str']:

            self.con.hmset(self.jobid, {"status_value": u"京东当前登录账户需要验证码,获取验证码失败，验证码服务器可能挂了"})

            logging.warning(msg=re_str['err_str'])

            self.con.hmset(self.jobid, {"status": 7})

            return

        else:

            key = [i for i in re_str.keys() if u'pic_s' in i ]

            self.authcode = re_str[key[0]]

            if self.authcode == "" or self.authcode is None:

                self.con.hmset(self.jobid, {"status_value": u"京东当前登录账户需要验证码,获取验证码为空"})

                yys = int(time.time() * 1000)

                authcode_url = self.authcode_url % (self.uuid, self.uuid, yys)

                #return

                yield Request(authcode_url, callback=self.parsecode,cookies=self.sess,dont_filter=True)


            else:

                self.con.hmset(self.jobid, {"status_value": u"京东当前登录账户需要验证码,成功获取验证码,开始登陆"})

                self.post_data.update({"authcode": self.authcode})

                login_url = self.login_url % (self.uuid, random.random())

                yield FormRequest(login_url, formdata=self.post_data, cookies=self.sess, callback=self.parse_item,dont_filter=True)

    def parse_item(self,response):

        if "success" in response.body and "//www.jd.com" in response.body:

            logging.warning(msg="Login jd success")

            #res_headers = response.headers.getlist('Set-Cookie')

            # self.sess = {}
            #
            # cookie = [i.split(";")[0] for i in headerss] + response.request.headers.getlist('Cookie')[0].split(";")
            #
            # for cook in cookie:
            #
            #     self.sess.update({cook[:cook.index("=")]: cook[cook.index("=") + 1:].replace('"',"")})

            # req_headers = dict(response.request.headers)
            #
            # Cookie = req_headers['Cookie']+[";".join([i.split(";")[0] for i in res_headers])]
            #
            # req_headers.update({'Cookie':Cookie})
            #
            # req_headers.update({'Referer': None})
            #
            # sess = {}
            #
            # for k,v in req_headers.iteritems():
            #
            #     if v is None:
            #         sess.update({k:""})
            #     else:
            #         sess.update({k:v[0]})

            #if self.spidertype == "realtime":

            #self.items.append({"status":1})

            self.con.hmset(self.jobid, {"status_value": u"京东当前登录账户登陆成功"})

            # self.con.hmset(self.jobid, {"status": 1})

            self.con.hmset(self.jobid, {"status":0})

            # # yield Request(url=self.logouturl,callback=None)
            #
            # return

            #else:

            yield Request(url=self.homeurl, callback=self.parse_ballancecount,dont_filter=True)

        elif "verifycode" in response.body or "emptyAuthcode" in response.body:

            self.con.hmset(self.jobid, {"status_value": u"京东当前登录账户需要验证码,当前验证码不正确,即将重新获取验证码"})

            yys = int(time.time() * 1000)

            logging.warning(msg="Login jd verifycode error")

            authcode_url = self.authcode_url % (self.uuid, self.uuid, yys)

            yield Request(authcode_url, callback=self.parsecode, dont_filter=True,cookies=self.sess)

        elif "pwd" in response.body:

            self.con.hmset(self.jobid, {"status_value": u"京东当前登录账户用户名或者密码不正确"})

            logging.warning(msg="Login jd passwd error")

            self.con.hmset(self.jobid, {"status": 3})

            return

        elif "username" in response.body:

            self.con.hmset(self.jobid, {"status_value": u"京东当前页面刷新次数过多,需要重新刷新"})

            yield Request(self.logins_url,dont_filter=True,callback=self.parse,meta=self.meta)

        else:

            if "safe.jd.com/dangerousVerify/index.action" in response.body:

                self.con.hmset(self.jobid, {"status_value": u"京东当前用户账号存在安全问题,即将发送验证码,验证码登陆"})

                yield Request(url=self.dangerurl%self.username,callback=self.sendphonecode,dont_filter=True)

                self.con.hmset(self.jobid, {"status": 2})

                return


    def sendphonecode(self,response):

        hxs = HtmlXPathSelector(response)

        sendphonecodekey = "".join(hxs.xpath("translate(//*[@id='sendMobileCode']/@href,'javascript:sendFindPwdCode(|);','')").extract()).replace("'","")

        if self.vercode is None:

            item = {}

            logging.warning(msg="Login jd need phone vercode, will send phone code to user phone ")

            item["status"] = 2

            item["jobid"] = self.jobid

            self.con.hmset(self.jobid, {"status_value": u"京东当前用户账号存在安全问题,已发送手机验证码"})

            self.con.hmset(self.jobid, {"status":2})

            yield Request(url=self.sendcodeurl % sendphonecodekey,callback=None,dont_filter=True)

        else:

            self.con.hmset(self.jobid, {"status_value": u"京东当前用户账号存在安全问题,即将发送验证码,验证码登陆"})

            yield Request(url=self.validatecodeurl%(self.vercode,sendphonecodekey),callback=self.checkphonekey,dont_filter=True)

    def checkphonekey(self,response):

        if  "codeFailure" in response.body:

            self.con.hmset(self.jobid, {"status_value": u"手机验证码不正确"})

            self.vercode = None

            self.con.hmset(self.jobid, {"status": 4})

            yield Request(url=self.dangerurl % self.username, callback=self.sendphonecode,dont_filter=True)

            return

        else:

            self.con.hmset(self.jobid, {"status_value": u"手机验证码正确,即将进入主页"})

            yield Request(url=self.homeurl, callback=self.parse_ballancecount,dont_filter=True)

    def parse_ballancecount(self, response):

        #self.con.hmset(self.jobid, {"status": 0})

        self.con.hmset(self.jobid, {"status_value": u"正在获取个人白条信息"})

        item = {}

        hxs = HtmlXPathSelector(response)

        item["spidertime"] = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

        item["username"] = self.username

        item["passwd"] = self.passwd

        item["usernickname"] = "".join(hxs.xpath("//div[@class='u-name']/a/text()").re(r'\S+'))

        item["userrank"] = "".join(hxs.xpath("//div[@class='u-level']/span/a/text()").re(r'\S+'))

        item["balance"] = "".join(hxs.xpath("//a[@id='BalanceCount']/text()").re(r'\S+'))

        item["baitiaobalance"] = "".join(hxs.xpath("//span[@class='baitiao-limit']/text()").re(r'\S+'))

        item["wallet"] = "".join(hxs.xpath("//div[@id='balance']/a[2]/em/text()").re(r'\S+'))

        item["yesprofit"] = "".join(hxs.xpath("//div[@class='ftx01 profit']/a/text()").re(r'\S+'))

        userinfo_url = 'https://i.jd.com/user/info'

        yield Request(url=userinfo_url,callback=self.parse_userinfo,meta={"item":item},dont_filter=True)


    def parse_userinfo(self,response):

        self.con.hmset(self.jobid, {"status_value": u"正在获取个人基本信息"})

        hxs = HtmlXPathSelector(response)

        item = response.meta["item"]

        item["userloginname"] = "".join(hxs.xpath("//div[@id='aliasBefore']/strong/text()").re(r'\S+'))

        item["usermail"] = "".join(hxs.xpath(u"//span[contains(text(),'邮箱：')]/following-sibling::div[1]/div/strong/text()").re(r'\S+'))

        item["userrealname"] = "".join(hxs.xpath("//input[@id='realName']/@value").re(r'\S+'))

        item["usertype"] = "".join(hxs.xpath(u"translate(//div[@class='info-m']/div[contains(text(),'会员类型：')]/text(),'会员类型：','')").re(r'\S+'))

        safetycenter_url = "https://safe.jd.com/user/paymentpassword/safetyCenter.action"

        yield Request(url=safetycenter_url,callback=self.parse_safetycenter,meta={"item":item},dont_filter=True)


    def parse_safetycenter(self,response):

        self.con.hmset(self.jobid, {"status_value": u"正在获取个人安全中心信息"})

        hxs = HtmlXPathSelector(response)

        item = response.meta["item"]

        item["userphone"] = "".join(hxs.xpath("//strong[@id='mobile']/text()").re(r'\S+'))

        item["useridcard"] = "".join(hxs.xpath(u"//span[contains(text(),'您认证的实名信息：')]/following::strong[2]/text()").re(r'\S+'))

        item["safelevel"] = "".join(hxs.xpath("//strong[contains(@class,'rank-text')]/text()").re(r'\S+'))

        item["namecert"] = True if "".join(hxs.xpath(u"//strong[text()='实名认证']/preceding-sibling::s[1]/@class").re(r'\S+')) == "icon-01" else False

        userscore_url = "https://home.jd.com/getUserVerifyRight.action"

        yield Request(url=userscore_url,callback=self.parse_user_verifyscore,meta={"item":item},dont_filter=True)

    def parse_user_verifyscore(self, response):

        self.con.hmset(self.jobid, {"status_value": u"正在获取小白分数"})

        j_read = json.loads(response.body)

        item = response.meta["item"]

        item["userverscore"] = j_read.get("content","")

        loginrecord_url = "https://safe.jd.com/user/paymentpassword/showLoginHistory.action"

        yield Request(url=loginrecord_url,callback=self.parse_loginrecord,dont_filter=True,meta={"item":item})

    def parse_loginrecord(self,response):

        self.con.hmset(self.jobid, {"status_value": u"正在获取登陆记录信息"})

        item = response.meta["item"]

        hxs = HtmlXPathSelector(response)

        login_records = []

        for record in hxs.xpath(u"//th[contains(text(),'登录时间')]/../following-sibling::tr"):

            records = {}

            records["login_time"] = "".join(record.xpath(".//td[1]/text()").extract())

            records["login_location"] = "".join(record.xpath(".//td[2]/text()").extract())

            records["login_ip"] = "".join(record.xpath(".//td[3]/text()").extract())

            records["login_type"] = "".join(record.xpath(".//td[4]/text()").extract())
        
            login_records.append(records)

        item["login_records"] = login_records

        address_url = "https://easybuy.jd.com/address/getEasyBuyList.action"

        yield Request(url=address_url,callback=self.parse_address,meta={"item":item},dont_filter=True)


    def parse_address(self,response):

        self.con.hmset(self.jobid, {"status_value": u"正在获取个人地址列表"})

        item = response.meta["item"]

        addresss = []

        hxs = HtmlXPathSelector(response)

        for address in hxs.xpath("//div[@class='sm easebuy-m ']"):
            addressitem = {}

            defaultaddress = "".join(address.xpath(".//div[@class='smt'][1]/h3[1]/span[1]/text()").extract())

            addressitem["defaultaddress"] = "True" if u"默认地址" in defaultaddress else "False"

            addressitem["receivername"] = "".join(address.xpath(u".//span[contains(text(),'收货人：')]/following-sibling::div[1]/text()").re(r'\S+'))

            addressitem["rceiverdistrict"] = "".join(
                address.xpath(u".//span[contains(text(),'所在地区：')]/following-sibling::div[1]/text()").re(r'\S+'))

            addressitem["receiveraddress"] = "".join(
                address.xpath(u".//span[contains(text(),'地址：')]/following-sibling::div[1]/text()").re(r'\S+'))

            addressitem["receiverphone"] = ";".join(
                address.xpath(u".//span[contains(text(),'手机：')]/following-sibling::div[1]/text()").re(r'\S+'))

            addressitem["receivertelephone"] = "".join(
                address.xpath(u".//span[contains(text(),'固定电话：')]/following-sibling::div[1]/text()").re(r'\S+'))

            addressitem["receivermail"] = "".join(
                address.xpath(u".//span[contains(text(),'电子邮箱：')]/following-sibling::div[1]/text()").re(r'\S+'))

            addresss.append(addressitem)

        item["all_address"] = addresss

        self.item = item

        order_url = "https://order.jd.com/center/list.action"

        yield Request(url=order_url, callback=self.parse_order_year,dont_filter=True)

    def parse_order_year(self,response):

        self.order_list = []

        self.con.hmset(self.jobid, {"status_value": u"正在获取订单列表"})

        hxs = HtmlXPathSelector(response)

        order_urls = hxs.xpath("//div[@class='time-list']/ul/li[position()>1]/a/@_val").extract()[0:2]

        order_url = "https://order.jd.com/center/list.action?search=0&d="

        for urls in order_urls:

            yield Request(url=order_url+urls,callback=self.parse_order_list,dont_filter=True)

    def parse_order_list(self,response):

        self.con.hmset(self.jobid, {"status_value": u"正在分析订单列表页"})

        hxs = HtmlXPathSelector(response)

        orders_urls = hxs.xpath("//a[@name='orderIdLinks']/@href").extract()

        order_status = [x.replace("\r","").replace("\n","").replace(" ","").replace("\t","") for x in hxs.xpath("//div[@class='status']/span[contains(@class,'order-status')]/text()").extract()]

        url_status = dict(zip(orders_urls,order_status))

        headers = dict(response.request.headers)

        headers.update({"Referer":None})

        self.sess = {}

        cookie = response.request.headers.getlist('Cookie')[0].split(";")

        for cook in cookie:

            self.sess.update({cook[:cook.index("=")]: cook[cook.index("=") + 1:].replace('"',"")})

        for order_url in orders_urls:

            if "orderId=" in order_url or "orderid" in order_url:

                #self.queues.push(Request(url=urljoin(self.start_urls[0],order_url),meta={"jobid":self.jobid},headers=headers))

                yield Request(url=urljoin(self.start_urlss[0],order_url),cookies=self.sess,meta={"jobid":self.jobid,"order_status":url_status[order_url]},callback=self.parse_items)

        next_page_url = hxs.xpath("//a[@class='next']/@href").extract()

        if next_page_url:

            for next_url in next_page_url:

                if next_url:

                    yield Request(url=urljoin(self.start_urlss[0],next_url),callback=self.parse_order_list,cookies=self.sess,dont_filter=True)



    def parse_items(self, response):

        self.con.hmset(self.jobid, {"status_value": u"正在获取订单信息"})

        self.jobid = response.meta["jobid"]

        order_status = response.meta["order_status"]

        item= {}

        hxs = HtmlXPathSelector(response)

        item["url"] = response.url

        item["orderid"] = "".join(hxs.xpath(u"//input[@id='orderid']/@value|//div[contains(@class,'w o-detail')]/@orderid|//div[contains(text(),'订单号：')]/text()").re(r"%s"%price_re))

        if item["orderid"] == "":

            return Request(url=response.url,meta={"jobid":self.jobid,"order_status":order_status},callback=self.parse_items,dont_filter=True,cookies=self.sess)

        item["ordertime"] = "".join(hxs.xpath(u"translate(//li[contains(text(),'下单时间：')]/text()|//input[contains(@id,'datesubmit-')]/@value|//td[contains(text(),'下单时间')]/following-sibling::td[1]/text(),'下单时间：','')").re(r'\S+'))

        item["ordercount"] = "".join(hxs.xpath(u"translate(//li[contains(text(),'充值面额：')]/text()|//span[contains(text(),'商品总额：')]/following-sibling::div[1]/span/text()|//td[contains(text(),'商品金额')]/following-sibling::td[1]/strong/text(),'充值面额：','')").re(r"%s"%price_re))

        item["orderstatus"] = order_status

        item["expresstype"] = "".join(hxs.xpath(u"translate(//li[contains(text(),'送货方式：')],'送货方式：','')").re(r'\S+'))

        item["expressfee"] = "".join(hxs.xpath(u"//*[contains(text(),'运费：')]/following-sibling::div[1]/text()").re(r"%s"%price_re))

        if "home.jd." in response.url:

            item["receivername"] = "".join(hxs.xpath(
                u"//div[contains(text(),'收货人信息：')]/following-sibling::div[1]/text()").re(r'([\S\s]+?)（'))

            item["receiverphone"] = ";".join(hxs.xpath(
                u"//div[contains(text(),'收货人信息：')]/following-sibling::div[1]/text()").re(r"（([\S\s]+?)）"))

            item["receiveraddress"] = "".join(hxs.xpath(
                u"//div[contains(text(),'收货地址：')]/following-sibling::div[1]/text()").re(r'\S+'))

            item["receiveridno"] = "".join(hxs.xpath(
                u"translate(//div[contains(text(),'收货人信息：')]/following-sibling::div[2]/text(),'，','')").re(r"\S+"))

            item["paycount"] = "".join(hxs.xpath(
                u"//div[contains(text(),'应付金额：')]/following-sibling::div[1]/b/text()").re(r'%s' % price_re))

        else:

            item["paycount"] = "".join(hxs.xpath(
                u"translate(//li[contains(text(),'在线支付：')]/text()|//span[contains(text(),'应支付金额：')]/following-sibling::div[1]/span/text()|//td[contains(text(),'商品金额')]/following-sibling::td[1]/strong/text(),'在线支付：','')").re(
                r'%s' % price_re))

            item["receiveridno"] = ""

            item["receivername"] = "".join(hxs.xpath(u"//span[contains(text(),'收货人：')]/following-sibling::div[1]/text()|//td[contains(text(),'收货人姓名')]/following-sibling::td[1]/text()").re(r'\S+'))

            item["receiverphone"] = ";".join(hxs.xpath(u"translate(//li[contains(text(),'手机号码：')]/text()|//span[contains(text(),'手机号码：')]/following-sibling::div[1]/text()|//td[contains(text(),'固定电话')]/following-sibling::td[1]/text(),'手机号码：','')").re(r"\S+"))

            item["receiveraddress"] = "".join(hxs.xpath(u"//span[contains(text(),'地址：')]/following-sibling::div[1]/text()|//td[contains(text(),'地址')]/following-sibling::td[1]/text()").re(r'\S+'))

        item["paytime"] = "".join(hxs.xpath(u"//span[contains(text(),'付款时间：')]/following-sibling::div[1]/text()|//td[contains(text(),'下单时间')]/following-sibling::td[1]/text()").re(r'\S+'))

        item["billtype"] = "".join(hxs.xpath(u"//span[contains(text(),'发票类型：')]/following-sibling::div[1]/text()|//td[contains(text(),'发票类型')]/following-sibling::td[1]/text()").re(r'\S+'))

        item["billtitle"] = "".join(hxs.xpath(u"//span[contains(text(),'发票抬头：')]/following-sibling::div[1]/text()|//td[contains(text(),'发票抬头')]/following-sibling::td[1]/text()").re(r'\S+'))

        item["billcontent"] = "".join(hxs.xpath(u"//span[contains(text(),'发票内容：')]/following-sibling::div[1]/text()|//td[contains(text(),'发票内容')]/following-sibling::td[1]/text()").re(r'\S+'))

        _item = []

        for goods in hxs.xpath("//tr[contains(@class,'product-')]|//table[@class='tb-void tb-none']/tbody/tr|//td[@class='itemName']/../following-sibling::tr"):

            _goods = {}

            _goods["itemname"] = "".join(goods.xpath(".//a[contains(@href,'item.jd')]/text()").re(r'\S+'))

            _goods["itemprice"] = "".join(goods.xpath(".//*[@class='f-price']/text()|.//td[3]/strong/text()|.//*[@class='jdPrice']/text()").re(r'%s'%price_re))

            _goods["itemnum"] = "".join(goods.xpath(".//td[5]/text()|.//*[@class='num']/text()").re(r'%s'%price_re))

            _goods["itemid"] = "".join(goods.xpath(".//a[contains(@href,'item.jd')][1]/@href").re(r'\d+')[0])

            _goods["itemurl"] = urljoin(self.start_urlss[0],"".join(goods.xpath(".//a[contains(@href,'item.jd')][1]/@href").extract()[0]))

            _item.append(_goods)

        item["items"] = _item

        item["jobid"] = self.jobid

        self.order_list.append(item)

    def spider_closed(self, spider):

        self.con.hmset(self.jobid,{"status":3})

        logging.warning(msg="{%s} spider closed"%spider.name)

    def spider_idle(self):

        if self.ti == 1:

            if self.item == {}:

                self.con.hmset(self.jobid, {"status": 3})

            else:

                self.con.hmset(self.jobid, {"status": 1})

                self.item["all_order_list"] = self.order_list

                self.con.hmset(self.jobid, {"items": self.item})

            #yield Request(url=self.logouturl,cookies=self.sess)

            con = Util().spider_login_out(method="get", url=self.logouturl, cookies=self.sess)

            logging.warning(msg="{%s} spider idle" % self.name)

            if self.item:

                del self.item

                self.item = {}

            if self.order_list:

                del self.order_list

                self.order_list = []

            del con

        self.schedule_next_requests()

        self.ti = 0

        raise DontCloseSpider
