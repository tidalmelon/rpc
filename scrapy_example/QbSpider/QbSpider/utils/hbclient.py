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
from scrapy.utils.project import get_project_settings
import time


class HbClient(object):

    split_char = '\t'

    mapping = {
                u'联通-个人信息': ('yys_lt_cl', 'YYS_LT'),
                u'联通-登录记录': ('yys_lt_al', 'YYS_LT'),
                u'联通-通话详单': ('yys_lt_cd', 'YYS_LT'),
                u'联通-历史账单': ('yys_lt_hb', 'YYS_LT'),
                u'联通-账户余额': ('yys_lt_ab', 'YYS_LT'),
                u'联通-手机上网流量详单': ('yys_lt_cf', 'YYS_LT'),
                u'联通-增值业务详单': ('yys_lt_va', 'YYS_LT'),
                u'联通-积分查询': ('yys_lt_sq', 'YYS_LT'),
                u'联通-短彩信详单查询': ('yys_lt_sd', 'YYS_LT'),
                u'联通-沃家成员信息': ('yys_lt_gi', 'YYS_LT'),
                u'联通-手机上网记录': ('yys_lt_cnpr', 'YYS_LT'),
                u'联通-实时话费': ('yys_lt_rt', 'YYS_LT'),
                u"公积金-湖南-信息查询 ":('gjj_hunan_bs', 'GJJ_HUNAN'),
                u"公积金-湖南-明细查询 ":('gjj_hunan_dt', 'GJJ_HUNAN'),
                u"公积金-湖南-贷款信息查询 ":('gjj_hunan_la', 'GJJ_HUNAN'),
                u"公积金-湖南-信息查询":('gjj_bs', 'GJJ_HUNAN'),
                u"公积金-湖南-明细查询":('gjj_dt', 'GJJ_HUNAN'),
                u"公积金-湖南-贷款信息查询":('gjj_la', 'GJJ_HUNAN'),
              }

    def __init__(self, pageName='login_key_page', keysName='login_user_keys'):

        settings = get_project_settings().getdict('PARAMS_CONNECT_HBASE')

        self.keysName = keysName
        self.pageName = pageName
        self.host = settings['host']
        self.port = settings['port']
        self.buf = settings['buf']

        self.reversemapping = self.__reversemapping()

    def __open(self):
        self.transport = TTransport.TBufferedTransport(TSocket.TSocket(self.host, self.port), rbuf_size=self.buf)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = Hbase.Client(self.protocol)
        self.transport.open()


    def __gentm(self):
        return str(int(time.time()))


    def __reversemapping(self):
        dic = {}
        for k in self.mapping:
            col, site = self.mapping[k]

            if site not in dic:
                dic[site] = {}

            if col in dic[site]:
                raise Exception('repeated columns %s' % col)

            dic[site][col] = k
        return dic

    def __insertpage(self, rowkey, url, html, struct_dic, row_key, post_dic=None, charset='utf-8'):

        if not html:
            return
        if struct_dic:
            alist = struct_dic[struct_dic.keys()[0]]
            if alist:
                for d in alist:
                    d['pagekey'] = rowkey
                    d['rowkey'] = row_key

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
            print 'rowkey:', rowkey
            print 'data:', struct_dic

    def insert(self, colname, url, html, struct_dic, id, token, charset='utf-8',post_dic=None):

        colname, std = self.mapping.get(colname, ('', ''))
        row_std = std + '_%s_%s'
        value_std = std + '_%s_%s_%s'

        if not colname:
            raise exception('colname not exists')

        row_key = row_std % (id, token)

        value_key = value_std % (id, colname, uuid.uuid1().get_hex())
        value_key1 = value_key + self.split_char
        try:
            self.__open()
            col = 'c:%s' % colname
            append = TAppend(table=self.keysName, row=row_key, columns=[col], values=[value_key1])
            self.client.append(append)
            self.__insertpage(rowkey=value_key, url=url, html=html, struct_dic=struct_dic, row_key=row_key, post_dic=post_dic, charset=charset)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', value_key

    def selectasdict(self, rowkey):
        """
        return rowkey, dict
        """
        self.__open()
        trowresult = self.client.getRow(self.keysName, rowkey, None)
        if not trowresult:
            return rowkey, {}

        bigdic = {}
        # 取列名
        dic_col = trowresult[0].columns
        for col in dic_col:
            # 取列key
            arr = dic_col[col].value.strip().split(self.split_char)
            if not arr:
                continue

            if len(arr) == 1:
                pagekey = arr[0]
                presult = self.client.get(self.pageName, pagekey, 'p:json', None)
                if presult:
                    dic_11 = json.loads(presult[0].value)
                    bigdic[col] = dic_11
            else:
                dic_merged = {}
                k_1 = None
                for pkey in arr:
                    tmp = self.client.get(self.pageName, pkey, 'p:json', None)
                    if not tmp:
                        continue
                    tmp_dic = json.loads(tmp[0].value)
                    if not dic_merged:
                        dic_merged = tmp_dic
                        k_1 = dic_merged.keys()[0]
                    else:
                        dic_merged[k_1].extend(tmp_dic[k_1])
                bigdic[col] = dic_merged
        return rowkey, bigdic


    def select(self, rowkey):
        self.__open()
        trowresult = self.client.getRow(self.keysName, rowkey, None)
        if not trowresult:
            yield rowkey, None, None, None, None
        else:
            site = '_'.join(rowkey.split('_')[0: 2])
            rmap = self.reversemapping[site]

            dic_col = trowresult[0].columns
            for col in dic_col:
                arr = dic_col[col].value.strip().split(self.split_char)
                if not arr:
                    yield rowkey, col, None, None, rmap[col.split(':')[1]]
                else:
                    if len(arr) == 1:
                        pagekey = arr[0]
                        presult = self.client.get(self.pageName, pagekey, 'p:json', None)
                        if presult:
                            yield rowkey, col, presult[0].value, pagekey, rmap[col.split(':')[1]]
                        else:
                            yield rowkey, col, None, pagekey, rmap[col.split(':')[1]]
                    else:
                        dic_merged = {}
                        k_1 = None
                        for pkey in arr:
                            tmp = self.client.get(self.pageName, pkey, 'p:json', None)
                            if not tmp:
                                continue
                            if not dic_merged:
                                dic_merged = json.loads(tmp[0].value)
                                k_1 = dic_merged.keys()[0]
                            else:
                                dic_merged[k_1].extend(json.loads(tmp[0].value)[k_1])
                        yield rowkey, col, json.dumps(dic_merged), arr, rmap[col.split(':')[1]]


    def getrowkeys(self, prefix):

        def ftime(m):
            m = int(str(m)[0: -3])
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m))

        self.__open()
        rows = []
        id = self.client.scannerOpenWithPrefix(tableName=self.keysName, startAndPrefix=prefix, columns=[], attributes=None)
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
                rows.append((e.row, timestamp))
        return rows

    def delrowsprefix(self, prefix):
        rows = self.getrowkeys(prefix)
        self.__open()
        for rowkey, _ in rows:
            self.client.deleteAllRow(self.keysName, row=rowkey, attributes=None)












