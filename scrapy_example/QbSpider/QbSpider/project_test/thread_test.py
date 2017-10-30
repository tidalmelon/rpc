# coding=utf-8
#import threadpool
import pycurl
import cStringIO
import time
import pymysql
from lxml import etree
import re
import threading

# body_check_dict = {
#     "site":"keyword",
# }

key_word_ip_xpath = '//*[@id="result"]/div/p[1]/code/text()'

ip_address_xpath = '//*[@id="result"]/div/p[2]/code/text()'


#连接数据库类
class Db(object):
    # DB
    __Config = {
        '_HOST': '127.0.0.1',
        '_NAME': 'root',
        '_PASS': 'toor',
        '_DB': '*****************************',
        '_CHARSET': 'utf8'
    }

    def __init__(self):
        self.__conn = pymysql.connect(host=self.__Config['_HOST'], user=self.__Config['_NAME'],
                                      passwd=self.__Config['_PASS'], db=self.__Config['_DB'],
                                      charset=self.__Config['_CHARSET']);
        self.__cur = self.__conn.cursor(pymysql.cursors.DictCursor)

    def GetProxy(self):
        self.__cur.execute("Select `ip` From `proxy`")
        ips = []
        for r in self.__cur:
            ips.append(r['ip'])
        return ips

    def Insert(self,ip):
        self.__cur.execute("insert into `proxy` Set `speed`='0',`update_time`=NOW(),`ip`='%s'"%ip)
        self.__conn.commit()

    def Delete(self, ip):
        self.__cur.execute("Delete from `proxy` where `ip`='%s'" % ip)
        self.__conn.commit()

    def Update(self, ip, ti, address):
        self.__cur.execute("Update `proxy` Set `speed`='%s',`update_time`=NOW(),`address`='%s' Where `ip`='%s'" %(ti,ip,address))
        self.__conn.commit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__cur.close()
        self.__conn.close()


#实时检测proxy类
class Proxy(object):

    db = Db()

    local_ip = "111.200.62.30"

    url = "http://www.ip.cn/index.php"

    def test_proxy(self,proxy):

        try:

            start_ti = int(time.time()*1000)

            body = GetBody().getbody(True,proxy,self.url)

            if body:

                end_ti = int(time.time() * 1000)

                #毫秒级别
                time_out = end_ti - start_ti

                #此处校验返回的页面内容是否为正常页面
                hxs = etree.HTML(text=body)

                ips = hxs.xpath(key_word_ip_xpath)[0]

                ip = "" if len(ips) == 0 and ips == [[]] else ips[0]

                addresss = hxs.xpath(ip_address_xpath)

                address = "" if len(addresss) == 0 and addresss == [[]] else addresss[0]

                if time_out < 2000 and ip != self.local_ip and ip != "":

                    #将此ip存入数据库中
                    self.db.Update(proxy,time_out,address)

                else:
                    #将此ip从数据库中删除
                    print ("Delete ip %(ip)s"%proxy)
                    self.db.Delete(proxy)
            else:

                # 将此ip从数据库中删除
                self.db.Delete(proxy)

            del body

        except Exception,e:

            #print e.message

            #self.db.Delete(proxy)

            pass

class GetBody(object):

    USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"

    def getbody(self,need_proxy,proxy,url):

        try:

            b = cStringIO.StringIO()

            c = pycurl.Curl()

            c.setopt(pycurl.URL, url)

            c.setopt(pycurl.FOLLOWLOCATION, 1)

            c.setopt(pycurl.USERAGENT, self.USER_AGENT)

            c.setopt(pycurl.TIMEOUT, 2)

            if need_proxy:

                c.setopt(pycurl.PROXY, "http://"+proxy)

            else :

                pass

            c.setopt(pycurl.WRITEFUNCTION, b.write)

            c.perform()

            body = b.getvalue()

            return body

        except Exception,e:

            return None


class GetProxy(object):

    getbody = GetBody()

    db = Db()

    proxys=[
        {
            'Url':'http://www.httpdaili.cn:8082/query?dingdanhao=887720140721951&type=%E9%AB%98%E5%8C%BF&area=&xianlu=all&method=POST&repeat=false&command_check=false&Encoding=gbk&selectall=true&excludePorts=3128,8080&num=1000',
            'Rex':r'([0-9]{1,3}\.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5})[^0-9]{1,1}'
        },
        {
            'Url':'http://www.httpdaili.com/api.asp?ddbh=128475938433142&dk=&old=&killdk=3128,8080&key=%ca%a1&sl=500',
            'Rex':r'([0-9]{1,3}\.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5})[^0-9]{1,1}'
        }]

    for proxy in proxys:

        body = getbody.getbody(False,None,proxy['Url'])

        if body:

            proxy_lists = re.findall(re.compile(r'%s'%proxy['Rex'],re.I),body)

            for ip in proxy_lists:

                if ip:

                    try:
                        db.Insert(ip)
                    except Exception,e:
                        #print e
                        pass


class myThread (threading.Thread):

    def __init__(self, obj,proxy):

        threading.Thread.__init__(self)

        self.obj = obj

        self.proxy = proxy

    def run(self):

        self.obj.test_proxy(self.proxy)

# if __name__ == "__main__":
#
#     threads = []
#
#     proxys = Db().GetProxy()
#
#     if len(proxys) <= 1000:
#
#         GetProxy()
#
#         proxys = Db().GetProxy()
#
#     for proxy in proxys:
#
#         thread = myThread(Proxy(),proxy)
#
#         thread.start()
#
#         threads.append(thread)
#
#     for t in threads:
#
#         t.join()
#
#     del threads
















