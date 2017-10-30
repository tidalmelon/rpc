#!/usr/bin/python
# -*-coding:utf-8-*-

import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class RotateUserAgentMiddleware(UserAgentMiddleware):
    """
        a useragent middleware which rotate the user agent when crawl websites

        if you set the USER_AGENT_LIST in settings,the rotate with it,if not,then use the default user_agent_list attribute instead.
    """

    # the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape
    # for more user agent strings,you can find it in http://www.useragentstring.com/pages/useragentstring.php
    user_agent_list = [ \
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1)', \
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; 360SE)', \
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; 360SE)', \
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727)', \
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; .NET CLR 1.1.4322)', \
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 2.0.50727; 360SE)', \
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; SE 2.X MetaSr 1.0)', \
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; 5i5jBrowser 2.0)', \
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; SV1; BTRS122063; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C; .NET4.0E)', \
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)', \
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; QQPinyin 730; 51Logon.com)', \
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0', \
        ]

    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def _user_agent(self, spider):
        if hasattr(spider, 'user_agent'):
            return spider.user_agent
        elif self.user_agent:
            return self.user_agent
        return random.choice(self.user_agent_list)

    def process_request(self, request, spider):
        ua = self._user_agent(spider)
        if ua:
            request.headers.setdefault('User-Agent', ua)
