# coding=utf-8
from thread_test import GetBody
from lxml import etree
from urlparse import urljoin
import csv
csvfile = file('csv_dailianmeng.csv', 'wb')
writer = csv.writer(csvfile)

urls = set()


class DaiLianMeng(object):

    nos = 0

    gb = GetBody()

    start_urls = ["http://www.dailianmeng.com/p2pblacklist/index.html"]

    def start_requests(self):

        for url in self.start_urls:

            body = self.gb.getbody(False,None,url)

            tree = etree.HTML(body)

            next_page = tree.xpath('//li[@class="next"]/a/@href')

            if len(next_page) >0:

                urls.add(self.start_urls[0])

                self.start_urls = [urljoin(self.start_urls[0],next_page[0])]

            nodes = tree.xpath(u"//a[contains(text(),'查看详情')]/@href")

            for node in nodes:

                url = urljoin(self.start_urls[0],node)

                self.parse(url)

    def parse(self,url):

        body = self.gb.getbody(False, None, url)

        tree = etree.HTML(body)

        nodes = tree.xpath('//table[contains(@class,"detail-view")]/tr')

        if self.nos == 0:

            items = [item.encode("utf8") for item in tree.xpath('//table[contains(@class,"detail-view")]/tr/th/text()')]

            writer.writerow(items)

            del items

        self.nos+=1

        items = []

        for node in nodes:

            itemm = node.xpath('.//td/text()')

            item = "" if len(itemm)==0 else itemm[0].encode("utf8")

            items.append(item)

        writer.writerow(items)

        del items

        if len(self.start_urls)>0:

            if self.start_urls[0] not in urls:

                self.start_requests()

    def __exit__(self, exc_type, exc_val, exc_tb):

        csvfile.close()



if __name__ == "__main__":

    DaiLianMeng().start_requests()