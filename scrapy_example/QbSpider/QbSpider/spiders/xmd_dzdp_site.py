#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
"""
Date: 2017/05/10 09:15:20
"""

import os

import logging
import json
import re


from scrapy.http import Request
from scrapy.spiders import CrawlSpider


#import os
#import sys
#sys.path.append(os.path.abspath("../../"))
#from QbSpider.scrapy_redis.spiders import Spiders


logger = logging.getLogger(__name__)


class XMDDZDPSpider(CrawlSpider):

    name = 'xmddzdpseed'

    allowed_domains = ['dianping.com']

    start_urls = ['https://www.dianping.com/citylist/citylist?citypage=1']

    def __gettxt(self, e, x, r=None):
        if r:
            e_list = e.xpath(x).re(r)
        else:
            e_list = e.xpath(x).extract()
        e_list = [x.strip() for x in e_list]
        txt = ''.join(e_list)
        return txt

    
    def parse(self, response):
        #dt_list = response.xpath("//ul[@id='divArea']/li/*[@class='terms']//a")
        try:
            with open('seeds.txt', 'w') as f:
                dt_list = response.xpath("//ul[@id='divArea']/li/*[@class='terms']")
                for dt in dt_list:

                    pro = self.__gettxt(dt, "./dt/text()")
                    if not pro:
                        pro = ' '
                    
                    a_list = dt.xpath(".//a")
                    for a in a_list:
                        anchor = self.__gettxt(a, ".//text()")
                        if anchor == '更多':
                            continue
                        href = self.__gettxt(a, "./@href")
                        outlink = response.urljoin(href)
                        line = '%s\t%s\t%s' % (pro, anchor, outlink)
                        #f.write(line + os.linesep)
                        f.write(line + '\r\n')
        except Exception as e:
            logging.exception(e)
        

