# -*- coding: UTF-8 -*-
# api4.py
# 可以在if里边将获取到得post参数或者header参数进行数据库查询获取插入，然后返回给客户端
import urlparse

import json

from cgi import parse_qs, escape


def application(environ, start_response):
    print environ
    print start_response
    # start_response('200 OK', [('Content-Type', 'text/html')])
    #
    # # code
    # code = 200
    #
    # # get data
    #
    # url = 'http://%s?%s' % (environ['HTTP_HOST'], environ['QUERY_STRING'])
    #
    # query = urlparse.urlparse(url).query
    #
    # gets = dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])
    #
    # # post data size
    #
    # dataSize = environ['CONTENT_LENGTH']
    #
    # # 判断http body大小,如果post没有上传东西，进行判断
    # if (dataSize != '' or dataSize != None):
    #
    #     # header
    #
    #     username = environ['HTTP_USER_NAME']
    #
    #     password = environ['HTTP_PASS_WORD']
    #
    #     coding = environ['HTTP_CODING']
    #
    #     headers = {'username': username, 'password': password, 'coding': coding}
    #
    #     # 读取body内容
    #     request_body = environ['wsgi.input'].read(int(dataSize))
    #     # 将字符串内容转换为字典
    #     body = eval('%s' % parse_qs(request_body))
    #     # 格式化字典，用于转换成json数据
    #     posts = dict([(k, v[0]) for k, v in body.items()])
    #
    #     # 返回json
    #     result = {'data': {'gets': gets, 'headers': headers, 'posts': posts}, 'code': code}
    #
    #     return json.dumps(result)

    # else:
    #     result = {'data': {'gets': gets}, 'code': code}
    #
    #     return json.dumps(result)


        # 如果有body，就返回header，post，get，如果没有则返回get