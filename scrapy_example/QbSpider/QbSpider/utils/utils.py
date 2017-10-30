# coding=utf-8
import sys, os
sys.path.append(os.path.abspath("../../"))
sys.setrecursionlimit(1500)
import json
import re
import logging
from os.path import join,dirname,pardir
import requests
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
import time
import Queue
import datetime
import pymysql
from scrapy.utils.project import get_project_settings
import random
from RedisUtil import RedisConfUtil as rcu
con = rcu().get_redis()
from scrapy.spidermiddlewares.depth import DepthMiddleware

def get_catch(func):

    def try_catch(arg1,arg2,arg3):

        try:
            func(arg1,arg2,arg3)
        except Exception,e:
            jobid = arg1.metas.get("key", "")
            arg1.metas["code"] = 1999
            con.hmset(jobid,dict(arg1.metas))

    return get_catch


class Util(object):



    def __init__(self):

        self.settings = get_project_settings()

        self.proxys = []


    def fetch_new_proxyes(self):
        mysqlset = self.settings.getdict("PROXY_MYSQL")
        conn = pymysql.connect(
            host=mysqlset['Host'],
            user=mysqlset['User'],
            passwd=mysqlset['Passwd'],
            db=mysqlset['Db'],
            charset=mysqlset['Charset']
        )
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(self.settings.get("PROXY_SQL"))
        for r in cur:
            ips = "http://" + r['ip']
            if ips not in self.proxys:
                self.proxys.append(ips)
        cur.close()
        conn.close()






    @staticmethod
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

    #check the str contains chinese
    def check_contain_chinese(check_str):
        for ch in check_str.decode('utf-8'):
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    #find some file and get the file path abspath
    def closest_scrapy_cfg(self,path='.', prevpath=None, filepath=None):
        """Return the path to the closest scrapy.cfg file by traversing the current
        directory and its parents

        @:ivar path parent path or grandparents path

        @:ivar filepath file path
        """
        if path == prevpath:
            return ''
        #path = os.path.abspath(path)
        path = os.path.abspath(join(os.path.dirname(__file__),pardir))
        cfgfile = os.path.join(path, filepath)
        if os.path.exists(cfgfile):
            return cfgfile
        #return self.closest_scrapy_cfg(os.path.dirname(path), path,filepath)
        else:

            logging.error("{%s} not found in {%s}"%(filepath,path))

            raise Exception


    #use request lib execute loginout
    def spider_login_out(self, method=None, url=None, cookies=None, meta=None):

        if method == "get":

            requests.get(url, cookies=cookies, verify=False)

        else:

            requests.post(url, cookies=cookies,  verify=False)

        # if len(self.proxys) == 0:
        #
        #     self.fetch_new_proxyes()
        #
        # proxy = random.choice(self.proxys)
        #
        # flag = False
        #
        # try:
        #
        #     if method == "get":
        #
        #         requests.get(url,cookies=cookies,proxies={"http":proxy},verify=False)
        #
        #     else:
        #
        #         requests.post(url, cookies=cookies,proxies={"http":proxy},verify=False)
        #
        #     flag = True
        #
        # except Exception,e:
        #
        #     logging.error(e.message)
        #
        #     self.proxys.remove(proxy)
        #
        #     return self.spider_login_out(url, cookies)
        #
        # if not flag:
        #
        #     self.proxys.remove(proxy)
        #
        #     return self.spider_login_out(url,cookies)


    def getlastdays(self, numofdays):
        """
        reverse
        """
        queue = Queue.Queue()
        end = datetime.date.today()
        for i in range(numofdays):
            current = end - datetime.timedelta(days=i)
            queue.put(current)
        return queue

    def getlastmonths(self, numofmon=6):
        """
        reverse
        """
        queue = Queue.Queue()
        end = datetime.date.today()
        begin = end.replace(day=1)
    
        for i in range(numofmon):
            end = begin - datetime.timedelta(days=1)
            begin = end.replace(day=1)
            queue.put((begin, end))
        return queue


    def getlast6month(self):

        """
        get last 6 months besides current month tuple[begin: end]
        """

        months = []
        end = datetime.date.today()
        begin = end.replace(day=1)
        months.append((begin, end))

        for i in range(5):
            end = begin - datetime.timedelta(days=1)
            begin = end.replace(day=1)
            months.append((begin, end))
        return months


    def getlast6month_1(self):
        """
        get last 6 months except current month tuple[begin: end]
        """
        months = []
        end = datetime.date.today()
        begin = end.replace(day=1)
        #months.append((begin, end))
    
        for i in range(6):
            end = begin - datetime.timedelta(days=1)
            begin = end.replace(day=1)
            months.append((begin, end))
            #months.append((str(begin), str(end)))
        return months


    #obtain haflyear month and the day that ervry month own
    def gethalfyearmonth(self):
        realdate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        realmonth = int(realdate[5:7])
        realyear = int(realdate[0:4])
        daycount_month = {"31": ["01", "03", "05", "07", "08", "10", "12"], "30": ["04", "06", "09", "11"], }
        if realyear%4 == 0:
            special_mon = {"29":["02"]}
            daycount_month.update(special_mon)
        else:
            special_mon = {"28":["02"]}
            daycount_month.update(special_mon)
        monthlist = []
        for x in xrange(0, 6):
            if realmonth > x:
                month = "0" + str(realmonth - x) if len(str(realmonth - x)) == 1 else str(realmonth - x)
                ym = str(realyear) + "-" + month
            else:
                y = str(x+7) if x+7 >=10 else "0"+str(x+7)
                ym = str(realyear - 1) + "-" + y
            if ym[5:7] == realdate[5:7]:
                day = {(realdate[:-2]+"01"): realdate}
            else:
                for k, v in daycount_month.iteritems():
                    if ym[5:7] in v:
                        day = {(ym + "-01"):(ym + "-%s" % k)}
            monthlist.append(day)
        return monthlist


    def getnexthalfyearmonth(self):

        realdate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        realmonth = int(realdate[5:7])
        realyear = int(realdate[0:4])
        daycount_month = {"31": ["01", "03", "05", "07", "08", "10", "12"], "30": ["04", "06", "09", "11"], }
        if realyear%4 == 0:
            special_mon = {"29":["02"]}
            daycount_month.update(special_mon)
        else:
            special_mon = {"28":["02"]}
            daycount_month.update(special_mon)
        monthlist = []
        for x in xrange(1, 7):
            if realmonth > x:
                month = "0" + str(realmonth - x) if len(str(realmonth - x)) == 1 else str(realmonth - x)
                ym = str(realyear) + "-" + month
            else:
                y = str(x+6) if x+6 >=10 else "0"+str(x+6)
                ym = str(realyear - 1) + "-" + y
            if ym[5:7] == realdate[5:7]:
                day = {(realdate[:-2]+"01"): realdate}
            else:
                for k, v in daycount_month.iteritems():
                    if ym[5:7] in v:
                        day = {(ym + "-01"):(ym + "-%s" % k)}
            monthlist.append(day)
        return monthlist


