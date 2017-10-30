#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
"""
Date: 2017/05/10 15:07:21
"""

import os
import sys
import json
import hashlib
import time
from urlparse import urlsplit
from urllib import urlencode
from urllib import quote
import datetime

from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
#sys.path.append(os.path.abspath("../"))
sys.path.append(os.path.abspath("../../"))
from QbSpider.hbases import Hbase
from QbSpider.hbases.ttypes import *
from scrapy.utils.project import get_project_settings

d = """currurl
cates
shopname
vshop
numbranch
star
numcomments
meanprice
taste
env
service
addr
tel
busihour
alias
intro
istoptrade
piccount
basic:c_mainregionid
basic:c_categoryname
basic:c_power
basic:c_shopid
basic:c_cityglng
basic:c_cityglat
basic:c_shopname
basic:c_fullname
basic:c_shopglng
basic:c_shopglat
basic:c_shopgroupid
basic:c_address
basic:c_userid
basic:c_citycnname
basic:c_shoppower
basic:c_shoptype
basic:c_publictransit
basic:c_shopcityid
basic:c_categoryurlname
basic:c_cityname
basic:c_maincategoryname
basic:c_cityenname
basic:c_maincategoryid
basic:c_cityid
basic:c_district"""


b = """b_todayhits
b_monthlyhits
b_weeklyhits
b_prevweeklyhit
b_glng
b_glat
b_shoptype
b_newshoptype
b_clienttype
b_cityid
b_phoneno
b_phoneno2
b_adduser
b_addusername
b_lastuser
b_lastusername
b_adddate
b_lastdate
b_address
b_crossroad
b_publictransit
b_shoppower
b_power
b_district
b_newdistrict
b_businesshours
b_shopgroupid
b_shopname
b_branchname
b_shopid"""

p = """p_tuan
p_wai"""


def reverseUrl(url):
    reverse_url = ''
    url = urlsplit(url)

    # reverse host
    reverse_host = '.'.join(url.hostname.split('.')[::-1])
    reverse_url += reverse_host

    # add protocol
    reverse_url += ':'
    reverse_url += url.scheme

    # add port if necessary
    if url.port:
        reverse_url += ':'
        reverse_url += str(url.port)

    # add path
    if url.path:
        reverse_url += url.path

    if url.query:
        reverse_url += '?'
        reverse_url += url.query

    if url.fragment:
        reverse_url += '#'
        reverse_url += url.fragment

    return reverse_url

def unreverseUrl(reversedUrl):

    buff = ''
    pathBegin = reversedUrl.find('/')
    if pathBegin == -1:
        pathBegin = len(reversedUrl)
    sub = reversedUrl[0: pathBegin]
    splits = sub.split(':')

    # protocol
    buff += splits[1]
    buff += '://'

    buff += '.'.join(splits[0].split('.')[::-1])

    # host
    if len(splits) == 3:
        buff += ':'
        buff += splits[2]

    buff += reversedUrl[pathBegin: ]
    return buff


