# -*- coding: utf-8 -*-
import sys 
import os
sys.path.append(os.path.abspath("../../"))
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
import logging
import time
from scrapy.http import Request, FormRequest
from QbSpider.scrapy_redis.spiders import Spiders
from QbSpider.utils.utils import Util
from scrapy import signals
import StringIO
import datetime
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
from scrapy.exceptions import DontCloseSpider
import json
import re
import base64
import copy
from QbSpider.utils.hbclient import HbClient
# from QbSpider.utils.utils import get_catch
# from twisted.internet.error import TimeoutError
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')


logger = logging.getLogger(__name__)

class RegionUnicom(object):

    data = u"""
    110 11 北京
    305 30 安徽
    831 83 重庆
    380 38 福建
    510 51 广东
    870 87 甘肃
    591 59 广西
    850 85 贵州
    710 71 湖北
    741 74 湖南
    188 18 河北
    760 76 河南
    501 50 海南
    971 97 黑龙江
    340 34 江苏
    901 90 吉林
    750 75 江西
    910 91 辽宁
    101 10 内蒙古
    880 88 宁夏
    700 70 青海
    170 17 山东
    310 31 上海
    190 19 山西
    841 84 陕西
    810 81 四川
    130 13 天津
    890 89 新疆
    790 79 西藏
    860 86 云南
    360 36 浙江
    HK HK 香港
    """

    fields = ['citycode', 'provcode', 'province']

    dic = {}

    @classmethod
    def code2region(cls, code):

        if not cls.dic:
            arr = cls.data.strip().split(os.linesep)
            for e in arr:
                obj = cls()
                line = e.strip()
                vals = line.split()
                for i in range(len(cls.fields)):
                    setattr(obj, cls.fields[i], vals[i])
                cls.dic[obj.provcode] = obj.province

        return cls.dic[code]


