# -*- coding=utf-8 -*-

import re
from urlparse import urlparse, urlsplit


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


class DomainExtractor():

    def __init__(self):
        self.topHostPostfix = [
            '.com','.la','.io',
            '.co', '.cn','.info',
            '.net', '.org','.me',
            '.mobi', '.us', '.biz',
            '.xxx', '.ca', '.co.jp',
            '.com.cn', '.net.cn', '.org.cn',
            '.mx','.tv', '.ws',
            '.ag', '.com.ag', '.net.ag',
            '.org.ag','.am','.asia',
            '.at', '.be', '.com.br',
            '.net.br',
            '.name',
            '.live',
            '.news',
            '.bz',
            '.tech',
            '.pub',
            '.wang',
            '.space',
            '.top',
            '.xin',
            '.social',
            '.date',
            '.site',
            '.red',
            '.studio',
            '.link',
            '.online',
            '.help',
            '.kr',
            '.club',
            '.com.bz',
            '.net.bz',
            '.cc',
            '.band',
            '.market',
            '.com.co',
            '.net.co',
            '.nom.co',
            '.lawyer',
            '.de',
            '.es',
            '.com.es',
            '.nom.es',
            '.org.es',
            '.eu',
            '.wiki',
            '.design',
            '.software',
            '.fm',
            '.fr',
            '.gs',
            '.in',
            '.co.in',
            '.firm.in',
            '.gen.in',
            '.ind.in',
            '.net.in',
            '.org.in',
            '.it',
            '.jobs',
            '.jp',
            '.ms',
            '.com.mx',
            '.nl','.nu','.co.nz','.net.nz',
            '.org.nz',
            '.se',
            '.tc',
            '.tk',
            '.tw',
            '.com.tw',
            '.idv.tw',
            '.org.tw',
            '.hk',
            '.co.uk',
            '.me.uk',
            '.org.uk',
            '.vg']

        self.extractPattern = r'[\.]('+'|'.join([h.replace('.',r'\.') for h in self.topHostPostfix])+')$'
        self.pattern = re.compile(self.extractPattern,re.IGNORECASE)
        self.level = "*"

    def parse_url(self,url):
        parts = urlparse(url)
        host = parts.netloc
        m = self.pattern.search(host)
        return m.group() if m else host

    def parse_url_level(self,url,level="*"):
        extractRule = self._parse_regex(level)
        parts = urlparse(url)
        host = parts.netloc
        pattern = re.compile(extractRule,re.IGNORECASE)
        m = pattern.search(host)
        self.level = level
        return m.group() if m else host

    def set_level(self,level):
        extractRule = self._parse_regex(level)
        self.extractPattern = extractRule
        self.pattern = re.compile(self.extractPattern,re.IGNORECASE)
        self.level = level

    def add_top_domain(self,top):
        if not top.startswith('.'):
            raise ValueError('top_domain must have . (.com|.com.cn|.net)')
        if top not in self.topHostPostfix:
            self.topHostPostfix.append(top)
            self._reset()
            return True
        else:
            return False

    def _reset(self):
        self.set_level(self.level)

    def _parse_regex(self,level):
        extractRule = r'(\w*\.?)%s('+'|'.join([h.replace('.',r'\.') for h in self.topHostPostfix])+')$'
        level = level if level == "*" else "{%s}"%level
        extractRule = extractRule%(level)
        return extractRule


FILTER = DomainExtractor()


def getDomain(url, level=1):
    """
    获取各级域名, 默认获取二级域名
    """
    return FILTER.parse_url_level(url, level=level)
    

############################
#测试区, 单元测试出国旅游了#
############################

def test_reverseurl_unreverseurl():
    url = 'http://www.tianyancha.com/company/2313776032'
    #url = 'http://www.11467.com/foshan/co/444200.htm'
    #url = 'http://007368.b2b.huangye88.com/product/'
    url_r = reverseUrl(url)
    print url_r
    uurl = unreverseUrl(url_r)
    print url
    print uurl


def test_DomainExtractor():
    url = 'http://007368.b2b.huangye88.com/product/'

    filter = DomainExtractor()
    print filter.level
    print filter.parse_url(url)
    print filter.parse_url_level(url, level=2)
    filter.set_level(1)
    print filter.parse_url_level(url, level=1)
    print filter.level


def test_getDoamin():
    url = 'http://007368.b2b.huangye88.com/product/'
    domain = getDomain(url)
    print domain


if __name__ == '__main__':
    test_reverseurl_unreverseurl()
    #test_DomainExtractor()
    #test_getDoamin()