if __name__ == "__main__":
    #print Util().gethalfyearmonth()
    #print Util().getlast6month_1()
    #print Util().getlast6month()

    #que = Util().getlastdays(10)
    #while not que.empty():
    #    print que.get()

    que = Util().getlastmonths()
    while not que.empty():
        print que.get()



#getlast6month
#[(datetime.date(2017, 4, 1), datetime.date(2017, 4, 7)), (datetime.date(2017, 3, 1), datetime.date(2017, 3, 31)), (datetime.date(2017, 2, 1), datetime.date(2017, 2, 28)), (datetime.date(2017, 1, 1), datetime.date(2017, 1, 31)), (datetime.date(2016, 12, 1), datetime.date(2016, 12, 31)), (datetime.date(2016, 11, 1), datetime.date(2016, 11, 30))]


#getlast6month_1
#[(datetime.date(2017, 3, 1), datetime.date(2017, 3, 31)), (datetime.date(2017, 2, 1), datetime.date(2017, 2, 28)), (datetime.date(2017, 1, 1), datetime.date(2017, 1, 31)), (datetime.date(2016, 12, 1), datetime.date(2016, 12, 31)), (datetime.date(2016, 11, 1), datetime.date(2016, 11, 30)), (datetime.date(2016, 10, 1), datetime.date(2016, 10, 31))]