class UnicomSpider(Spiders):

    name = "unicom"
    redis_key = "QUEUE_YYS_LT"
    allowed_domains = []
    # 这里会提示是否需要验证码
    # scrapy_redis/spiders.py
    start_urlss = ["https://uac.10010.com/portal/mallLogin.jsp?redirectURL=http://www.10010.com"]

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_TIMEOUT': 35,
        'COOKIES_ENABLED': True,
        'REDIRECT_ENABLED': False,
        'REFERER_ENABLED': True,
        'USEPROXYHIGHLEVEL': False,
        'USELOCALIP': 1
   }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(UnicomSpider, cls).from_crawler(crawler,
                                                       *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def __init__(self, *a, **kw):
        super(UnicomSpider, self).__init__(*a, **kw)
        self.utils = Util()
        self.con = rcu().get_redis()
        self.con.ping()

        self.code_url = 'https://uac.10010.com/portal/Service/CreateImage?t=%s'
        #https://uac.10010.com/portal/Service/MallLogin?callback=jQuery17209809556654635019_1490578881710&req_time=1490578942510&redirectURL=http%3A%2F%2Fwww.10010.com&userName=15507312690&password=050628&pwdType=01&productType=01&redirectType=01&rememberMe=1&_=1490578942512
        self.login_code_url = 'https://uac.10010.com/portal/Service/MallLogin?callback=jQuery_%s&req_time=%s&redirectURL=http://www.10010.com&userName=%s&password=%s&pwdType=01&productType=01&verifyCode=%s&uvc=%s&redirectType=01&rememberMe=1&_=%s'
        self.login_random_url = 'https://uac.10010.com/portal/Service/MallLogin?callback=jQuery_%s&req_time=%s&redirectURL=http://iservice.10010.com&userName=%s&password=%s&pwdType=02&productType=01&redirectType=01&rememberMe=1&_=%s'
        self.send_random_url = 'https://uac.10010.com/portal/Service/SendMSG?callback=jQuery_%s&req_time=%s&mobile=%s&_=%s'
        #https://uac.10010.com/portal/Service/MallLogin?callback=jQuery17209809556654635019_1490578881710&req_time=1490578942510&redirectURL=http%3A%2F%2Fwww.10010.com&userName=15507312690&password=050628&pwdType=01&productType=01&redirectType=01&rememberMe=1&_=1490578942512

        self.check_authcode = 'https://uac.10010.com/portal/Service/CtaIdyChk?callback=jQuery_%s&verifyCode=%s&verifyType=1&_=%s'
        self.logouturl_post = 'http://www.10010.com/mall-web/Index/logout'

        # 登陆逻辑部分
        # 登陆页面
        self.login_url = 'https://uac.10010.com/portal/Service/MallLogin?callback=jQuery_%s&req_time=%s&redirectURL=http://www.10010.com&userName=%s&password=%s&pwdType=01&productType=01&redirectType=01&rememberMe=1&_=%s'
        # 逻辑：是否需要验证码
        self.authcode_url = 'https://uac.10010.com/portal/Service/CheckNeedVerify?callback=jQuery_%s&userName=%s&pwdType=01&_=%s'

        # 数据部分
        # 1-个人信息
        self.checklogin_url = 'http://iservice.10010.com/e3/static/check/checklogin/?_=%s'

        # 2-登录记录
        self.accesslog_url = 'https://uac.10010.com/portal/query/accessLogs?callback=getLoginInfo&_=%s'

        # 3-通话详单
        self.calldetail_url = 'http://iservice.10010.com/e3/static/query/callDetail?_=%s&accessURL=http://iservice.10010.com/e4/query/bill/call_dan-iframe.html?menuCode=000100030001&menuid=000100030001'

        # 4-历史账单
        self.historybill_url = 'http://iservice.10010.com/e3/static/query/queryHistoryBill?_=%s&accessURL=http://iservice.10010.com/e4/skip.html?menuCode=000100020001&menuCode=000100020001&menuid=000100020001'

        # 5-账户余额
        self.accountbalance_url = 'http://iservice.10010.com/e3/static/query/accountBalance/search?_=%s&accessURL=http://iservice.10010.com/e4/skip.html?menuCode=000100010002&menuCode=000100010002&menuid=000100010013'

        # 6-手机上网流量详单
        self.callflow_url = "http://iservice.10010.com/e3/static/query/callFlow?_=%s&accessURL=http://iservice.10010.com/e4/query/basic/call_flow_iframe1.html?menuCode=000100030004&menuid=000100030004"

        # 7-增值业务详单
        self.valueadded_url = "http://iservice.10010.com/e3/static/query/callValueAdded?_=%s&accessURL=http://iservice.10010.com/e4/query/basic/callValueAdded_iframe.html?menuCode=000100030003&menuid=000100030003"

        # 8-积分查询
        self.scorefourgresutl_url = 'http://iservice.10010.com/e3/static/query/scoreFourgResult?_=%s&accessURL=http://iservice.10010.com/e4/query/basic/scoreQuery-iframe.html?menuCode=000100050001&menuid=000200040003'

        # 9-短彩信详单查询
        self.sms_url = "http://iservice.10010.com/e3/static/query/sms?_=%s&accessURL=http://iservice.10010.com/e4/query/calls/call_sms-iframe.html?menuCode=000100030002&menuid=000100030002"

        # 10-智慧沃家成员信息

        # 11-手机上网记录
        self.callnetplayrecord_url = 'http://iservice.10010.com/e3/static/query/callNetPlayRecord?_=%s&accessURL=http://iservice.10010.com/e4/query/basic/call_phont_record-iframe.html?menuCode=000100030009&menuid=000100030009'

        # 12-实时话费 
        # 1 作废
        #self.currentfee_url = 'http://iservice.10010.com/e3/static/query/currentFee?_=%s&accessURL=http://iservice.10010.com/e4/skip.html'
        # 2
        self.realtimewoquery_url = 'http://iservice.10010.com/e3/static/realtimewo/query?_=%s'

        # ---------------------
        # 上网流量
        self.query_netflowresult_url = 'http://iservice.10010.com/e3/static/query/queryNetFlowResult?_=%s&accessURL=http://iservice.10010.com/e4/query/basic/data_flow-iframe.html?menuCode=000100040002&menuid=000100040002'

        self.ti = 0
        self.tb = HbClient()

    def parse(self, response):
        logging.info(msg='parse start url: %s' %  response.url)

        self.userinfo = response.meta['metass']
        self.username = self.userinfo.get('phone', '')

        logging.info(msg='user info: %s' % self.userinfo)
        logging.info(msg=u'account <%s> login success' % self.username)

        self.item = {}
        self.record_list = []
        self.passwd = self.userinfo.get('pwd', '')
        self.phone = self.username
        self.jobid = self.userinfo.get('key','')
        self.vercode = self.userinfo.get('sms','')
        self.spidertype = ''

        # 是否需要验证码
        ti = int(time.time() * 1000)
        check_url = self.authcode_url % (ti, self.username, ti)

        logging.info(msg='checkneedverify url: %s' % check_url)
        yield Request(url=check_url, callback=self.parse_checkneedverify, dont_filter=True)


    def parse_checkneedverify(self, response):

        def obtain_json(resp_texts):
            '''
            format the response content
            '''
            #use regex for comm
            regex = "[\S\s]+?{([\S\s]+)}"
            resp_text = re.findall(re.compile(r'%s'%regex,re.I),resp_texts)
            if resp_text:
                strs = "{"+resp_text[0]+"}"
                re_item = re.compile(r'(?<=[{,])\w+')
                after = re_item.sub("\"\g<0>\"", strs)
                return json.loads(after)
            else:
                return json.loads("{"+resp_text[0]+"}")

        logging.info(msg='account <%s> parrse checkneedverify' % self.username)
        ti = int(time.time() * 1000)

        try:
            logging.debug(msg='checkneedverify html: %s' % response.body)
            j_read = obtain_json(response.body)
            logging.debug(msg='checkneedverify json: %s' % j_read)
        except Exception, e:
            self.ti = 0
            logging.exception(msg='get json failed: %s %s' % (e.message, response.body))

            self.userinfo['code'] = 1999
            self.con.hmset(self.jobid, dict(self.userinfo))
            logging.error(msg='set code: %s' % 1999)
            return

        if j_read.get(u'resultCode', None) == u'false':
            # 不需验证码
            logging.info(msg='account <%s> does not require verification code' % self.username)
            login_url = self.login_url % (ti, ti, self.username, self.passwd, ti)
            logging.info(msg='transfer to login url: %s' % login_url)
            yield Request(url=login_url, callback=self.parse_malllogin, dont_filter=True)
        else:
            # 需要验证码
            logger.info(msg='account <%s> does require verification code' % self.username)
            authcode_url = self.code_url % ti
            logging.info(msg='verification code url: %s' % authcode_url)
            yield Request(url=authcode_url, callback=self.parsecode, dont_filter=True, cookies=self.sess)

    #@get_catch
    def parsecode(self, response):

        logger.info(msg="账号<%s>,正在获取验证码" % self.username)

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

    def get_codes(self, response):
        """
        未考虑
        """

        logger.info(msg="账号<%s>,正在获取验证码" % self.username)
        self.sess = {}
        cookie = [i.split(";")[0] for i in response.headers.getlist('Set-Cookie')]
        for cook in cookie:
            self.sess.update({cook[:cook.index("=")]: cook[cook.index("=") + 1:]})
            ti = int(time.time() * 1000)
            re_str = json.loads(response.body)
            if 'OK' not in re_str['err_str']:
                self.ti = 0
                logger.warning(msg="账号<%s>,验证码服务器出现问题或者本地服务器出现问题,服务器错误码<%s>,Redis错误码<%s>" % (self.username,re_str['err_str'],1019))
                self.userinfo["code"] = 1019
                self.con.hmset(self.jobid, dict(self.userinfo))
                return

            else:
                key = [i for i in re_str.keys() if u'pic_s' in i]
                self.authcode = re_str[key[0]]
                if self.authcode == "" or self.authcode is None:
                    logger.info(msg="账号<%s>,获取验证码内容为空,即将再次获取" % self.username)
                    authcode_url = self.code_url % ti
                    yield Request(url=authcode_url, callback=self.parsecode, dont_filter=True, cookies=self.sess)
                else:
                    logger.info(msg="账号<%s>,成功获取验证码" % self.username)
                    check_authcode_url = self.check_authcode % (ti, self.authcode, ti)
                    yield Request(url=check_authcode_url, callback=self.check_code, cookies=self.sess, dont_filter=True)

    #@get_catch
    def check_code(self, response):

        def obtain_json(resp_texts):
            '''
            format the response content
            '''
            #use regex for comm
            regex = "[\S\s]+?{([\S\s]+)}"
            resp_text = re.findall(re.compile(r'%s'%regex,re.I),resp_texts)
            if resp_text:
                strs = "{"+resp_text[0]+"}"
                re_item = re.compile(r'(?<=[{,])\w+')
                after = re_item.sub("\"\g<0>\"", strs)
                return json.loads(after)
            else:
                return json.loads("{"+resp_text[0]+"}")

        logger.info(msg="账号<%s>,检查验证码是否正确" % self.username)
        ti = int(time.time() * 1000)
        j_read = obtain_json(response.body)
        if j_read.get(u'resultCode', None) == u'true':
            logger.info(msg="账号<%s>,当前验证码校验成功" % self.username)
            login_code_url = self.login_code_url % (
                ti, ti, self.username, self.passwd, self.authcode, self.sess.get('uacverifykey', ""), ti)
            yield Request(url=login_code_url, callback=self.parse_malllogin, dont_filter=True)
        else:
            logger.info(msg="账号<%s>,当前验证码校验失败" % self.username)
            authcode_url = self.code_url % ti
            yield Request(url=authcode_url, callback=self.parsecode, dont_filter=True, cookies=self.sess)

    def parse_malllogin(self, response):

        """
        login:
        success:
        jQuery17205445927260395554_1490579539681({resultCode:"0000",redirectURL:"http://www.10010.com"});
        pwd err:

        #jQuery_1490944944653({resultCode:"7009",redirectURL:"http://www.10010.com",errDesc:"null",msg:'系统忙，请稍后再试。',needvode:"1",errorFrom:"cb"});

        # 部分用户系统升级
        #jQuery_1491011056223({resultCode:"7207",redirectURL:"http://www.10010.com",errDesc:"null",msg:'null',needvode:"1",errorFrom:"bss"});

        """

        def get_res_code(body, pat=re.compile(r'resultCode:"(?P<result_code>[\S]+?)"')):
            m = pat.search(body)
            if m:
                return m.group('result_code')
            return ''

        logging.info('account <%s>, parse malllogin' % self.username)
        res_headers = response.headers.getlist('Set-Cookie')

        # 装填cookie
        self.sess = {}
        cookie = [i.split(';')[0] for i in res_headers]
        for cook in cookie:
            self.sess.update({cook[:cook.index('=')]: cook[cook.index('=') + 1:].replace('"', '')})


        ti = int(time.time() * 1000)
        logging.debug(msg='malllogin html: %s' % response.body)

        result_code = get_res_code(response.body)
        if not result_code:
            self.ti = 0
            self.userinfo['code'] = 1999
            self.con.hmset(self.jobid, dict(self.userinfo))
            logging.warning(msg='account <%s> login failed: login response content is empty' % self.username)
            logging.warning(msg='account <%s> login failed: set redis code <%s>' % (self.username,1999))
            return

        if result_code == '0000':
            # 竟然在这里改的状态1
            self.ti = 1
            # 登陆成功
            logger.info(msg='account <%s> login success' % self.username)
            self.userinfo['code'] = 1009
            self.con.hmset(self.jobid, dict(self.userinfo))

            # 2-登录记录
            accesslog_url = self.accesslog_url % ti
            logging.info('accesslog url: %s' % accesslog_url)
            yield Request(url=accesslog_url, callback=self.parse_accesslog, dont_filter=True)
            # 串行
            # 并行

        elif result_code == '7007':
            self.ti = 0
            logging.info("account <%s> login failed: pwd error" % self.username)
            self.userinfo['code'] = 1004
            self.con.hmset(self.jobid, dict(self.userinfo))
            return
        elif result_code in ['7004', '7072', '7009', '7207', '7005']:
            self.ti = 0
            logging.info(msg="account <%s> login failed: max num of times today" % self.username)
            self.userinfo["code"] = 1022
            self.con.hmset(self.jobid, dict(self.userinfo))
            return
        else:
            self.ti = 0
            logger.info(msg="account <%s> login failed: unknown reason" % self.username)
            self.userinfo['code'] = 1999
            self.con.hmset(self.jobid, dict(self.userinfo))
            return


    def parse_accesslog(self, response):

        # 1-个人信息
        ti = int(time.time() * 1000)
        checklogin_url = self.checklogin_url % ti
        logging.info(msg='generate checklogin url: %s' % checklogin_url)
        yield Request(url=checklogin_url, callback=self.parse_checklogin, method='POST', dont_filter=True)

        # 2-登录记录

        def get_json(body, pat=re.compile(r'getLoginInfo\(([\s\S]*?)\);')):
            m = pat.search(body)
            if m:
                g1 = m.group(1)
                dic = json.loads(g1)
                return dic
            return None

        def str2cookie(cook):
            dic = {}
            arr = cook.split(';')
            for item in arr:
        
                key, val = item.strip().split('=', 1)
                print key, val
                dic[key] = val
            return dic

        logging.info(msg='account <%s> parse accesslogs' % self.username)
        #logging.debug(msg='accesslogs html: %s' % response.body)
        try:
            j_read = get_json(response.body)
            #logging.debug(msg='accesslogs json: %s' % j_read)
        except Exception, e:
            self.ti = 0
            self.userinfo['code'] = 1999
            self.con.hmset(self.jobid, dict(self.userinfo))
            logging.error(msg='ErrCode <%s>, Error <%s>, Content<%s>' % (1999, e.message, response.body))
            return

        records = []
        if 'content' in j_read and 'hits' in j_read['content'] and 'hits' in j_read['content']['hits']:
            for hit in j_read['content']['hits']['hits']:

                node_source = hit.get('_source', '')
                if not node_source:
                    logging.warning(msg="not found ['content']['hits']['hits']['_source']")
                    continue
                
                item = {}
                item['os'] = node_source.get('os', '')
                item['logintime'] = node_source.get('login_time', '')
                item['loginlocation'] = node_source.get('login_location', '')
                item['loginfrom'] = node_source.get('login_from', '')
                item['brower'] = node_source.get('brower', '')
                item['userid'] = node_source.get('user_id', '')
                item['loginip'] = node_source.get('login_ip', '')
                item['custid'] = node_source.get('cust_id', '')
                records.append(item)
        else:
            logging.warning(msg="parse accesslogs faild, return! reason: not found ['content']['hits']['hits']")

            self.ti = 0
            self.userinfo['code'] = 1999
            self.con.hmset(self.jobid, dict(self.userinfo))
            logging.error(msg='ErrCode <%s>, Error <%s>, Content<%s>' % (1999, e.message, response.body))
            return

        if not records:
            logging.warning('parse accesslogs failed, return! reason: result is null')
            return

        accesslogs = {'accesslogs': records}
        #logging.debug(msg='accesslogs struct json: %s' % json.dumps(accesslogs))

        self.tb.insert(colname=u'联通-登录记录', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=accesslogs, post_dic=None)
        logging.info(msg='insert accesslogs success')



    def parse_checklogin(self, response):
        # 12-实时话费
        ti = int(time.time() * 1000)
        rtwoquery_url = self.realtimewoquery_url % ti
        yield Request(url=rtwoquery_url, method='POST', callback=self.parse_realtimewoquery, dont_filter=True)

        # 1-个人信息

        def todate(opendate):
            if not opendate:
                return ''
            dt = datetime.datetime.strptime(opendate, '%Y%m%d%H%M%S')
            str_dt = dt.strftime('%Y-%m-%d %H:%M:%S')
            return str_dt

        def type2name(paytype):
            if paytype == '1':
                return u'预付费'
            elif paytype == '2':
                return u'后付费'
            else:
                return ''

        def certtype2name(certtype):
            if certtype == '11':
                return u'身份证'
            elif certtype == '02':
                return u'18位身份证'
            else:
                # extends in the future
                return ''


        def sex2name(custsex):
            if custsex == '1':
                return u'男'
            elif custsex == '2':
                return u'女'
            else:
                return ''

        def parse_mainnumflagname(mng):
            if not mng:
                return ''
            if mng == '0':
                return u'主号码'
            elif mng == '1':
                return u'成员号码'
            else:
                return ''

        def parse_serviceclasscodename(scc):
            if not scc:
                return ''

            if scc == '0050':
                return u'移网'
            elif scc == '0030':
                return u'固话'
            elif scc == '0040':
                return u'宽带'
            else:
                return ''

        logging.info(msg='account <%s> parse checklogin' % self.username)
        #logging.debug(msg='checklogin html: %s' % response.body)
        j_read = json.loads(response.body.decode("utf8"))
        #logging.debug(msg='checklogin json: %s' % j_read)

        if 'userInfo' in j_read:
            info = j_read['userInfo']
            item = {}
            # 个人信息
            item['custid'] = info.get('customid', '')
            item['custname'] = info.get('custName', '')
            item['custlvl'] = info.get('custlvl', '')
            item['certtype'] = info.get('certtype', '')
            item['certtypename'] = certtype2name(info.get('certtype', ''))
            item['certnum'] = info.get('certnum', '')
            item['usernumber'] = info.get('usernumber', '')
            item['custsex'] = info.get('custsex', '')
            item['custsexname'] = sex2name(info.get('custsex', ''))
            item['certaddr'] = info.get('certaddr', '')
            pcode = info.get('provincecode', '')
            pcode = pcode[1:]
            item['provincecode'] = pcode
            item['province'] = RegionUnicom.code2region(pcode)
            item['citycode'] = info.get('citycode', '')

            # 号码信息
            item['opendate'] = todate(info.get('opendate', ''))
            item['paytype'] = info.get('paytype', '')
            item['paytypename'] = type2name(info.get('paytype', ''))
            item['subscrbstat'] = info.get('subscrbstat', '')
            item['brandcode'] = info.get('brand', '')
            item['brandname'] = info.get('brand_name', '')

            # 当前套餐信息
            item['productname'] = info.get('packageName', '')
            item['productid'] = info.get('packageID', '')
            #上述二者一个文字一个数字，意义一致
            item['producttype'] = info.get('productType', '')

            if 'group_info' in info and 'con_member_info' in info['group_info']:
                con_members = info['group_info']['con_member_info']
                numbers = []
                for e in con_members:
                    num = e.get('serial_number', '')
                    if num:
                        numbers.append(num)
                serial_numbers = '|'.join(numbers)
                item['serial_numbers'] = serial_numbers
            else:
                item['serial_numbers'] = ''

            # 10-智慧沃家成员信息
            if 'group_info' in info and 'con_member_info' in info['group_info']:
                con_members = info['group_info']['con_member_info']
                mms = []
                for e in con_members:
                    dic = {}
                    # 号码
                    dic['serialnumber'] = e.get('serial_number', '')
                    # 0 主号码 1成员号码
                    dic['mainnumflag'] = e.get('main_num_flag', '')
                    dic['mainnumflagname'] = parse_mainnumflagname(dic['mainnumflag'])
                    # 姓名
                    dic['memberusername'] = e.get('member_user_name', '')
                    # 服务类别
                    dic['serviceclasscode'] = e.get('service_class_code', '')
                    dic['serviceclasscodename'] = parse_serviceclasscodename(dic['serviceclasscode'])

                    mms.append(dic)
                if mms:
                    groupinfo = {'groupinfo': mms}
                    logging.debug(msg='group info struct json: %s' % json.dumps(groupinfo))

                    self.tb.insert(colname=u'联通-沃家成员信息', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=groupinfo, post_dic=None)
                    logging.info(msg='insert group info success')

            checklogin = {'checklogin': [item]}
            #logging.debug(msg='checklogin struct json: %s' % json.dumps(checklogin))

            self.tb.insert(colname=u'联通-个人信息', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=checklogin, post_dic=None)
            logging.info(msg='insert checlogin success')

        #e4_url = 'http://iservice.10010.com/e4/index_server.html'
        #print >> sys.stderr, 'e4_url', e4_url
        #yield Request(url=e4_url, callback=self.parse_e4, dont_filter=True)


        # 信用额度调整历史查询
        # 上网流量
        # 流量包订购记录
        # 流量币账单：尊敬的用户，您不是60元沃派不清零套餐用
        # wlan详单: 无法确定是否采集，目前的手机号都无可现实数据
        # 话费购
        # 余量查询: 没什么意义
        # 合约期查询: 无可显示数据



    def parse_realtimewoquery(self, response):
        # 8-积分查询
        ti = int(time.time() * 1000)
        scorefourgresutl_url = self.scorefourgresutl_url % ti
        yield Request(url=scorefourgresutl_url, callback=self.parse_scorefourgresult, method='POST', dont_filter=True)

        # 12-实时话费
        def get_curdate(input):
            if not input:
                return ''
            now = datetime.datetime.strptime(input, '%Y年%m月%d日')
            now = now.strftime('%Y-%m-%d')
            return now

        def get_balancename(input):
            if not input:
                return ''
            if input == 'A':
                return u'可用余额'
            else:
                return u'当前可用余额'

        logging.info(msg='account <%s> parse realtimewoquery' % self.username)
        logging.debug(msg='realtimewoquery html: %s' % response.body)
        j_read = json.loads(response.body)
        #logging.debug(msg='realtimewoquery json: %s' % j_read)

        if not j_read.get('success', ''):
            # reason
            # 更新redis状态
            return

        dic = {}
        # 截止日期
        dic['curdate'] = get_curdate(j_read.get('curDate', ''))
        result = j_read.get('result', '')
        if result:
            # 不可见字段
            dic['balancereportscheme'] = result.get('balanceReportScheme', '')

            # 实时话费合计
            dic['realfee'] = result.get('realFee', '')
            # 当前可用余额
            dic['balance'] = result.get('balance', '')
            dic['balancename'] = get_balancename(dic['balancereportscheme'])
            # 账户欠费
            dic['totalfee'] = result.get('totalFee', '')

            rlf = {'realtimefee': [dic, ]}
            #logging.debug(msg='realtimefee struct json: %s' % json.dumps(rlf))

            self.tb.insert(colname=u'联通-实时话费', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=rlf, post_dic=None)
            logging.info(msg='insert realtimefee success')

        

    def parse_scorefourgresult(self, response):
        # 5-账户余额
        ti = int(time.time() * 1000)
        accountbalance_url = self.accountbalance_url % ti
        logging.info(msg=accountbalance_url)
        pay_load = {'type':'onlyAccount'}

        yield FormRequest(url=accountbalance_url,method='POST',callback=self.parse_accountbalance,dont_filter=True,formdata=pay_load, meta=pay_load)

        # 8-积分查询
        #logging.debug('scorefourgresutl html: %s' % response.body)
        j_read = json.loads(response.body.decode('utf-8'))
        #logging.debug('scorefourgresutl json: %s' % j_read)

        if not j_read.get('issuccess', ''):
            # 捕获错误描述，错误码
            # 修改redis
            logging.warning(msg='parse_scorefourgresult failed, %s' % response.body)
            return

        t = []
        result = j_read.get('result', '')
        if result:
            scoreinfolist = result.get('scoreinfo', '')
            if scoreinfolist:
                scoreinfo = scoreinfolist[0]

                dic = {}
                # 当前总积分
                dic['totalscore'] = scoreinfo.get('totalscore', '')
                # 当前可用积分
                dic['availablescore'] = scoreinfo.get('availablescore', '')
                # 本月新增积分
                dic['lastmonthscore'] = scoreinfo.get('lastmonthscore', '')
                # 本月即将失效积分
                dic['invalidscore'] = scoreinfo.get('invalidscore', '')

                # 隐藏字段
                dic['userstate'] = scoreinfo.get('userstate', '')
                t.append(dic)

        sfr = {'scorequery': t}
        #logging.debug(msg='scorefourgresult struct json: %s' % json.dumps(sfr))

        self.tb.insert(colname=u'联通-积分查询', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=sfr, post_dic=None)
        logging.info(msg='insert scorefourgresult success')



    def parse_accountbalance(self,response):
        # 6-手机上网流量详单

        ti = int(time.time() * 1000)
        days_que = Util().getlastdays(numofdays=10)
        if not days_que.empty():
            day = days_que.get()
            day = str(day)
            pay_load = {
                'pageNo': '1',
                'pageSize': '100',
                'beginDate': day,
                'endDate': day
            }
            callflow_url = self.callflow_url % ti
            logging.info(msg='generate new callflow url: %s, %s' % (day, callflow_url))
            metadata = {'postdata': pay_load, 'days_que': days_que}
            yield FormRequest(url=callflow_url, method="POST", formdata=pay_load, callback=self.parse_callflow, dont_filter=True,meta=metadata)


        ## 上网流量

        # 4-历史账单
        # 目前发现存在两个版本
        ti = int(time.time() * 1000)
        historybill_url = self.historybill_url % ti
        monlist = Util().getlast6month_1()
        for begin, _ in monlist:
            billdate = begin.strftime('%Y%m')
            pay_load = {
                'querytype': '0001',
                'querycode': '0001',
                'billdate': billdate,
                'flag': '1',
            }
            yield FormRequest(url=historybill_url, method='POST',formdata=pay_load, callback=self.parse_historybill, dont_filter=True,meta=pay_load)

        # 3-通话详单
        monlist = Util().getlast6month()
        for begin, end in monlist:
            begin = str(begin)
            end = str(end)
            pay_load = {
                'pageNo': '1',
                'pageSize': '100',
                'beginDate': begin,
                'endDate': end
            }

            ti = int(time.time() * 1000)
            record_url = self.calldetail_url % ti
            yield FormRequest(url=record_url, method='POST', formdata=pay_load, callback=self.parse_calldetail,
                              dont_filter=True, meta=pay_load)

        # 11-手机上网记录(网页最多查两个月的)
        #monlist = Util().getlast6month()[0: 2]
        monlist = Util().getlast6month()
        # 先抓这个月的
        begin, end = monlist[0]
        begin = begin.strftime('%Y-%m-%d')
        end = end.strftime('%Y-%m-%d')
        pay_load = {
            "pageNo": "1",
            "pageSize": "20",
            "beginDate": begin,
            "endDate": end
        }
        ti = int(time.time() * 1000)
        callnetplayrecord_url = self.callnetplayrecord_url % ti
        ret = FormRequest(url=callnetplayrecord_url, method="POST", formdata=pay_load, callback=self.parse_callnetplayrecord,
                          dont_filter=True, meta=pay_load)
        yield ret

        # 9-短彩信详单查询
        monlist = Util().getlast6month()
        # 先知抓上个月的
        begin, end = monlist[1]
        begin = begin.strftime('%Y%m%d')
        end = end.strftime('%Y%m%d')
        pay_load = {
            "pageNo": "1",
            "pageSize": "20",
            "begindate": begin,
            "enddate": end
        }
        ti = int(time.time() * 1000)
        sms_url = self.sms_url % ti
        
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'Keep-Alive',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Host': 'iservice.10010.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'X-Requested-With': 'XMLHttpRequest',
        }
        ret = FormRequest(url=sms_url, method="POST", headers=headers, formdata=pay_load, callback=self.parse_sms,
                          dont_filter=True, meta=pay_load)
        yield ret

        # 7-增值业务详单
        monlist = Util().getlast6month()
        for begin, end in monlist:
            begin = str(begin)
            end = str(end)
            pay_load = {
                "pageNo": "1",
                "pageSize": "100",
                "beginDate": begin,
                "endDate": end
            }
            ti = int(time.time() * 1000)
            valueadded_url = self.valueadded_url % ti
            yield FormRequest(url=valueadded_url, method="POST", formdata=pay_load, callback=self.parse_callvalueadded,
                              dont_filter=True,meta=pay_load)
            # 一条先
            break

        ### 当前账户充值信息 (***)
        ##monlist = Util().getlast6month()
        ##for begin, end in monlist:
        ##    begin = begin.strftime('%Y%m%d')
        ##    end = end.strftime('%Y%m%d')
        ##    pay_load = {
        ##        "pageNo": "1",
        ##        "pageSize": "100",
        ##        "beginDate": begin,
        ##        "endDate": end
        ##    }
        ##    add_fee_url = "http://iservice.10010.com/e3/static/query/paymentRecord?_=%s&accessURL=http://iservice.10010.com/e4/query/calls/paid_record-iframe.html?menuCode=000100010003&menuid=000100010003"%ti
        ##    yield FormRequest(url=add_fee_url, method="POST", formdata=pay_load, callback=self.parse_add_fee,
        ##                      dont_filter=True,meta={"dataa": begin})

        # 5-账户余额
        logging.info(msg='account %s parse accountbalance' % self.username)
        #logging.debug(msg='accountbalance html: %s' % response.body)
        j_read = json.loads(response.body)
        #logging.debug(msg='accountbalance json: %s' % j_read)

        dic = {}
        info = j_read.get('userInfo', '')
        if info:
            dic['custname'] = info.get('custName', '')
            dic['usernumber'] = info.get('usernumber', '')
        dic['cctbalance'] = j_read.get('acctbalance', '')
        dic['freezamount'] = j_read.get('freezamount', '')
        dic['sumfee'] = j_read.get('sumFee', '')

        actban = {'accountbalance': [dic, ]}
        #logging.debug(msg='accountbalance struct json: %s' % json.dumps(actban))

        post_dic = response.meta
        self.tb.insert(colname=u'联通-账户余额', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=actban, post_dic=post_dic)
        logging.info(msg='insert accountbalance success')

        #self.sess = {}
        #cookie = response.request.headers.getlist('Cookie')[0].split(';')
        #for cook in cookie:
        #    self.sess.update({cook[:cook.index('=')]: cook[cook.index('=') + 1:].replace('"', '')})



    def parse_callflow(self, response):
        # 6-手机上网流量详单
        #metadata = {'postdata': pay_load, 'que_wait': days_que}

        def combine_starttime(cdrinfo):
            begin = cdrinfo.get('begindateformat')
            end = cdrinfo.get('begintimeformat', '')
            if begin and end:
                return '%s %s' % (begin, end)
            return ''

        post_dic = response.meta['postdata']

        begindate = post_dic.get('beginDate', '')
        pageno = post_dic.get('pageNo', '')
        logging.info(msg='account %s parse callflow date: %s pageno: %s' % (self.username, begindate, pageno))
        #logging.debug(msg='callflow html: %s' % response.body)
        j_read = json.loads(response.body)
        #logging.debug(msg='callflow json: %s' % j_read)

        issuccess = j_read.get('issuccess')
        if not issuccess:
            desc = j_read.get('rspdesc', '')
            if desc:
                logging.warning(msg='parse callflow failed, reason: %s' % desc)
            else:
                logging.warning(msg='parse callflow failed,reason: not found')
            # 标注redis

            # 1 进一步的修改, 这个直接干掉下一页, 2其次 要 要控制优先级了
            #"rspcode":"ECS000000002"
            #"rspdesc":"业务访问限制超出限制次数"
            # 如果出现这个了，就不yield了
            return

        # 如果成功了
        days_que = response.meta['days_que']
        if not days_que.empty():
            day = days_que.get()
            day = str(day)
            pay_load = {
                'pageNo': '1',
                'pageSize': '100',
                'beginDate': day,
                'endDate': day
            }
            ti = int(time.time() * 1000)
            callflow_url = self.callflow_url % ti
            logging.info(msg='generate new callflow url: %s, %s' % (day, callflow_url))

            metadata = {'postdata': pay_load, 'days_que': days_que}
            yield FormRequest(url=callflow_url, method="POST", formdata=pay_load, callback=self.parse_callflow, dont_filter=True,meta=metadata)


        result = j_read.get('result', '')
        #冗余处理
        callflowlist = []
        if result:
            cdrinfo = result.get('cdrinfo', '')
            if cdrinfo:
                cdrdetailinfo = cdrinfo[0].get('cdrdetailinfo', '')
                if cdrdetailinfo:
                    for cinfo in cdrdetailinfo:
                        dic = {}
                        uinfo = j_read.get('userinfo', '')
                        if uinfo:
                            # 客户姓名
                            dic['custname'] = uinfo.get('custname', '')
                            # 手机号码
                            dic['usernumber'] = uinfo.get('usernumber', '')

                        # 费用合计
                        dic['alltotalfee'] = result.get('alltotalfee', '')
                        # 总记录数
                        dic['totalrecord'] = result.get('totalrecord', '')
                        # 流量合计
                        dic['totalsm'] = result.get('totalsm', '')

                        # 起始时间
                        dic['starttime'] = combine_starttime(cinfo)
                        # 通信地点
                        dic['homearea'] = cinfo.get('homearea', '')

                        # 网络类型
                        dic['nettype'] = cinfo.get('nettype', '')
                        dic['nettypeformat'] = cinfo.get('nettypeformat', '')

                        # 计费类型
                        # 2
                        dic['feetype'] = cinfo.get('feetype', '')
                        # 02 套餐内流量
                        dic['svcname'] = cinfo.get('svcname', '')
                        
                        # 是否定向
                        # 1
                        dic['forwardtype'] = cinfo.get('forwardtype', '')
                        # 非定向流量
                        dic['forwardtypeformat'] = cinfo.get('forwardtypeformat', '')

                        # 总流量(kb)
                        dic['pertotalsm'] = cinfo.get('pertotalsm', '')
                        # 通信费
                        dic['totalfee'] = cinfo.get('totalfee', '')
                        callflowlist.append(dic)
        if callflowlist:
            clf = {'callflow': callflowlist}
            logging.debug(msg='callflow struct json: %s' % json.dumps(clf))

            self.tb.insert(colname=u'联通-手机上网流量详单', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=clf, post_dic=post_dic)
            logging.info(msg='insert callflow success phone: %s date: %s pageno: %s' % (self.username, begindate, pageno))


    def parse_callnetplayrecord(self, response):
        # 11-手机上网记录

        def parse_querydatescope(scope):
            if not scope:
                return ''
            return scope.replace('至', ' ')

        pay_load = response.meta
        pageno = pay_load.get('pageNo', '')
        begin = pay_load.get('beginDate', '')
        logging.info(msg='account <%s> parse callnetplayrecord date:%s page:%s' % (self.username, begin, pageno))

        logging.debug(msg='callnetplayrecord html: %s' % response.body)
        j_read = json.loads(response.body.decode('utf8'))
        #logging.debug(msg='callnetplayrecord json: %s' % j_read)

        if not j_read.get('isSuccess', ''):
            reason = j_read.get('errorMessage', '')
            logging.warning(msg='reason: %s' % str(reason).decode('unicode-escape'))
            # 标记redis状态
            return

        userinfo = j_read.get('userInfo', '')
        pagemap = j_read.get('pageMap', '')
        if pagemap:
            resultlist = pagemap.get('result', '')
            if not resultlist:
                return

            records = []
            for record in resultlist:
                dic = {}
                if userinfo:
                    # 客户姓名
                    dic['custname'] = userinfo.get('custName', '')
                    # 手机号码
                    dic['usernumber'] = userinfo.get('usernumber', '')
                # 总记录数
                dic['totalrecord'] = j_read.get('totalRecord', '')
                # 查询周期
                dic['querydatescope'] = parse_querydatescope(j_read.get('queryDateScope', ''))

                # 起始时间
                dic['begintime'] = record.get('begintime', '')
                # 业务类型
                dic['bizname'] = record.get('bizname', '')
                dic['biztype'] = record.get('biztype', '')
                # 流量类型
                dic['flowname'] = record.get('flowname', '')
                dic['flowtype'] = record.get('flowtype', '')
                # 访问地址
                dic['featinfo'] = record.get('featinfo', '')
                # 网址名称
                dic['domainname'] = record.get('domainname', '')

                # 不可见字段
                dic['totaltraffic'] = record.get('totaltraffic', '')
                dic['durationtime'] = record.get('durationtime', '')
                dic['rattype'] = record.get('rattype', '')
                dic['apn'] = record.get('apn', '')
                dic['uptraffic'] = record.get('uptraffic', '')
                dic['downtraffic'] = record.get('downtraffic', '')
                # 客户端ip
                dic['clientip'] = record.get('clientip', '')
                # 服务端ip
                dic['accessip'] = record.get('accessip', '')
                dic['useragent'] = record.get('useragent', '')

                records.append(dic)

            callnetplayrecord = {'callnetplayrecord': records}
            logging.debug(msg='callnetplayrecord struct json: %s' % json.dumps(callnetplayrecord))

            self.tb.insert(colname=u'联通-手机上网记录', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=callnetplayrecord, post_dic=pay_load)
            logging.info(msg='insert callnetplayrecord success phone: %s date: %s pageno: %s' % (self.username, begin, pageno))


    def parse_calldetail(self, response):
        # 3-通话详单

        def combine_date(row):
            """合并时间"""
            dt = row.get('calldate', '')
            tm = row.get('calltime', '')
            if dt and tm:
                return '%s %s' % (dt, tm)
            if dt and not tm:
                return '%s %s' % (dt, '00:00:00')
            return ''

        def calc_duration(input, pat=re.compile('\d+')):
            """计算时长"""
            arr = pat.findall(input)
            arr.reverse()
            total = 0
            for i in range(len(arr)):
                n = int(arr[i])
                total += n * (60 ** i)
            return str(total)

        def parsejson(j_read):
            if not j_read.get('pageMap', '') or not j_read['pageMap'].get('result', ''):
                logging.info('not found key: pageMap or pageMap.result')
                return None
            records = []
            for row in j_read['pageMap']['result']:
                record = {}
                # 起始时间
                record['starttime'] = combine_date(row)

                # 通话时长
                record['calllonghour'] = row.get('calllonghour','')
                # 通话时长 单位秒
                record['calllonghourunitsecond'] = calc_duration(row.get('calllonghour',''))

                # 呼叫类型
                record['calltypename'] = row.get('calltypeName','')
                # 呼叫类型：1 主叫  2 被叫
                record['calltype'] = row.get('calltype','')

                # 对方号码
                record['othernum'] = row.get('othernum','')

                # 本机通话地
                record['homeareaname'] = row.get('homeareaName','')
                # 本机通话地1
                record['otherareaname'] = row.get('otherareaName','')

                # 对方归属地
                record['calledhome'] = row.get('calledhome','')
                # 通话类型
                record['landtype'] = row.get('landtype','')
                # 通话费
                record['totalfee'] = row.get('totalfee','')
                # 还有明细的费用

                records.append(record)

            dic = {'calldetail': records}
            return dic

        pay_load = response.meta
        pageno = pay_load.get('pageNo', '')
        begin = pay_load.get('beginDate', '')

        logging.info(msg='account <%s> parse calldetail date:%s page:%s' % (self.username, begin, pageno))
        ti = int(time.time() * 1000)

        if response.body:
            ##logging.debug(msg='calldetail html: %s' % response.body)
            j_read = json.loads(response.body.decode('utf8'))
            ##logging.debug(msg='calldetail json: %s' % j_read)

            if isinstance(j_read, dict):
                if j_read.get('errorMessage', ''):
                    logging.warning(u'数据采集不完整!系统访问频繁,请明天再试')
                    logging.debug(msg='calldetail html: %s' % response.body)
                    self.userinfo['code'] = 1023
                    self.con.hmset(self.jobid, dict(self.userinfo))
                    return

                # 解析json
                struct_dic = parsejson(j_read)
                if not struct_dic:
                    # 这里需要更改redis状态，暂时设置1023, 并要检查所有return
                    # case1: 这里很奇怪，采集第一页被封，但第二页却不会被封。
                    # 这里要设置么？
                    logging.warning(u'数据采集不完整!系统访问频繁,请明天再试')
                    self.userinfo['code'] = 1023
                    self.con.hmset(self.jobid, dict(self.userinfo))
                    # 只要被封了，下面的请求应该也是被封的，所以return
                    return

                ##logging.debug(msg='call detail struct json: %s' % json.dumps(dic))

                # 入库
                self.tb.insert(colname=u'联通-通话详单', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=struct_dic, post_dic=pay_load)
                logging.info(msg='insert calldetail success phone: %s date: %s pageno: %s' % (self.username, begin, pageno))


                # 翻页策略1: 每次只翻一页
                #if 'totalRecord' in j_read:
                #    counts = int(j_read['totalRecord'])
                #    pagenos = counts / 100 if counts % 100 == 0 else counts / 100 + 1
                #    if int(pageno) < pagenos:
                #        nos = int(pageno) + 1
                #        pay_load = {
                #            'pageNo': '%s' % nos,
                #            'pageSize': '100',
                #            'beginDate': begin,
                #            'endDate': end
                #        }
                #        logging.info(msg='pay_load: %s' % pay_load)
                #        record_url = self.calldetail_url % ti
                #        logging.info('page num: %s %s' % (nos, record_url))
                #        yield FormRequest(url=record_url, formdata=pay_load, callback=self.parse_calldetail,
                #                          dont_filter=True, meta=pay_load)

                ## 翻页策略2: 一次性产生所有请求, (并发度太高，容易造成系统访问频繁, 而导致数据不完整)
                #if 'totalRecord' in j_read:
                #    if pageno != '1':
                #        return

                #    counts = int(j_read['totalRecord'])
                #    pagenos = counts / 100 if counts % 100 == 0 else counts / 100 + 1
                #    for nos in range(2, pagenos + 1):
                #        pay_load = {
                #            'pageNo': '%s' % nos,
                #            'pageSize': '100',
                #            'beginDate': begin,
                #            'endDate': end
                #        }
                #        logging.info(msg='pay_load: %s' % pay_load)
                #        record_url = self.calldetail_url % ti
                #        logging.info('page num: %s %s' % (nos, record_url))
                #        yield FormRequest(url=record_url, formdata=pay_load, callback=self.parse_calldetail,
                #                          dont_filter=True, meta=pay_load)

        else:
            logging.info(msg='download calldetail failed, return')
            # 请注明redis状态
            return

        #self.tb.insert_bill_detail(phone=self.phone, jobid=self.userinfo["token"], url=response.url, post_data=dataa)
        #logging.info('inser success')
        #self.tb.insert_page(url=response.url, phone=self.phone, html=response.body, charset='utf-8',
        #                    struct_json={"detailed_query":{"voice_communication_detailed_list":recordd}}, post_data=dataa)
        #logging.info('inser success')

    # 作废
    def parse_record(self, response):
        logger.info(msg='account<%s>,get account record' % self.username)
        k = response.meta['k']
        v = response.meta['v']
        ti = int(time.time() * 1000)
        if response.body:
            #logging.debug(msg='parse record html: %s' % response.body)
            j_read = json.loads(response.body.decode('utf8'))
            #logging.debug(msg='parse record json: %s' % j_read)
            if isinstance(j_read, dict):
                if j_read.get('errorMessage', '') != '':
                    logging.warning(u'数据采集不完整!系统访问频繁,请明天再试')
                    self.userinfo['code'] = 1023
                    self.con.hmset(self.jobid, dict(self.userinfo))
                    return
                counts = int(j_read['totalRecord'])
                pagenos = counts / 100 if counts % 100 == 0 else counts / 100 + 1
                for nos in xrange(1, pagenos + 1):
                    pay_load = {
                        'pageNo': '%s' % nos,
                        'pageSize': '100',
                        'beginDate': k,
                        'endDate': v
                    }
                    logging.info(msg='pay_load: %s' % pay_load)
                    record_url = self.calldetail_url % ti
                    logging.info(record_url)
                    #yield FormRequest(url=record_url, formdata=pay_load, callback=self.parse_record_detail,
                    #                  dont_filter=True,meta={'dataa':k})
        #    else:
        #        rest = copy.deepcopy(response.request)
        #        yield rest
        #else:
        #    rest = copy.deepcopy(response.request)
        #    yield rest

    # 作废
    def parse_record_detail(self, response):

        logger.info(msg="账号<%s>,正在获取当前账户通话详单信息详情页面" % self.username)
        dataa = response.meta["dataa"]
        recordd = []
        if response.body:
            j_read = json.loads(response.body.decode("utf8"))
            if isinstance(j_read, dict):
                if j_read.get("errorMessage", "") != "":
                    logging.warning(u"数据采集不完整!系统访问频繁,请明天再试")
                    self.userinfo["code"] = 1023
                    self.con.hmset(self.jobid, dict(self.userinfo))
                    return

                for record in j_read["pageMap"]["result"]:
                    records = {}
                    records["start_time"] = record.get("calldate","")
                    # records["calltime"] = record["calltime"]
                    records["communication_duration"] = record.get("calllonghour","")
                    records["communication_mode"] = record.get("calltypeName","")
                    records["other_number"] = record.get("othernum","")
                    records["home_communication_location"] = record.get("homeareaName","")
                    records["other_communication_location"] = record.get("calledhome","")
                    records["communication_type"] = record.get("landtype","")
                    records["localfee"] = record.get("landfee","")
                    records["toll_call"] = record.get("otherfee","")
                    records["roam_call_free"] = record.get("roamfee","")
                    records["new_call"] = ""
                    records["business_name"] = ""
                    records["package_discount"] = ""
                    records["communication_fee"] = record.get("totalfee","")
                    recordd.append(records)
            else:
                rest = copy.deepcopy(response.request)
                return rest
        else:
            rest = copy.deepcopy(response.request)
            return rest

        print '-------', dataa
        self.tb.insert_bill_detail(phone=self.phone, jobid=self.userinfo["token"], url=response.url, post_data=dataa)
        logging.info('inser success')

        self.tb.insert_page(url=response.url, phone=self.phone, html=response.body, charset='utf-8',
                            struct_json={"detailed_query":{"voice_communication_detailed_list":recordd}}, post_data=dataa)
        logging.info('inser success')


    def parse_add_fee(self,response):
        logger.info(msg="账号<%s>,正在获取当前账户充值信息" % self.username)
        dataa = response.meta["dataa"]
        j_read = json.loads(response.body)
        r_d = []
        if j_read.get("totalResult","") != "":
            for add_fee in j_read["totalResult"]:
                recharge_details = {}
                recharge_details["recharge_time"] = add_fee.get("paydate","")
                recharge_details["cost_change_type"] = add_fee.get("paychannel","")
                recharge_details["recharge_sum"] = add_fee.get("payfee","")
                r_d.append(recharge_details)
        else:
            recharge_details = {}
            recharge_details["recharge_time"] = ""
            recharge_details["cost_change_type"] =""
            recharge_details["recharge_sum"] = ""
            r_d.append(recharge_details)

        self.tb.insert_bill_detail(phone=self.phone, jobid=self.userinfo["token"], url=response.url, post_data=dataa)

        logging.info('inser success')
        self.tb.insert_page(url=response.url, phone=self.phone, html=response.body, charset='utf-8',
                            struct_json={"detailed_query":{"recharge_details":r_d}}, post_data=dataa)


    def parse_callvalueadded(self,response):
        # 7-增值业务详单

        def combine_starttime(result):
            dt = result.get('begindate')
            tme = result.get('begintime', '')
            if dt and tme:
                return '%s %s' % (dt, tme)
            return ''

        pay_load = response.meta
        begindate = pay_load['beginDate']
        pageno = pay_load['pageNo']
        logging.info(msg='account <%s> parse callValueAdded %s %s' % (self.username, begindate, pageno))

        #logging.debug(msg='callvalueadded html: %s' % response.body)
        j_read = json.loads(response.body)
        #logging.debug(msg='callvalueadded json: %s' % j_read)

        if not j_read.get('isSuccess', ''):
            reason = j_read.get('errorMessage', '')
            logging.warning(msg='reason: %s' % str(reason).decode('unicode-escape'))
            # 标记redis状态
            return

        userinfo = j_read.get('userInfo', '')
        valueaddedlist = []
        pagemap = j_read.get('pageMap', '')
        if pagemap:
            resultlist = pagemap.get('result', '')
            if resultlist:
                for result in resultlist:
                    dic = {}

                    if userinfo:
                        dic['custname'] = userinfo.get('custName', '')
                        dic['usernumber'] = userinfo.get('usernumber', '')

                    dic['alltotalfee'] = j_read.get('alltotalfee', '')
                    dic['querydatescope'] = j_read.get('queryDateScope', '')
                    dic['totalrecord'] = j_read.get('totalRecord', '')

                    # 产品名称
                    dic['businessname'] = result.get('businessname', '')
                    # 业务类型
                    dic['businesstype'] = result.get('businesstype', '')
                    dic['businesscode'] = result.get('businesscode', '')

                    # 订购/使用时间
                    dic['starttime'] = combine_starttime(result)

                    # 使用时长
                    # 0秒， 由于无统计数据，不进行数据清洗
                    dic['capturetime'] = result.get('capturetime', '')
                    # 对方号码
                    dic['othernum'] = result.get('othernum', '')
                    # 费用类别
                    dic['billingmethod'] = result.get('billingmethod', '')
                    # 费用
                    dic['totalfee'] = result.get('totalfee', '')

                    # 隐藏字段，意义未知
                    dic['spname'] = result.get('spname', '')
                    dic['spcode'] = result.get('spcode', '')
                    dic['spmethod'] = result.get('spmethod', '')

                    valueaddedlist.append(dic)

        valueadded = {'valueadded': valueaddedlist}
        #logging.debug(msg='callvalueadded struct json: %s' % json.dumps(valueadded))

        self.tb.insert(colname=u'联通-增值业务详单', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=valueadded, post_dic=pay_load)
        logging.info(msg='insert callvalueadded success phone: %s date: %s pageno: %s' % (self.username, begindate, pageno))


    def parse_sms(self, response):
        # 9-短彩信详单查询

        def combine_datescope(pagemap):
            begin = pagemap.get('beginDate', '')
            end = pagemap.get('endDate', '')
            if begin and end:
                return '%s-%s' % (begin, end)
            return ''

        def combine_starttime(result):
            dt = result.get('smsdate', '')
            stm = result.get('smstime', '')
            if dt and stm:
                return '%s %s' % (dt, stm)
            return ''

        def parse_smstypename(smstype):
            if not smstype:
                return ''
            if smstype == '1':
                return u'接受'
            elif smstype == '2':
                return u'发送'
            else:
                return smstype

        def parse_businesstypename(businesstype):
            if not businesstype:
                return ''
            if businesstype == '01':
                return u'国内短信'
            elif businesstype == '02':
                return u'国际短信'
            elif businesstype == '03':
                return u'国内彩信'
            elif businesstype == '04':
                return u'国际漫游短信'
            elif businesstype == '05':
                return u'集团短信'
            elif businesstype == '06':
                return u'国际彩信'
            else:
                return ''

        pay_load = response.meta
        pageno = pay_load.get('pageNo', '')
        begin = pay_load.get('begindate', '')

        logging.info(msg='account <%s> parse sms, date: %s pageno: %s' % (self.username, begin, pageno))
        #logging.debug(msg='sms html: %s' % response.body)
        j_read = json.loads(response.body)
        #logging.debug(msg='sms json: %s' % j_read)

        if not j_read.get('isSuccess', ''):
            #"errorMessage":{"respCode":"2114030170","respDesc":"??????2114030170?"}
            # 返回的字节数组就是?????? 但浏览器是怎么做的呢
            reason = j_read.get('errorMessage', '')

            if reason:
                logging.warning(msg='reason: %s' % str(reason).decode('unicode-escape'))
            else:
                logging.warning(msg='not found reason')

            # 标注redis
            return

        userinfo = j_read.get('userInfo', '')
        pagemap = j_read.get('pageMap', '')
        t = []
        if pagemap:
            resultlist = pagemap.get('result', '')
            if resultlist:
                for result in resultlist:
                    dic = {}
                    if userinfo:
                        # 客户姓名
                        dic['custname'] = userinfo.get('custName', '')
                        # 手机号码
                        dic['usernumber'] = userinfo.get('usernumber', '')
                        # 不可见字段（网络类型)
                        dic['nettype'] = userinfo.get('nettype', '')

                    # 短/彩信合计
                    dic['mmscount'] = j_read.get('mmsCount', '')
                    # 查询周期
                    dic['querydatescope'] = combine_datescope(j_read)
                    # 费用合计
                    dic['totalfee'] = j_read.get('totalfee', '')

                    # 起始时间
                    dic['starttime'] = combine_starttime(result)

                    # 发送方式
                    dic['smstype'] = result.get('smstype', '')
                    dic['smstypename'] = parse_smstypename(dic['smstype'])

                    # 业务类型
                    dic['businesstype'] = result.get('businesstype', '')
                    dic['businesstypename'] = parse_businesstypename(dic['businesstype'])

                    # 对方号码
                    dic['othernum'] = result.get('othernum', '')
                    # 费用合计
                    dic['amount'] = result.get('amount', '')
                    t.append(dic)

        smsdetail = {'smsdetail': t}
        #logging.debug(msg='sms struct json: %s' % json.dumps(smsdetail))
        self.tb.insert(colname=u'联通-短彩信详单查询', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=smsdetail, post_dic=pay_load)
        logging.info(msg='insert smsdetail success phone: %s date: %s pageno: %s' % (self.username, begin, pageno))


    def parse_historybill(self, response):
        # 这个确实是有两个版本的

        def historyresultlist2json(j_read):
            dic_tmp = {}
            history = j_read.get('historyResultList', '')
            if history:
                for d in history:
                    billname = d.get('name', '')
                    billvalue = d.get('value', '')
                    dic_tmp[billname] = billvalue
            return json.dumps(dic_tmp)

        pay_load = response.meta
        billdate = pay_load.get('billdate', '')

        logging.debug(msg='historybill html: %s' % response.body)
        j_read = json.loads(response.body)
        #logging.debug(msg='historybill json: %s' % j_read)

        errinfo = j_read.get('errorMessage', '')
        if errinfo:
            logging.warning(msg='request historybill %s failed, reason: %s' % (billdate, str(errinfo).decode('unicode-escape')))
            return

        logging.info(msg='account <%s> parse historybill date:%s' % (self.username, billdate))

        dic = {}
        info = j_read.get('userInfo', '')
        if info:
            dic['custname'] = info.get('custName', '')
            dic['usernumber'] = info.get('usernumber', '')

        dic['nowfee'] = j_read.get('nowFee', '')
        dic['discount'] = j_read.get('discount', '')
        dic['paytotal'] = j_read.get('payTotal', '')
        dic['billcycle'] = j_read.get('billcycle', '').replace(u'至', ' ')
        dic['paysum'] = j_read.get('paySum', '')

        # 动态字段 采用内置json字符串的形式存储，类似于mongo的内置文档
        dic['historyresultlist'] = historyresultlist2json(j_read)

        hsb = {'historybill': [dic, ]}
        #strjson = json.dumps(hsb)
        #logging.debug(msg='historybill struct json: %s' % strjson)

        if dic['nowfee'] or dic['discount'] or dic['paytotal'] or dic['billcycle'] or dic['paysum']:
            self.tb.insert(colname=u'联通-历史账单', url=response.url, html=response.body, charset='utf-8', id=self.userinfo['phone'], token=self.userinfo['token'], struct_dic=hsb, post_dic=pay_load)
            logging.info(msg='insert historybill success phone: %s date: %s' % (self.username, billdate))


    def spider_closed(self, spider):

        if self.ti == 1:
            self.userinfo["code"] = 1001
            self.con.hmset(self.jobid, dict(self.userinfo))
            logging.warning(msg="{%s} spider closed" % spider.name)
        else:
            pass


    def spider_idle(self):

        logger.info(msg="spider_idle")

        if self.ti == 1:
            self.userinfo["code"] = 1001
            self.con.hmset(self.jobid, dict(self.userinfo))
            try:
                con = Util().spider_login_out(method="post", url=self.logouturl_post, cookies=self.sess)
                del con
            except Exception,e:
                pass
        self.schedule_next_requests()
        self.ti = 0
        raise DontCloseSpider

    # 作废, 改版或者字段冗余的请求
    def parse_realtimebill(self, response):

        def parse_period(period):
            print >> sys.stderr, 'period:', period
            if not period:
                return ''
            new_period = period.replace(' 至 ', ' ')
            print >> sys.stderr, 'new_period:', new_period
            return new_period

        def parse_star(star):
            print >> sys.stderr, 'star:', star
            if not star:
                return ''
            new_star = star.replace('用户', '')
            print >> sys.stderr, 'new_star:', new_star
            return new_star

        def parse_package_fee(package_fee, pat=re.compile('(\d+)元')):
            print >> sys.stderr, 'package_fee', package_fee
            if not package_fee:
                return ''
            m = pat.search(package_fee)
            if m:
                price = m.group(1)
                print >> sys.stderr, 'new_package_fee', price
                return price
            return ''

        logger.info(msg='account <%s> get real time bill' % self.username)
        ti = int(time.time() * 1000)
        #logging.debug(msg='real time bill html: %s' % response.body)
        j_read = json.loads(response.body)
        #logging.debug(msg='real time bill json: %s' % j_read)

        #bill_inquiry = {}
        #bill_inquiry['billing_cycle'] = parse_period(j_read.get('period', ''))
        #bill_inquiry['current_consumption'] = ''
        #bill_inquiry['main_account_balance'] = ''
        #bill_inquiry['available_integral'] = ''
        #bill_inquiry['star_level'] = parse_star(j_read.get('custlvl', ''))
        #bill_inquiry['package_fee'] = parse_package_fee(package_fee=j_read.get('packageName', ''))
        #bill_inquiry['foreign_language_fee'] = ''
        #bill_inquiry['internet_access_fee'] = ''
        #bill_inquiry['package_SMS_charges'] = ''
        #bill_inquiry['value_added_service_fee'] = ''
        #bill_inquiry['collection_fee'] = ''
        #bill_inquiry['other_expenses'] = ''

        #expense_detail ={}
        #expense_detail['package_name'] = ''
        #expense_detail['package_fee_details'] = ''

        #e_d = []

        ##b_i = []
        #if j_read.get('rspArgs','') and j_read['rspArgs'].get('result',''):
        #    for fee in j_read['rspArgs']['result']:
        #        if fee.get('title', None) == u'账户可用余额':
        #            bill_inquiry['main_account_balance'] = fee.get('fee', '')
        #        elif fee.get('title', None) == u'实时话费':
        #            bill_inquiry['current_consumption'] = fee.get('fee', '')
        #            if fee.get('content','') !='':
        #                for fees in fee['content']:

        #                    # 这里得new
        #                    expense_detail = {}
        #                    expense_detail['package_name'] = fees[0]
        #                    expense_detail['package_fee_details'] = fees[1]
        #                    e_d.append(expense_detail)

        #                    # 这里需要统计下所有可能的字段
        #                    if u'上网流量费' in fees[0]:
        #                        bill_inquiry['internet_access_fee'] = fees[1]
        #                    elif u'一体化套餐月套餐费' in fees[0]:
        #                        bill_inquiry['package_fee'] = fees[1]
        #                    elif u'增值业务' in fees[0]:
        #                        bill_inquiry['value_added_service_fee'] = fees[1]
        #                    elif u'短信' in fees[0] or u'彩信' in fees[0]:
        #                        bill_inquiry['package_SMS_charges'] = fees[1]
        #                    elif u'通话' in fees[0] or u'语音' in fees[0]:
        #                        bill_inquiry['foreign_language_fee'] = fees[1]
        #                    elif u'代收业务' in fees[0]:
        #                        bill_inquiry['collection_fee'] = fees[1]
        #                    elif u'其他费用' in fees[0]:
        #                        bill_inquiry['other_expenses'] = fees[1]
        #                        # 逻辑错误
        #                        #b_i.append(bill_inquiry)

        #self.tb.insert_bill_statis(phone=self.phone, jobid=self.userinfo['token'], url=response.url+'_yys_bs')
        #logging.info('inser success')

        #self.tb.insert_page(url=response.url+'_yys_bs', phone=self.phone, html=response.body, charset='utf-8',
        #                    struct_json={'bill_inquiry': [bill_inquiry]})
        #logging.info('inser success')

        #self.tb.insert_charge_detail(phone=self.phone, jobid=self.userinfo['token'], url=response.url+'_yys_cd')
        #logging.info('inser success')

        #self.tb.insert_page(url=response.url+'_yys_cd', phone=self.phone, html=response.body, charset='utf-8',
        #                    struct_json={'expense_detail': e_d if e_d else [expense_detail]})
        #logging.info('inser success')

