# coding=utf-8
"""
Depth Spider Middleware

See documentation in docs/topics/spider-middleware.rst
"""
#!/usr/bin/python
# -*-coding:utf-8-*-
import os,sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.abspath("../../"))
"""
HttpError Spider Middleware

See documentation in docs/topics/spider-middleware.rst
"""

from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from scrapy.xlib.tx import ResponseFailed
from scrapy.exceptions import IgnoreRequest
from scrapy.core.downloader.handlers.http11 import TunnelError
import logging
from thrift.transport.TTransport import TTransportException
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
from scrapy.exceptions import IgnoreRequest

logger = logging.getLogger(__name__)


class HttpError(IgnoreRequest):
    """A non-200 response was filtered"""

    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(HttpError, self).__init__(*args, **kwargs)


class HttpErrorMiddleware(object):
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError, HttpError, TTransportException,Exception)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.handle_httpstatus_all = settings.getbool('HTTPERROR_ALLOW_ALL')
        self.handle_httpstatus_list = settings.getlist('HTTPERROR_ALLOWED_CODES')

    def process_spider_input(self, response, spider):
        if 200 <= response.status < 300:
            spider.ti = 1# common case
            return
        meta = response.meta
        if 'handle_httpstatus_all' in meta:
            spider.ti = 1
            return
        if 'handle_httpstatus_list' in meta:
            allowed_statuses = meta['handle_httpstatus_list']
        elif self.handle_httpstatus_all:
            spider.ti = 1
            return
        else:
            allowed_statuses = getattr(spider, 'handle_httpstatus_list', self.handle_httpstatus_list)
        if response.status in allowed_statuses:
            spider.ti = 1
            return
        raise HttpError(response, 'Ignoring non-200 response')

    def process_spider_exception(self, response, exception, spider):
        if not isinstance(exception,self.EXCEPTIONS_TO_RETRY):
            spider.ti = 1
        else:
            spider.ti = 0
            #spider.metas["code"] = 1999
            #rcu().get_redis().hmset(spider.jobid,dict(spider.metas))
            spider.userinfo["code"] = 1999
            rcu().get_redis().hmset(spider.jobid,dict(spider.userinfo))
            logger.error(msg="账号<%s>,爬去出现问题" % spider.username)
        if isinstance(exception, HttpError):
            logger.info(
                "Ignoring response %(response)r: HTTP status code is not handled or not allowed",
                {'response': response}, extra={'spider': spider},
            )
            return []
