# -*- coding: utf-8 -*-

import threading
import ConfigParser
import gl
import re

lock_config = threading.Lock()


class Config(object):

    __instance = None

    def __init__(self, fname='./conf/server.conf'):
        self.conf = ConfigParser.ConfigParser()
        self.conf.read(fname)

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            try:
                lock_config.acquire()
                if not cls.__instance:
                    cls.__instance = super(Config, cls).__new__(cls, *args, **kwargs)
            finally:
                lock_config.release()
        return cls.__instance

    def get(self, name, defaltValue):
        if self.conf.has_option(gl.SECTION, name):
            return self.conf.get(gl.SECTION, name)
        else:
            return defaltValue

    def getint(self, name, defaltValue):
        if self.conf.has_option(gl.SECTION, name):
            return self.conf.getint(gl.SECTION, name)
        else:
            return defaltValue


class TelUtil(object):
    """
    function:
    ...
    problem list:
    extends to support province telcom
    support vtirtual carrieroperator ?
    support phone in hongkong?
    """

    def __init__(self, conf):
        seg_yd = conf.get('seg_yd', None)
        self.seg_yd = set(seg_yd.split())
        seg_lt = conf.get('seg_lt', None)
        self.seg_lt = set(seg_lt.split())
        # magic num
        self.regPhone = re.compile(r'^1[34578]\d{9}$')

    def getSiteByPhone(self, phone):
        yys = phone[0:3]
        if yys in self.seg_yd:
            return 'YYS_YD'
        if yys in self.seg_lt:
            return 'YYS_LT'
        return None

    def isPhone(self, phone):
        m = self.regPhone.match(phone)
        if m:
            return True
        return False


if __name__ == '__main__':
    con = Config(fname='./conf/server.conf')
    #logPath = con.get('logs.conf.path', 'None')
    #print logPath

    #seg_lt = con.get('seg_yd', None)
    #arr = seg_lt.split()
    #print arr

    fname = './conf/server.conf'
    conf = Config(fname=fname)
    tool = TelUtil(conf=conf)

    print tool.isPhone('18501086711')

