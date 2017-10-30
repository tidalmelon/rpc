# -*- coding: utf-8 -*-
import os
import sys
import uuid
import traceback

sys.path.append(os.path.abspath("../"))
import time
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from QbSpider.hbases import Hbase
from QbSpider.hbases.ttypes import *
import json


class HbUnicom(object):
    """
    172.28.40.43:9090 thrift1
    基本原则：一次请求入一次库
    """

    mapping = {'yys_lt_al': 'YYS_LT_%s_%s'}

    def __init__(self, host='172.28.40.23', port=9090, buf=512, pageName='login_key_page', keysName='login_user_keys'):
    #def __init__(self, host='172.28.40.45', port=9090, buf=512, pageName='login_key_page', keysName='login_user_keys'):
    #def __init__(self, host='172.28.40.43', port=9090, buf=512, pageName='login_key_page', keysName='login_user_keys'):

        self.keysName = keysName
        self.pageName = pageName
        self.host = host
        self.port = port
        self.buf = buf

        self.row = 'YYS_LT_%s_%s'
        self.value_key = 'YYS_LT_%s_%s'
        self.split_char = '\t'

        self.__open()

    def __open(self):
        self.transport = TTransport.TBufferedTransport(TSocket.TSocket(self.host, self.port), rbuf_size=self.buf)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = Hbase.Client(self.protocol)
        self.transport.open()


    def __gentm(self):
        return str(int(time.time()))


    def __inserttm(self, rowkey):
        mutations = [Mutation(column="c:yys_lt_tm", value=self.__gentm())]
        self.client.mutateRow(self.keysName, rowkey, mutations, None)


    def __insertpage(self, rowkey, url, html, struct_dic, post_dic=None, charset='utf-8'):

        if not html:
            # 如果源码为空，返回
            return

        try:
            post_data = None
            if post_dic:
                post_data = json.dumps(post_dic)

            mutations = [Mutation(column="f:url", value=url),
                         Mutation(column="f:cnt", value=html),
                         Mutation(column="f:typ", value=charset),
                         Mutation(column="f:pst", value=post_data),
                         Mutation(column="f:tm", value=self.__gentm()),
                         Mutation(column="p:json", value=json.dumps(struct_dic))]
            self.client.mutateRow(self.pageName, rowkey, mutations, None)
        except Exception, e:
            print traceback.format_exc()
            print e.message
            print 'rowkey:', row_key
            print 'data:', struct_json

    def insert(self, url, html, charset, userinfo, struct_dic, post_dic=None):
        """
        用户登录记录
        """

        self.__open()
        phone = userinfo.get('phone', '')
        token = userinfo.get('token', '') 

        row_key = self.row % (phone, token)
        value_key = self.value_key % (phone, uuid.uuid1().get_hex())
        value_key1 = value_key + self.split_char
        try:
            append = TAppend(table=self.keysName, row=row_key, columns=['c:yys_lt_al'], values=[value_key1])
            self.client.append(append)
            self.__inserttm(row_key)
            
            self.__insertpage(value_key, url, html, struct_dic, post_dic, charset)

        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', value_key


    def insert_accesslog(self, url, html, charset, userinfo, struct_dic, post_dic=None):
        """
        用户登录记录
        """

        self.__open()
        phone = userinfo.get('phone', '')
        token = userinfo.get('token', '') 

        row_key = self.row % (phone, token)
        value_key = self.value_key % (phone, uuid.uuid1().get_hex())
        value_key1 = value_key + self.split_char
        try:
            append = TAppend(table=self.keysName, row=row_key, columns=['c:yys_lt_al'], values=[value_key1])
            self.client.append(append)
            self.__inserttm(row_key)
            
            self.__insertpage(value_key, url, html, struct_dic, post_dic, charset)

        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', value_key






    def __del__(self):
        self.transport.close()

    def __genkey(self, phone, url, post_data):
        if isinstance(post_data,int):
            post_data = str(post_data)
        row_key = '%s_%s' % (phone, url)
        if post_data:
            row_key += '_' + post_data
        return row_key


    #def insert_page(self, url, phone, html, charset, struct_json, post_data=None):
    #    """
    #    schema:
    #    f:url -> 网页地址
    #    f:cnt -> 网页
    #    f:typ -> 网页编码
    #    p:json -> 结构化数据json
    #    """
    #    try:
    #        row_key = self.__genkey(phone, url, post_data)
    #        mutations = [Mutation(column="f:url", value=url),
    #                     Mutation(column="f:cnt", value=html),
    #                     Mutation(column="f:typ", value=charset),
    #                     Mutation(column="f:tm", value=self.__gentm()),
    #                     Mutation(column="p:json", value=json.dumps(struct_json))]
    #        self.client.mutateRow(self.pageName, row_key, mutations, None)
    #    except Exception, e:
    #        print traceback.format_exc()
    #        print e.message
    #        print 'rowkey:', row_key
    #        print 'data:', struct_json

    def insert_person_info(self, phone, jobid, url, post_data=None):
        """
        用户信息:个人信息
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'
        try:
            append = TAppend(table=self.keysName, row=row_key, columns=['c:yys_pi'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_bill_statis(self, phone, jobid, url, post_data=None):
        """
        账单查询:六个月的话费统计
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.keysName, row=row_key, columns=['c:yys_bs'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_bill_detail(self, phone, jobid, url, post_data=None):
        """
        详单查询:
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.keysName, row=row_key, columns=['c:yys_bd'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_account_info(self, phone, jobid, url, post_data=None):
        """
        账户信息：
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.keysName, row=row_key, columns=['c:yys_ai'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_charge_detail(self, phone, jobid, url, post_data=None):
        """
        费用明细:
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.keysName, row=row_key, columns=['c:yys_cd'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_remain_score(self, phone, jobid, url, post_data=None):
        """
        积分余额
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.keysName, row=row_key, columns=['c:yys_rs'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_commu_amount(self, phone, jobid, url, post_data=None):
        """
        通信量
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.keysName, row=row_key, columns=['c:yys_ca'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_account_detail(self, phone, jobid, url, post_data=None):
        """
        账户明细
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.keysName, row=row_key, columns=['c:yys_ad'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

