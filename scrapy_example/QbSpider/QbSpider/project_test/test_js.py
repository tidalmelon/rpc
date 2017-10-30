
# -*- coding: utf-8 -*-


# import re
import bs4
import requests
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

import os
import sys
import time
import json
import random

import argparse
from selenium import webdriver

# get function name
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name


def tags_val(tag, key='', index=0):
    '''
    return html tag list attribute @key @index
    if @key is empty, return tag content
    '''
    if len(tag) == 0 or len(tag) <= index:
        return ''
    elif key:
        return tag[index].get(key)
    else:
        return tag[index].text


def tag_val(tag, key=''):
    '''
    return html tag attribute @key
    if @key is empty, return tag content
    '''
    if tag is None:
        return ''
    elif key:
        return tag.get(key)
    else:
        return tag.text


class JDSpider(object):
    '''
    This class used to simulate login JD
    '''

    def __init__(self, usr_name, usr_pwd):
        # cookie info
        self.trackid = ''
        self.uuid = ''
        self.eid = ''
        self.fp = ''

        self.usr_name = usr_name
        self.usr_pwd = usr_pwd

        self.interval = 0

        # init url related
        self.home = 'https://passport.jd.com/new/login.aspx'
        self.login = 'https://passport.jd.com/uc/loginService'
        self.imag = 'https://authcode.jd.com/verify/image'
        self.auth = 'https://passport.jd.com/uc/showAuthCode'

        self.sess = requests.Session()
        self.sess.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'ContentType': 'application/x-www-form-urlencoded; charset=utf-8',
            'Connection': 'keep-alive',
        }

        try:
            self.browser = webdriver.PhantomJS('phantomjs.exe')
        except Exception, e:
            print 'Phantomjs initialize failed :', e
            exit(1)

    @staticmethod
    def print_json(resp_text):
        '''
        format the response content
        '''
        if resp_text[0] == '(':
            resp_text = resp_text[1:-1]

        for k, v in json.loads(resp_text).items():
            print u'%s : %s' % (k, v)

    @staticmethod
    def response_status(resp):
        if resp.status_code != requests.codes.OK:
            print 'Status: %u, Url: %s' % (resp.status_code, resp.url)
            return False
        return True

    def need_auth_code(self, usr_name):
        # check if need auth code
        #
        auth_dat = {
            'loginName': usr_name,
        }
        payload = {
            'r': random.random(),
            'version': 2015
        }

        resp = self.sess.post(self.auth, data=auth_dat, params=payload)
        if self.response_status(resp):
            js = json.loads(resp.text[1:-1])
            return js['verifycode']

        print u'获取是否需要验证码失败'
        return False

    def get_auth_code(self, uuid):
        # image save path
        image_file = os.path.join(os.getcwd(), 'authcode.jfif')

        payload = {
            'a': 1,
            'acid': uuid,
            'uid': uuid,
            'yys': str(int(time.time() * 1000)),
        }

        # get auth code
        r = self.sess.get(self.imag, params=payload)
        if not self.response_status(r):
            print u'获取验证码失败'
            return False

        with open(image_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

            f.close()

        os.system('start ' + image_file)
        return str(raw_input('Auth Code: '))

    def login_once(self, login_data):
        # url parameter
        payload = {
            'r': random.random(),
            'uuid': login_data['uuid'],
            'version': 2015,
        }

        resp = self.sess.post(self.login, data=login_data, params=payload)
        if self.response_status(resp):
            js = json.loads(resp.text[1:-1])
            # self.print_json(resp.text)

            if not js.get('success'):
                print  js.get('emptyAuthcode')
                return False
            else:
                return True

        return False

    def login_try(self):
        # get login page
        # resp = self.sess.get(self.home)
        print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        print u'{0} > 登陆'.format(time.ctime())

        try:
            # 2016/09/17 PhantomJS can't login anymore
            self.browser.get(self.home)
            soup = bs4.BeautifulSoup(self.browser.page_source, "html.parser")

            # set cookies from PhantomJS
            for cookie in self.browser.get_cookies():
                self.sess.cookies[cookie['name']] = str(cookie['value'])

            # for (k, v) in self.sess.cookies.items():
            #	print '%s: %s' % (k, v)

            # response data hidden input == 9 ??. Changed
            inputs = soup.select('form#formlogin input[type=hidden]')
            rand_name = inputs[-1]['name']
            rand_data = inputs[-1]['value']
            token = ''

            for idx in range(len(inputs) - 1):
                id = inputs[idx]['id']
                va = inputs[idx]['value']
                if id == 'token':
                    token = va
                elif id == 'uuid':
                    self.uuid = va
                elif id == 'eid':
                    self.eid = va
                elif id == 'sessionId':
                    self.fp = va

            auth_code = ''
            if self.need_auth_code(self.usr_name):
                auth_code = self.get_auth_code(self.uuid)
            else:
                print u'无验证码登陆'

            login_data = {
                '_t': token,
                'authcode': auth_code,
                'chkRememberMe': 'on',
                'loginType': 'f',
                'uuid': self.uuid,
                'eid': self.eid,
                'fp': self.fp,
                'nloginpwd': self.usr_pwd,
                'loginname': self.usr_name,
                'loginpwd': self.usr_pwd,
                rand_name: rand_data,
            }

            login_succeed = self.login_once(login_data)
            if login_succeed:
                self.trackid = self.sess.cookies['TrackID']
                print u'登陆成功 %s' % self.usr_name
            else:
                print u'登陆失败 %s' % self.usr_name

            return login_succeed

        except Exception, e:
            print 'Exception:', e.message
            print e

        return False

    def cart_detail(self):
        # list all goods detail in cart
        cart_url = 'http://cart.jd.com/cart.action'
        cart_header = u'购买    数量    价格        总价        商品'
        cart_format = u'{0:8}{1:8}{2:12}{3:12}{4}'

        try:
            resp = self.sess.get(cart_url)
            soup = bs4.BeautifulSoup(resp.text, "html.parser")

            print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++'
            print u'{0} > 购物车明细'.format(time.ctime())
            print cart_header

            items = soup.select('div.item-form')
            for item in items:
                check = tags_val(item.select('div.cart-checkbox input'), key='checked')
                check = ' Y' if check else ' -'
                count = tags_val(item.select('div.quantity-form input'), key='value')
                price = tags_val(item.select('div.p-price strong'))
                sums = tags_val(item.select('div.p-sum strong'))
                gname = tags_val(item.select('div.p-name a'))
                print cart_format.format(check, count, price, sums, gname)

            t_count = tags_val(soup.select('div.amount-sum em'))
            t_value = tags_val(soup.select('span.sumPrice em'))
            print u'总数: {0}'.format(t_count)
            print u'总额: {0}'.format(t_value)

        except Exception, e:
            print 'Exp {0} : {1}'.format(FuncName(), e)


if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and buy sepecified good')
    parser.add_argument('-u', '--username',
                        help='Jing Dong login user name', default='')
    parser.add_argument('-p', '--password',
                        help='Jing Dong login user password', default='')


    options = parser.parse_args()

    if options.password == '' or options.username == '':
        print u'请输入用户名密码'
        exit(1)

    jd = JDSpider(options.username, options.password)
    jd.login_try()
    jd.cart_detail()
