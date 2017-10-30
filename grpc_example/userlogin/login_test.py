# -*- coding: utf-8 -*-

import urllib2
import json
import uuid


def doPost(url, dic):
    request = urllib2.Request(url=url, data=json.dumps(dic))
    request.add_header('Content-Type', 'application/json')
    resp = urllib2.urlopen(request)
    res = resp.read()
    return json.loads(res)


def loadSites(url='http://172.28.40.23:8080/v1/sites', dic=None):
    if not dic:
        dic = {'unamed': 1}
    return doPost(url, dic)


def login(token, site, phone, pwd, sms, url='http://172.28.40.23:8080/v1/yys'):
    dic = {'token': token, 'site': site, 'phone': phone, 'pwd': pwd}
    if sms:
        dic['sms'] = sms
    return doPost(url, dic)


def run(token):
    while True:
        site = raw_input('input site(YYS_LT, YYS_DX, YYS_YD):')
        if site in ['YYS_LT', 'YYS_DX', 'YYS_YD']:
            break

    phone = raw_input('input phone:')
    pwd = raw_input('input pwd:')
    sms = ''

    while True:
        dic = login(token, site, phone, pwd, sms)
        #{"token":"tttttxtt-b4ee-4530-b2c6-62c3f79dbdce","status":"SUCCESS","code":1001}
        status = dic['status']
        code = dic['code']
        if status == 'SUCCESS':
            print 'SUCCESS: status %s code %s' % (status, code)
            break
        elif status == 'PROCESS':
            print 'PROCESS: status %s code %s' % (status, code)
            if code == 1002:
                sms = raw_input('input sms:')
                continue
            elif code == 1009:
                print 'login success: %s' % code
                continue
            else:
                print 'unhandled exception'
                break
        elif status == 'FAILED':
            print 'FAILED: status %s code %s' % (status, code)
            break
        else:
            print 'INVALID: status %s code %s' % (status, code)
            break


if __name__ == '__main__':
    token = uuid.uuid1().get_hex()
    run(token)
