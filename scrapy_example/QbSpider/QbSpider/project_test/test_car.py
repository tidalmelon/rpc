import cStringIO
import pycurl
from lxml import etree
from BeautifulSoup import BeautifulSoup


USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"

url = 'https://www.guazi.com/bj/buy/o2/'

def getbody(need_proxy,proxy,url):

    try:

        b = cStringIO.StringIO()

        c = pycurl.Curl()

        c.setopt(pycurl.URL, url)

        c.setopt(pycurl.USERAGENT, USER_AGENT)

        c.setopt(pycurl.WRITEFUNCTION, b.write)

        c.setopt(pycurl.SSL_VERIFYPEER, 0)

        c.setopt(pycurl.SSL_VERIFYHOST, 0)

        if need_proxy:

            c.setopt(pycurl.PROXY, proxy)

        else :

            pass

        c.perform()

        body = b.getvalue()

        return body

    except Exception,e:

        print e

        return None


def Parsebody(body):

    tree = etree.HTML(text=body)

    nodes = tree.xpath("//*[@class='list-infoBox']")

    for node in nodes:

        print node.xpath('.//a[1]/@title')[0]

        print node.xpath('.//*[@class="fc-org priType"]/text()')[0]
    #
    #     #print node.xpath('')

    # soup = BeautifulSoup(body)
    #
    # for node in soup.findAll('div',"list-infoBox"):
    #     print node.find('i','fc-org priType').string



if __name__ == "__main__":

    body = getbody(False,None,url)

    print Parsebody(body)




