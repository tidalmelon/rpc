# coding=utf-8
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
try:
    from urlparse import urljoin
except:
    from urllib.parse import urljoin
from scrapy.selector.lxmlsel import HtmlXPathSelector
import csv
csvfile = file('csv_guazi.csv', 'wb')
writer = csv.writer(csvfile)
writer.writerow(["url", "title", "nowprice", "oldprice", "drivetime", "city", "brand"])
reprs = ['\t','\n','\r'," ","   "]



class QianbSpider(CrawlSpider):

    name = "guazi"

    allowed_domains = ["guazi.com"]

    start_urls = ["https://www.guazi.com/www/buy/"]

    def parse(self, response):

        hxs = HtmlXPathSelector(response)

        all_city_name = hxs.xpath('//div[@class="all-city"]/descendant::a[contains(@data-gzlog,"select_city")]/text()').re(r'\S+')

        all_city_url = hxs.xpath('//div[@class="all-city"]/descendant::a[contains(@data-gzlog,"select_city")]/@href').extract()

        for item in zip(all_city_name,all_city_url):

            if len(item) ==2:

                yield Request(urljoin(self.start_urls[0],item[1]),callback=self.parse_list)

    def parse_list(self,response):

        hxs = HtmlXPathSelector(response)

        all_brand_name = hxs.xpath('//span[contains(@class,"brand-all")]/descendant::a/text()').re(r'\S+')

        all_brand_url = hxs.xpath('//span[contains(@class,"brand-all")]/descendant::a/@href').extract()

        for item in zip(all_brand_name,all_brand_url):

            if len(item) ==2:

                yield Request(urljoin(self.start_urls[0], item[1]), callback=self.parse_item,meta={'brand_name':item[0]})

    def parse_item(self, response):

        hxs = HtmlXPathSelector(response)

        meta = response.meta

        nodes = hxs.xpath("//div[@class='list-infoBox']")

        city = "".join(hxs.xpath('//a[@class="choose-city"]/span/text()').re(r'\S+'))

        for node in nodes:

            items_list = []

            title = "".join(node.xpath('.//a[1]/@title').extract())

            nowprice = "".join(node.xpath(".//i[@class='fc-org priType']/text()").extract())

            url = urljoin(self.start_urls[0],"".join(node.xpath('.//a[1]/@href').extract()))

            oldprice = "".join(node.xpath('.//p[@class="priType-s"]/s/text()').extract())

            drivetime = "".join(node.xpath('.//p[@class="fc-gray"]/descendant::text()').extract())

            items_list.append([url,title,nowprice,oldprice,drivetime,city,meta['brand_name']])

            writer.writerow([x.encode("utf8").replace("\n","").replace("\t","").replace("\r","").replace(" ","") for x in items_list[0]])

        next_page = hxs.xpath('//a[@class="next"]/@href').extract()

        if next_page:

            url = urljoin(self.start_urls[0],next_page[0])

            yield Request(url,callback=self.parse_item,meta=meta)








