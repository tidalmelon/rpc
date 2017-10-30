# -*- coding=utf-8 -*-

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

if __name__ == '__main__':
    url = 'https://zhuanlan.zhihu.com/p/20208594'
    print url
    url_1 = reverseUrl(url)
    print url_1
    url = unreverseUrl(url_1)
    print url



