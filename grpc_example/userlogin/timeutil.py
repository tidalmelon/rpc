# -*- coding: utf-8 -*-

import time
import datetime


def getCurTimeStamp():
    #return int(time.time() * 1000)
    return int(time.time())

def getCurStrTime():
    t = time.strftime('%Y-%m-%d', time.localtime())
    return t


def getCurStrTime():
    t = time.strftime('%Y-%m-%d', time.localtime())
    return t


def htimestamp2str(timestamp):
    """
    13位时间戳str-日期格式str
    """
    timestamp = timestamp[0: -3]
    timestamp = int(timestamp)
    #t = time.gmtime(timestamp)
    t = time.localtime(timestamp)
    t = time.strftime('%Y-%m-%d', t)
    return t


def formatStrTime(tm, fmt='%Y/%m/%d %H:%M:%S'):
    """
    2014/3/1 13:20:40 -> 2014-03-01(str)
    """
    if not tm:
        return ''
    try:
        t = time.strptime(tm, fmt)
        t = time.strftime('%Y-%m-%d', t)
        return t
    except:
        return ''


def getTimeStamp(days=90):
    return int(time.time()) + 86400 * days


def elapsedTime(start, end):
    """
    {0}H:{1}M:{2}S
    """
    pass

if __name__ == '__main__':
    #print getCurTimeStamp()

    #print getTimeStamp(90)

    #timestamp = '1468383534499'

    #t = htimestamp2str(timestamp)
    #print t


    #astr = '2011/7/4 7:15:23'
    #astr = '2016/8/15 10:13:10'
    #print formatStrTime(astr)

    print getCurStrTime()
