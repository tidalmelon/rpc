# -*- coding: utf-8 -*-

import json
import redis
import threading
from operator import itemgetter
import time

lock_redis = threading.Lock()


class RedisClient(object):
    """
    单例模式
    """

    def __init__(self, host='172.28.40.23', port=6379, password='Qbbigdata'):
        self.host = host
        self.port = port
        self.password = password

    def __set(self, key, value):
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        r.set(key, value)

    def __get(self, key):
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        return r.get(key)

    def __sget(self, key):
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        return r.smembers(key)

    def addSite(self, cate, key, val, name='sites'):
        dic = {}
        if self.exists(name):
            res_json = self.__get(name)
            dic = json.loads(res_json)

        if cate not in dic:
            dic[cate] = {}
        #如果没有则写入， 如果有则重写
        dic[cate][key] = val

        res_json = json.dumps(dic)
        print 'addsite:', res_json
        self.__set(name, res_json)

    def getSites(self, key='sites'):
        dic = self.__get(key)
        dic = dic.decode('utf-8')
        #dic = json.loads(dic)
        print 'getsites:', type(dic), dic
        return dic

    def setLoginInfo1(self, key, val_dic):
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        r.hmset(key, val_dic)

    def getLoginInfo1(self, key):
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        return r.hgetall(key)

    def modifyLoginInfo1(self, key, code):
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        r.hset(key, 'code', code)

    def modifyLoginInfoPwd(self, key, pwd):
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        r.hset(key, 'pwd', pwd)

    def gettimestamp(self, key):
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        tt = r.hget('tm', key)
        if tt:
            return int(tt)
        return None

    def getcode(self, key):
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        code = r.hget('code', key)
        return int(code)

    def setLoginInfo(self, key, val_json):
        self.__set(key, val_json)

    def getLoginInfo(self, key):
        return self.__get(key)

    def modifyLoginInfo(self, key, code):
        res_json = self.__get(key)
        res_dict = json.loads(res_json)
        res_dict['code'] = code

        res_json = json.dumps(res_dict)
        self.setLoginInfo(key, res_json)

    def isCrawledXmd(self, site, city, shopName, code_success=3001):
        """
        special for XMD
        """
        now = int(time.time())
        pattern = '%s_%s_%s*' % (site, city, shopName)
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        keys = r.keys(pattern)
        if keys:
            for key in keys:
                begin = self.gettimestamp(key=key)
                if not begin:
                    continue
                delta = now - begin
                # 如果小于1天，且抓取成功了。
                if delta < 86400 and self.getcode(key=key) == code_success:
                    token = key.split('_')[-1]
                    return True, token
        return False, None

    def issueTask(self, site, value):
        que_name = 'QUEUE_' + site
        #r = redis.Redis(connection_pool=self.pool)
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        r.rpush(que_name, value)

    def getTask(self, site):
        que_name = 'QUEUE_' + site
        #r = redis.Redis(connection_pool=self.pool)
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        return r.lpop(que_name)

    def exists(self, key):
        #r = redis.Redis(connection_pool=self.pool)
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        return r.exists(key)

    def getShopInfos(self, key):
        """
        key: token,
        """
        return self.__get(key)

    def queTaskStatisPhone(self):
        """
        return:
        err:,[]
        lt:[]
        yd:[]
        dx:[]
        """
        r = redis.Redis(host=self.host, port=self.port, password=self.password)
        #keys = r.keys('QUEUE_*')
        dic = {}
        keys = r.keys('YYS_*')
        for key in keys:
            arr = key.split('_')
            if not arr or len(arr) != 4:
                if 'err' in dic:
                    dic['err'].append(key)
                else:
                    dic['err'] = [key]
            yys, phone = arr[1:3]

            if yys in dic:
                if phone in dic[yys]:
                    dic[yys][phone] += 1
                else:
                    dic[yys][phone] = 1
            else:
                dic[yys] = {}
        return dic

if __name__ == '__main__':
    # 下发大众点评任务
    import sys
    import json

    #shopid = sys.argv[1]
    for line in sys.stdin:
        url = line.split()[0]
        shopid = url.split('/')[-1]
        #print shopid
        
        shopid = str(shopid)
        cli = RedisClient()

        task = {'shopid': shopid}
        task_json = json.dumps(task)
        cli.issueTask('XMD_DZDP', task_json)

    #cli = RedisClient()
    ##cli.issueTask('YYS_LT', 'task1')
    #res = cli.getTask('YYS_LT')
    #print res

    #cli = RedisClient()
    #cli.test_type()


    #cli = RedisClient()
    #key = u'XMD_DZDP_SN_2_眉州东坡酒楼(昌平店)_dzdp_14f0b8c8-b4ee-4530-b2c6-62c3f79dbdce0011'
    #key = u'XMD_DZDP_SN_2_康二姐串串香天通苑店(原盘古店)_qqqq-b4ee-4530-b2c6-62c3f79dbdce'
    #key = u'XMD_DZDP_SN_2_康二姐串串香_eeee0307-b4ee-4530-b2c6-62c3f79dbdce'
    #key = u'XMD_DZDP_SN_2_眉州东坡酒楼·婚宴_eeee0309009-b4ee-4530-b2c6-62c3f79dbdce'
    #key = u'XMD_DZDP_SN_2_丰茂烤串l羊肉现穿才好吃(知春路店)_3ecfb2a6fd96a1a34d6102283ac1bd2c'
    #key = u'XMD_DZDP_SN_2_丰茂烤串l羊肉现穿才好吃(知春路店)_3ecfb2a6fd96a1a34d6102283ac1bd2c'
    #key = 'XMD_DZDP_SI_66550944_f891a9f404cb11e787ad5a29abf1bafd'
    #key = u'XMD_DZDP_SN_173_国美电器_59b08d80c9f40587b7649fdb7d468a1d'
    #cli.modifyLoginInfo1(key, 3101)
    #print cli.getLoginInfo1(key=key)

    # 获取商户列表
    #token = '59b08d80c9f40587b7649fdb7d468a1d'
    #cli = RedisClient()
    #print cli.getShopInfos(token)

    # 更改状态示例（爬虫)
    #import sys
    #import json
    #key = sys.argv[1]
    #code = int(sys.argv[2])
    #print 'key: ', key
    #print 'code change to: ', code

    #cli = RedisClient()
    #cli.modifyLoginInfo(key, code)

    pass
