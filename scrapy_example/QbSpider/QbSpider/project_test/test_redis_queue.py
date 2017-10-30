from QbSpider.scrapy_redis.queue import SpiderPriorityQueue
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
from QbSpider.spiders.redis_spider import DmozSpider
from scrapy.http import Request
con = rcu().get_redis()

if __name__ == "__main__":
    queuess = SpiderPriorityQueue(server=con, spider=DmozSpider(),
                                       key="dmozqueue")
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
    }

    queuess.push(Request(url="http://www.dmoz.org/",headers=headers))

    queuess.push(Request(url="http://www.dmoz.org/Recreation/Travel/Attractions/", headers=headers))