class HBClient(object):
    def __init__(self, detailname='webpage_r', comname='comments'):

        settings = get_project_settings().getdict('PARAMS_CONNECT_HBASE')

        self.host = settings['host']
        self.port = settings['port']
        self.buf = settings['buf']

        self.DetailTabName = detailname
        self.ComTabName = comname

        self.d_t = [e.strip() for e in d.split('\n')]
        self.b_t = [e.strip() for e in b.split('\n')]
        self.p_t = [e.strip() for e in p.split('\n')]

    def __open(self):
        self.transport = TTransport.TBufferedTransport(TSocket.TSocket(self.host, self.port), rbuf_size=self.buf)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = Hbase.Client(self.protocol)
        self.transport.open()

    def __exist(self, rowkey):
        result = self.client.getRow(self.ComTabName, rowkey, None)
        if result:
            return True
        return False

    def __gencomrowkey(self, id, tm, uname, cnt):

        m = hashlib.md5()
        m.update(uname)
        m.update(cnt)
        mdigest = m.hexdigest()

        tm = tm.replace('-', '')
        if not id or not tm or not uname:
            raise Exception('shopid time or uname empty')

        rowkey = '%s_%s_%s' % (id, tm, mdigest)
        return rowkey

    def _urlencode(self, seq, enc):
        values = [(self.to_bytes(k, enc), self.to_bytes(v, enc)) for k, v in seq]
        return urlencode(values, doseq=1)

    def _formaturl(self, url):
        if '?' not in url:
            return url
        arr = url.split('?')

        # 方法2 要保持原序
        uri = arr[0] + '?'
        param = []
        for line in arr[1].split('&'):
            key, val = line.split('=')
            val = quote(val)
            param.append(key + '=' + val)
        uri += '&'.join(param)
        return uri

    def to_bytes(self, text, encoding=None, errors='strict'):
        if isinstance(text, bytes):
            return text
        if encoding is None:
            encoding = 'utf-8'
            return text.encode(encoding, errors)

    def insertanchor(self, url, anchor):
        self.__open()
        rowkey = reverseUrl(url)
        mutations = [Mutation(column="f:bas", value=url),
                     Mutation(column="f:anc", value=anchor)]
        self.client.mutateRow(self.DetailTabName, rowkey, mutations, None)

    def getanchor(self, url):
        self.__open()
        rowkey = reverseUrl(url)
        ajson = self.client.get(self.DetailTabName, rowkey, 'f:anc', None)
        print ajson[0].value


    def insertdetail(self, url, anchor, html, struct_dic, outlinks=None):
        self.__open()
        rowkey = reverseUrl(url)
        
        mutations = [Mutation(column="f:bas", value=url),
                     Mutation(column="f:cnt", value=html),
                     Mutation(column="p:json", value=json.dumps(struct_dic)),
                    ]
        if anchor:
            mutations.append(Mutation(column="f:anc", value=json.dumps(anchor)))
        if outlinks:
            mutations.append(Mutation(column="f:ol", value=outlinks))
        self.client.mutateRow(self.DetailTabName, rowkey, mutations, None)

    def getdetail(self, url):
        self.__open()
        rowkey = reverseUrl(url)
        #ajson = self.client.get(self.DetailTabName, rowkey, 'p:json', None)
        cols = self.client.getRowWithColumns(self.DetailTabName, rowkey,['p:json', 'f:ol'], None)
        if not cols:
            return None

        row = []
        if 'p:json' in cols[0].columns:
            json_d = cols[0].columns['p:json'].value
            dic_d = json.loads(json_d)
            for k in self.d_t:
                if ':' not in k:
                    row.append((k, dic_d[k]))
                else:
                    k1, k2 = k.split(':')
                    row.append((k, dic_d[k1][k2]))

        if 'f:ol' in cols[0].columns:
            links = cols[0].columns['f:ol'].value
            outlinks = links.split('|')
            for outlink in outlinks:
                subrow = self.getbyurl(outlink)
                row.extend(subrow)
        return row

    def getrowkeys(self, prefix='com.dianping.www:https/shop/'):

        def ftime(m):
            m = int(str(m)[0: -3])
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m))

        self.__open()
        rows = []
        id = self.client.scannerOpenWithPrefix(tableName=self.DetailTabName, startAndPrefix=prefix, columns=[], attributes=None)
        while True:
            try:
                result = self.client.scannerGetList(id=id, nbRows=10)
            except:
                break
            if not result:
                break
            for e in result:
                columns = e.columns
                timestamp = None
                if columns:
                    timestamp = columns[columns.keys()[0]].timestamp
                    timestamp = ftime(timestamp)
                rows.append((unreverseUrl(e.row), timestamp))
        return rows

    def getbyurl(self, url):
        self.__open()
        url = self._formaturl(url)
        rowkey = reverseUrl(url)
        
        print url
        row = []
        ajson = self.client.get(self.DetailTabName, rowkey, 'p:json', None)
        if ajson:
            j = ajson[0].value
            dic = json.loads(j)

            if 'Promo' in url:
                for k in self.p_t:
                    v = dic.get(k, '')
                    row.append((k, v))
                return row

            if 'Basic' in url:
                for k in self.b_t:
                    v = dic.get(k, '')
                    row.append((k, v))
                return row

    def insertcom(self, id, tm, uname, cnt, struct_dic):

        """
        insert success: 1
        exist : 2
        """

        self.__open()
        rowkey = self.__gencomrowkey(id, tm, uname, cnt)
        if self.__exist(rowkey):
            return 2

        mutations = [Mutation(column="f:json", value=json.dumps(struct_dic))]
        self.client.mutateRow(self.ComTabName, rowkey, mutations, None)
        return 1

    def __getdatenow(self):
        now = datetime.date.today()
        return now.strftime('%Y-%m-%d')


    def getcom(self, url=None, shopid=None, tbegin=None, tend=None):
        if not url and not shopid:
            # 可以改为扫描全表，负载太大
            raise Exception('url shopid both None')

        if not shopid:
            shopid = url.split('/')[-1].strip()
            if not shopid.isdigit():
                raise Exception('invalid url, shopid must be num/digit')
        self.__open()
        id = None
        if not tbegin:
            id = self.client.scannerOpenWithPrefix(tableName=self.ComTabName, startAndPrefix=shopid, columns=['f:json'], attributes=None)
        else:
            if not tend:
                tend = self.__getdatenow()
            tbegin = tbegin.replace('-', '')
            tend = tend.replace('-', '')
            startrow = '%s_%s' % (shopid, tbegin)
            stoprow = '%s_%s' % (shopid, tend)
            print startrow, stoprow 
            id = self.client.scannerOpenWithStop(tableName=self.ComTabName, startRow=startrow, stopRow=stoprow, columns=['f:json'], attributes=None)

        res = []
        while True:
            try:
                result = self.client.scannerGetList(id=id, nbRows=50)
            except:
                break
            if not result:
                break

            for e in result:
                columns = e.columns
                if columns:
                    v = columns['f:json'].value
                    if v:
                        dic = json.loads(v)
                        res.append(dic)
        return res


if __name__ == '__main__':
    ## detail region
    #url = 'https://www.dianping.com/shop/67056533'
    #url = 'https://www.dianping.com/shop/9811536'
    #url = 'https://www.dianping.com/shop/15859122'
    #url = 'https://www.dianping.com/shop/32610697'
    #url = 'https://www.dianping.com/shop/20779486'
    ##url = 'https://www.dianping.com/shop/notexist'

    #hb = HBClient()
    #row = hb.getdetail(url)
    #for k, v in row:
    #    print k, v
    #print '----------'

    ## comments region
    #url = 'https://www.dianping.com/shop/20779486'
    #url = 'https://www.dianping.com/shop/91027352'
    #cli = HBClient()
    ##res = cli.getcom(url)
    ##res = cli.getcom(url=url, tbegin='2017-05-01')
    #res = cli.getcom(url=url, tbegin='2017-05-01', tend='2017-05-15')
    #for r in res:
    #    print json.dumps(r)
    #    print '----------------'

    cli = HBClient()
    rows = cli.getrowkeys()
    for row in rows:
        print row
