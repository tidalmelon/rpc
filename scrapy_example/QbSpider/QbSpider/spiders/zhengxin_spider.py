# coding=utf-8
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from urlparse import urljoin
from scrapy.selector.lxmlsel import HtmlXPathSelector
import json
import re
import csv


class ZhengxinSpider(CrawlSpider):

    name = "zhengxin"

    allowed_domains = []

    nos = 0

    start_urls = []

    def start_requests(self):

        csvfile = file('csv_shixin.csv', 'wb')
        self.writer = csv.writer(csvfile)


        for x in xrange(101):

            url = "https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?resource_id=6899&query=%E5%85%A8%E5%9B%BD%E6%B3%95%E9%99%A2%E5%A4%B1%E4%BF%A1%E8%A2%AB%E6%89%A7%E8%A1%8C%E4%BA%BA%E5%90%8D%E5%8D%95&" + "pn=%s"%(x*10) + "&rn=10&ie=utf-8&oe=utf-8&format=json&t=1477373667446&cb=jQuery110204414144057265048_1477373405031&_=1477373405056"

            yield Request(url)

    def parse(self, response):

        body = re.findall(re.compile(r'jQuery\S+?\(([\S\s]+)\);',re.I),response.body)

        if len(body) > 0:

            j_read = json.loads(body[0])

            for user in j_read["data"][0]["result"]:

                if self.nos == 0:

                    self.writer.writerow(user.keys())

                else:

                    self.writer.writerow([v if type(v)==int else v.encode("utf8").replace("\n","").replace("\t","").replace("\r","").replace(" ","") for v in user.values()])

                self.nos += 1










