# encoding:utf8
import os, urllib2, time


class dailog(object):
    def __init__(self, num):
        super(dailog, self).__init__()
        self.num = num

    def check(self):
        num = self.num
        num1 = 0
        url = ['http://www.163.com', 'http://www.baidu.com', 'http://www.sina.com.cn']
        res = []
        while True:
            for x in url:
                try:
                    s = urllib2.urlopen(x)
                    res.append(s)
                except:
                    res.append(None)
                if not any(res):
                    print ("rasdial dai 057117114392 525953")  # dai:宽带连接名称,gb39301:账号,111111:密码
                    os.popen("rasdial dai /d")
                    os.popen("rasdial dai 57117114392 525953")
                    num1 += 1
                    print "*"*66
                else:
                    print "network is ok"
                time.sleep(num)
                if num1 == 10:
                    print "try reconect 10 ago ,error"
                    break


if __name__ == '__main__':
    p = dailog(180)
    p.check()
