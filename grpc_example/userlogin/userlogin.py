# --*-- coding:utf-8 --*--

from concurrent import futures
import time
import datetime
import logging
import logging.config
import sys
import grpc
import user_login_pb2
import user_login_pb2_grpc
import gl
import tools
from redisclient import RedisClient
from hbcommon import HBClient
import pbjson
import json
import regionutil


class UserLoginServicerImpl(user_login_pb2_grpc.UserLoginServicer):
    def __init__(self, conf):
        self.logger = logging.getLogger(gl.LOGGERNAME)

        # redis配置
        host = conf.get('redis.host', 'localhost')
        port = conf.getint('redis.port', 6379)
        self.redis = RedisClient(host=host, port=port)

        # hbase 配置
        self.hbase_1 = HBClient()
        # xmd region recognize
        self.regUtil = regionutil.RegionUtil()

        self.telutil = tools.TelUtil(conf=conf)

    def loadSites(self, request, context):

        # 计算时延
        sites = self.redis.getSites()
        res = user_login_pb2.SitesResponse()
        res.sites = sites
        self.logger.info('load site names success')
        return res

    def loginYys(self, request, context):

        token = request.token
        site = request.site
        idcard = request.idcard
        name = request.name
        phone = request.phone
        pwd = request.pwd
        repwd = request.repwd
        sms = request.sms

        line = 'site: %s, token: %s, idcard: %s, name: %s, phone: %s, pwd: %s, repwd: %s, sms: %s' % (
            site, token, idcard, name, phone, pwd, repwd, sms)
        self.logger.info(line)

        # 手机号码判定, 第一步正则判定，第二部区域判定
        if not self.telutil.isPhone(phone=phone):
            response = user_login_pb2.ResponseYYS()
            response.token = token
            response.status = user_login_pb2.FAILED
            response.code = user_login_pb2.YYS_I_PHONE_INVALID
            return response

        #用户信息
        key = '%s_%s_%s' % (site, phone, token)
        dict_req = pbjson.pb2dict(request)

        #下发任务
        if not self.redis.exists(key):
            dict_req['key'] = key
            json_req = json.dumps(dict_req)
            self.redis.issueTask(site, json_req)

        # 判断任务执行情况
        info_dict = self.redis.getLoginInfo1(key)
        #info_dict = json.loads(info_json)
        if 'code' in info_dict:
            code = int(info_dict['code'])
            self.logger.info('repeated task, key:%s code:%s' % (key, code))
            if code == user_login_pb2.YYS_I_SUCCESS:
                self.logger.info('ignore task, reason: repeated, key:%s code:%s' % (key, code))
                response = user_login_pb2.ResponseYYS()
                response.token = token
                response.status = user_login_pb2.SUCCESS
                response.code = code
                return response

        # code 1000 meanless, spider 内部使用
        dict_req['code'] = user_login_pb2.YYS_S_WAIT
        #json_req = json.dumps(dict_req)
        self.redis.setLoginInfo1(key, dict_req)

        start = datetime.datetime.now()
        while True:
            #magic num
            time.sleep(0.5)

            end = datetime.datetime.now()
            delta = (end - start).seconds
            # magic num
            if delta > (60 * 20):
                response = user_login_pb2.ResponseYYS()
                response.token = token
                response.status = user_login_pb2.FAILED
                response.code = user_login_pb2.YYS_I_FETCH_TIMEOUT
                return response

            info_dict = self.redis.getLoginInfo1(key)
            #info_dict = json.loads(info_json)
            code = int(info_dict['code'])
            if code == user_login_pb2.YYS_S_WAIT:
                self.logger.info('key:%s code:%s' % (key, code))
                continue
            elif code == user_login_pb2.YYS_I_SUCCESS:
                self.logger.info('key:%s code:%s' % (key, code))
                response = user_login_pb2.ResponseYYS()
                response.token = token
                response.status = user_login_pb2.SUCCESS
                response.code = code
                return response
            elif code in (user_login_pb2.YYS_I_INPUT_SMS_AGAIN,
                          user_login_pb2.YYS_I_INPUT_SMS,
                          user_login_pb2.YYS_I_PWD_ERR,
                          user_login_pb2.YYS_I_SMS_ERR,
                          user_login_pb2.YYS_I_SMS_INVALID,
                          user_login_pb2.YYS_I_IDCARD_INVALID,
                          user_login_pb2.YYS_I_PWD_SIM_INIT,
                          user_login_pb2.YYS_I_LOGIN_SUCCESS,
                          user_login_pb2.YYS_I_PHONE_INVALID,
                          user_login_pb2.YYS_I_NAME_INVALID,
                          user_login_pb2.YYS_I_PHONE_NOT_SUPPORT,
                          user_login_pb2.YYS_I_SERVICE_OFF,
                          user_login_pb2.YYS_I_CXXD_1001,
                          user_login_pb2.YYS_I_CXXD_1001_AGAIN,
                          user_login_pb2.YYS_I_INPUT_REPWD,
                          1023,
                          user_login_pb2.YYS_I_REPWD_ERR):
                self.logger.info('key:%s code:%s' % (key, code))
                response = user_login_pb2.ResponseYYS()
                response.token = token
                response.status = user_login_pb2.PROCESS
                response.code = code
                return response
            elif code in (user_login_pb2.YYS_I_FETCH_TIMEOUT, user_login_pb2.YYS_I_FETCH_EXCEPTION):
                self.logger.info('key:%s code:%s' % (key, code))
                response = user_login_pb2.ResponseYYS()
                response.token = token
                response.status = user_login_pb2.FAILED
                response.code = code
                return response
            else:
                self.logger.warning('key:%s code:%s INVALID CODE' % (key, code))

    def loginGjj(self, request, context):

        token = request.token
        site = request.site
        idcard = request.idcard
        pwd = request.pwd

        line = 'site: %s, token: %s, idcard: %s, pwd: %s' % (site, token, idcard, pwd, )
        self.logger.info(line)

        #用户信息
        key = '%s_%s_%s' % (site, idcard, token)
        dict_req = pbjson.pb2dict(request)

        if not self.redis.exists(key):
            # 下发任务
            # 同步code为初始状态
            dict_req['code'] = user_login_pb2.GJJ_S_WAIT
            self.redis.setLoginInfo1(key, dict_req)
            # 下发任务
            dict_req['key'] = key
            json_req = json.dumps(dict_req)
            self.redis.issueTask(site, json_req)
        else:
            info_dict = self.redis.getLoginInfo1(key)
            code = int(info_dict['code'])
            if code == user_login_pb2.GJJ_I_PWD_ERR:
                pwd_pre = info_dict['pwd']
                # 如果密码相同, 继续返回GJJ_I_PWD_ERR
                if pwd_pre == pwd:
                    self.logger.info('key:%s code:%s GJJ_I_PWD_ERR AGAIN' % (key, code))
                    response = user_login_pb2.ResponseGJJ()
                    response.token = token
                    response.code = code
                    return response
                # 如果密码发生变化, 则更新下密码
                else:
                    self.redis.modifyLoginInfoPwd(key, pwd)
                    # 置为初始状态
                    self.redis.modifyLoginInfo1(key, user_login_pb2.GJJ_S_WAIT)

        start = datetime.datetime.now()
        while True:
            time.sleep(0.5)
            end = datetime.datetime.now()
            delta = (end - start).seconds
            if delta > (60 * 20):
                response = user_login_pb2.ResponseGJJ()
                response.token = token
                response.status = user_login_pb2.FAILED
                # 登陆超时
                response.code = 2106
                return response

            info_dict = self.redis.getLoginInfo1(key)
            code = int(info_dict['code'])
            # 登录成功
            if code == user_login_pb2.GJJ_I_LOGIN_SUCCESS:
                self.logger.info('key:%s code:%s GJJ_I_LOGIN_SUCCESS' % (key, code))
                response = user_login_pb2.ResponseGJJ()
                response.token = token
                response.code = code
                return response
            # 密码错误：爬虫保证明确密码错误， 密码正确
            elif code == user_login_pb2.GJJ_I_PWD_ERR:
                self.logger.info('key:%s code:%s GJJ_I_PWD_ERR' % (key, code))
                response = user_login_pb2.ResponseGJJ()
                response.token = token
                response.code = code
                return response
            else:
                self.logger.info('key:%s code:%s busy wait' % (key, code))


    #def loginGjj(self, request, context):

    #    token = request.token
    #    site = request.site
    #    idcard = request.idcard
    #    pwd = request.pwd
    #    sms = request.sms

    #    line = 'site: %s, token: %s, idcard: %s, pwd: %s, sms: %s' % (site, token, idcard, pwd, sms)
    #    self.logger.info(line)

    #    #用户信息
    #    key = '%s_%s_%s' % (site, idcard, token)
    #    dict_req = pbjson.pb2dict(request)

    #    #下发任务
    #    if not self.redis.exists(key):
    #        dict_req['key'] = key
    #        json_req = json.dumps(dict_req)
    #        self.redis.issueTask(site, json_req)

    #    # code 1000 meanless, spider 内部使用
    #    dict_req['code'] = user_login_pb2.GJJ_S_WAIT
    #    #json_req = json.dumps(dict_req)
    #    self.redis.setLoginInfo1(key, dict_req)

    #    start = datetime.datetime.now()
    #    while True:
    #        #magic num
    #        time.sleep(0.5)
    #        end = datetime.datetime.now()
    #        delta = (end - start).seconds
    #        if delta > (60 * 20):
    #            response = user_login_pb2.ResponseGJJ()
    #            response.token = token
    #            response.status = user_login_pb2.FAILED
    #            response.code = 2106
    #            return response

    #        info_dict = self.redis.getLoginInfo1(key)
    #        #info_dict = json.loads(info_json)
    #        code = int(info_dict['code'])
    #        if code == user_login_pb2.GJJ_S_WAIT:
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            continue
    #        elif code == user_login_pb2.GJJ_I_SUCCESS:
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            response = user_login_pb2.ResponseGJJ()
    #            response.token = token
    #            response.status = user_login_pb2.SUCCESS
    #            response.code = code
    #            return response
    #        elif code in (user_login_pb2.GJJ_I_LOGIN_SUCCESS,
    #                      user_login_pb2.GJJ_I_PWD_ERR,
    #                      user_login_pb2.GJJ_I_SMS_ERR):
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            response = user_login_pb2.ResponseGJJ()
    #            response.token = token
    #            response.status = user_login_pb2.PROCESS
    #            response.code = code
    #            return response
    #        elif code == user_login_pb2.GJJ_I_FETCH_EXCEPTION:
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            response = user_login_pb2.ResponseGJJ()
    #            response.token = token
    #            response.status = user_login_pb2.FAILED
    #            response.code = code
    #            return response
    #        else:
    #            self.logger.warning('key:%s code:%s INVALID CODE' % (key, code))

    def searchXmdDzdp(self, request, context):
        """仅作为任务下发通道， 更新交给爬虫来做"""

        token = request.token
        shopId = request.shopId
        city = request.city
        shopName = request.shopName
        site = 'XMD_DZDP'

        response = user_login_pb2.ResponseXmdDzdpSearch()
        response.token = token

        try:

            line = 'task received: %s:%s:%s:%s' % (site, shopId, shopName, token)
            self.logger.info(msg=line)

            dict_req = pbjson.pb2dict(request)
            dict_req['site'] = 'XMD_DZDP'
            
            key = '%s_%s' % (site, shopId)
            # 存在则不下发
            if self.redis.exists(key):
                line = 'task exists: %s %s' % (key, token)
                self.logger.info(msg=line)
                response.status = user_login_pb2.SUCCESS
            else:
                # 记录任务时间戳
                dict_req['__tm'] = str(time.time())
                self.redis.setLoginInfo1(key, dict_req)
                
                # 下发任务: 字符串
                task = json.dumps(dict_req)
                self.redis.issueTask(site, task)
                response.status = user_login_pb2.SUCCESS
                line = 'task issue: %s %s' % (key, token)
                self.logger.info(msg=line)
        except Exception as e:
            response.status = user_login_pb2.FAILED
            line = 'task failed: %s %s' % (key, token)
            self.logger.info(msg=line)
            self.logger.exception(e)

        return response

    def getCommentsXmdDzdp(self, request, context):

        token = request.token
        shopID = request.shopID

        line = 'read shopinfo, shopID: %s, token: %s' % (shopID, token)
        self.logger.info(line)

        response = user_login_pb2.ResponseXmdDzdpComment()
        response.token = token
        ####response.status = user_login_pb2.FAILED

        try:
            url = 'https://www.dianping.com/shop/%s' % shopID
            basicinfo = self.hbase_1.getdetail(url)
            comments = self.hbase_1.getcom(shopid=shopID)

            if not basicinfo and not comments:
                response.status = user_login_pb2.FAILED
                self.logger.info(msg='%s not fetch' % shopID)
                return response

            if basicinfo:
                dic_b = {}
                for k, v in basicinfo:
                    if not isinstance(v, basestring):
                        v = str(v)
                    dic_b[k] = v
                response.basicinfo = json.dumps(dic_b)
            else:
                response.basicinfo = 'null'

            if comments:
                for c in comments:
                    response.comments.append(json.dumps(c))

            response.status = user_login_pb2.SUCCESS
        except Exception as e:
            response.status = user_login_pb2.FAILED
            self.logger.exception(e)
        return response


        

        

    #def searchXmdDzdp(self, request, context):
    #    print dir(context)

    #    token = request.token
    #    shopId = request.shopId
    #    city = request.city
    #    shopName = request.shopName
    #    site = 'XMD_DZDP'
    #    #site = 'XMD_DZDP_SN'
    #    #site = 'XMD_DZDP_SI'

    #    # city code transfer to dzdp and mt
    #    num, city = self.regUtil.getNumByCity(city)
    #    if not city:
    #        response = user_login_pb2.ResponseXmdDzdpSearch()
    #        response.token = token
    #        response.status = user_login_pb2.FAILED
    #        #response.code = user_login_pb2.XMD_DZDP_S_I_CITY_NOT_FOUND
    #        response.code = 3005
    #        return response

    #    line = 'site: %s, city: %s, shopname: %s, token: %s' % (site, city, shopName, token)
    #    self.logger.info(line)

    #    # 数据判重
    #    crawled, token_1 = self.redis.isCrawledXmd(site=site, city=city, shopName=shopName)
    #    if crawled:
    #        #read redis
    #        response = user_login_pb2.ResponseXmdDzdpSearch()
    #        response.token = token
    #        response.status = user_login_pb2.SUCCESS
    #        response.code = user_login_pb2.XMD_DZDP_S_I_SUCCESS
    #        shopInfos = self.redis.getShopInfos(key=token_1)
    #        response.shopInfo = shopInfos
    #        return response

    #    #用户信息
    #    key = '%s_%s_%s_%s' % (site, city, shopName, token)
    #    dict_req = pbjson.pb2dict(request)
    #    dict_req['city'] = city

    #    #下发任务
    #    if not self.redis.exists(key):
    #        dict_req['key'] = key
    #        json_req = json.dumps(dict_req)
    #        self.redis.issueTask(site, json_req)

    #        # code 1000 meanless, spider 内部使用
    #        dict_req['code'] = user_login_pb2.XMD_DZDP_S_S_WAIT
    #        #json_req = json.dumps(dict_req)
    #        self.redis.setLoginInfo1(key, dict_req)

    #    start = datetime.datetime.now()
    #    while True:
    #        #magic num
    #        time.sleep(0.5)
    #        end = datetime.datetime.now()
    #        delta = (end - start).seconds
    #        # magic num
    #        if delta > (3600 * 1):
    #            response = user_login_pb2.ResponseXmdDzdpSearch()
    #            response.token = token
    #            response.status = user_login_pb2.FAILED
    #            response.code = 3003
    #            return response
    #        info_dict = self.redis.getLoginInfo1(key)
    #        #info_dict = json.loads(info_json)
    #        code = int(info_dict['code'])
    #        if code == user_login_pb2.XMD_DZDP_S_S_WAIT:
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            response = user_login_pb2.ResponseXmdDzdpSearch()
    #            response.token = token
    #            response.status = user_login_pb2.SUCCESS
    #            response.code = 3000
    #            return response
    #        elif code == user_login_pb2.XMD_DZDP_S_I_SUCCESS:
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            response = user_login_pb2.ResponseXmdDzdpSearch()
    #            response.token = token
    #            response.status = user_login_pb2.SUCCESS
    #            response.code = code
    #            shopInfos = self.redis.getShopInfos(key=token)
    #            response.shopInfo = shopInfos
    #            return response
    #        elif code in (user_login_pb2.XMD_DZDP_S_I_FETCH_EXCEPTION,):
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            response = user_login_pb2.ResponseXmdDzdpSearch()
    #            response.token = token
    #            response.status = user_login_pb2.FAILED
    #            response.code = code
    #            shopInfos = self.redis.getShopInfos(key=token)
    #            response.shopInfo = shopInfos
    #            return response
    #        elif code in (user_login_pb2.XMD_DZDP_S_I_CITY_NOT_FOUND,):
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            response = user_login_pb2.ResponseXmdDzdpSearch()
    #            response.token = token
    #            response.status = user_login_pb2.FAILED
    #            response.code = code
    #            return response
    #        else:
    #            self.logger.warning('key:%s code:%s INVALID CODE' % (key, code))

    #def getCommentsXmdDzdp(self, request, context):

    #    token = request.token
    #    shopID = request.shopID
    #    site = 'XMD_DZDP_SI'

    #    # city code transfer to dzdp and mt

    #    line = 'site: %s, shopID: %s, token: %s' % (site, shopID, token)
    #    self.logger.info(line)

    #    #用户信息
    #    key = '%s_%s_%s' % (site, shopID, token)
    #    dict_req = pbjson.pb2dict(request)

    #    #下发任务
    #    if not self.redis.exists(key):
    #        dict_req['key'] = key
    #        json_req = json.dumps(dict_req)
    #        self.redis.issueTask(site, json_req)

    #    # code 1000 meanless, spider 内部使用
    #    if not self.redis.exists(key):
    #        dict_req['code'] = user_login_pb2.XMD_DZDP_C_S_WAIT
    #        #json_req = json.dumps(dict_req)
    #        self.redis.setLoginInfo1(key, dict_req)

    #    start = datetime.datetime.now()
    #    while True:
    #        #magic num
    #        time.sleep(0.5)
    #        end = datetime.datetime.now()
    #        delta = (end - start).seconds
    #        # magic num
    #        if delta > (3600 * 1):
    #            response = user_login_pb2.ResponseXmdDzdpComment()
    #            response.token = token
    #            response.status = user_login_pb2.FAILED
    #            response.code = 3103
    #            return response
    #        info_dict = self.redis.getLoginInfo1(key)
    #        #info_dict = json.loads(info_json)
    #        code = int(info_dict['code'])
    #        if code == user_login_pb2.XMD_DZDP_C_S_WAIT:
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            response = user_login_pb2.ResponseXmdDzdpComment()
    #            response.token = token
    #            response.status = user_login_pb2.PROCESS
    #            response.code = 3100
    #            return response
    #        elif code == user_login_pb2.XMD_DZDP_C_I_SUCCESS:
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            response = user_login_pb2.ResponseXmdDzdpComment()
    #            response.token = token
    #            response.status = user_login_pb2.SUCCESS
    #            response.code = code
    #            # read hbase
    #            key1 = '%s_%s_%s' % ('XMD_DZDP', shopID, token)
    #            self.logger.info(key1)
    #            # hbase 配置
    #            self.hbase = HbUnicom()
    #            comments = self.hbase.getCommentsByKey(key=key1)
    #            if comments:
    #                for c in comments:
    #                    response.comments.append(c)
    #            return response
    #        elif code in (user_login_pb2.XMD_DZDP_C_I_DISAPPEAR, ):
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            response = user_login_pb2.ResponseXmdDzdpComment()
    #            response.token = token
    #            response.status = user_login_pb2.FAILED
    #            response.code = code
    #            return response
    #        elif code == user_login_pb2.XMD_DZDP_C_I_FETCH_EXCEPTION:
    #            self.logger.info('key:%s code:%s' % (key, code))
    #            response = user_login_pb2.ResponseXmdDzdpComment()
    #            response.token = token
    #            response.status = user_login_pb2.FAILED
    #            response.code = code
    #            # read hbase
    #            key1 = '%s_%s_%s' % ('XMD_DZDP', shopID, token)
    #            self.logger.info(key1)
    #            # hbase 配置
    #            self.hbase = HbUnicom()
    #            comments = self.hbase.getCommentsByKey(key=key1)
    #            if comments:
    #                for c in comments:
    #                    response.comments.append(c)
    #            return response
    #        else:
    #            self.logger.warning('key:%s code:%s INVALID CODE' % (key, code))


def serve(conf):
    max_workers = conf.get(name='server.threadpool.capacity', defaltValue=50)
    port = conf.getint(name='server.port', defaltValue=50051)

    logger = logging.getLogger(gl.LOGGERNAME)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    user_login_pb2_grpc.add_UserLoginServicer_to_server(UserLoginServicerImpl(conf), server)
    server.add_insecure_port('[::]:%s' % port)
    server.start()
    logger.info('server started, listening on  %s' % port)

    try:
        while True:
            time.sleep(gl.ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop()


if __name__ == '__main__':
    fname = None
    if len(sys.argv) == 2:
        fname = sys.argv[1]
    else:
        print sys.stderr, 'err: python userlogin.py ./conf/server.conf'
        exit(1)

    conf = tools.Config(fname=fname)
    logPath = conf.get(name='logs.conf.path', defaltValue='./conf/logging.conf')
    print 'logs conf path:', logPath
    logging.config.fileConfig(logPath)
    serve(conf)
