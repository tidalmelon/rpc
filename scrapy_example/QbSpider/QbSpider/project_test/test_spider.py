# from twisted.internet import reactor
# import scrapy
# from scrapy.crawler import CrawlerRunner
# from scrapy.utils.log import configure_logging
#
# class MySpider(scrapy.Spider):
#     # Your spider definition
#     ...
#
# configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
# runner = CrawlerRunner()
#
# d = runner.crawl(MySpider)
# d.addBoth(lambda _: reactor.stop())
# reactor.run()

if  __name__ == "__main__":

    a = {'Set-Cookie': ['_ntvKlgJ=""; Expires=Thu, 01-Jan-1970 00:00:10 GMT; Path=/', '_ntvKlgJ=""; Expires=Thu, 01-Jan-1970 00:00:10 GMT; Path=/', 'sc_t=1; Expires=Fri, 17-Nov-2017 03:43:35 GMT; Path=/; HttpOnly', 'mp=18519114597; Expires=Sat, 17-Dec-2016 03:43:35 GMT; Path=/; HttpOnly;', 'TrackID=1U6vVapJs-oI21lG_1w97YZpEhdq4WRO7SSLZ79IeUyHZUJMJpWkLOalIGlJTdk6WF8AaImLHqUDacnJqY4ccIg; Domain=.jd.com; Expires=Tue, 16-Nov-2021 03:43:35 GMT; Path=/;', 'pinId=78vIc6jygGwLecTKMSUXfg; Domain=.jd.com; Expires=Fri, 17-Nov-2017 03:43:35 GMT; Path=/;', 'pin=zqp821907280; Domain=.jd.com; Expires=Sat, 17-Dec-2016 03:43:35 GMT; Path=/;', 'unick=zqp821907280; Domain=.jd.com; Expires=Sat, 17-Dec-2016 03:43:35 GMT; Path=/; HttpOnly;', 'thor=5A0C9CFF5409198EBDC06570D67D4B2F1BAD130D5EBD61013666A6D02729B71FABEEE88D831FEE03F37594BC751475339A2B8E234364B24E8AD7C87504B2977054364806EBF30237527E84C6565087DB6CAA67B290C10917346272134B44265C41BF43A289A00331796EBA543891D4DDEF502BC57C56DD0DDF44E6FA8AC7420BBC98C65CF47D5B5E9690FD9F36FBA767; Domain=.jd.com; Expires=Fri, 17-Nov-2017 03:43:35 GMT; Path=/; HttpOnly;', 'ol=1; Path=/; HttpOnly;', '_tp=Atqr%2BFsLT3Ja7vKptizhFA%3D%3D; Domain=.jd.com; Expires=Sat, 17-Dec-2016 03:43:35 GMT; Path=/;', 'logining=1; Domain=.jd.com; Path=/;', '_pst=zqp821907280; Domain=.jd.com; Expires=Sat, 17-Dec-2016 03:43:35 GMT; Path=/; HttpOnly;', 'ceshi3.com=pXcTsUKTWWaiWpA9GXPaRcoiklKMvTwePWwBPPrseuQ; Domain=.jd.com; Path=/; HttpOnly;', 'qr_t=""; Expires=Thu, 01-Jan-1970 00:00:10 GMT; Path=/'], 'Expires': ['Thu, 17 Nov 2016 03:43:35 GMT'], 'Server': ['JengineD'], 'Pragma': ['no-cache'], 'Cache-Control': ['max-age=0'], 'Date': ['Thu, 17 Nov 2016 03:43:35 GMT'], 'P3P': ['CP="CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR"']}

    cookie = {}

    print ";".join([i.split(";")[0] for i in a['Set-Cookie']])

    for ii in [i.split(";")[0] for i in a['Set-Cookie']]:

        cookie.update({ii[:ii.index("=")]:ii[ii.index("=")+1:]})

    print cookie

    b = ["{'Accept-Language': ['en'], 'Accept-Encoding': ['gzip,deflate'], 'Accept': ['text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'], 'User-Agent': ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'], 'Referer': ['https://authcode.jd.com/verify/image?a=1&acid=5aaf9c70-83bb-4464-9234-7cd65b184d33&uid=5aaf9c70-83bb-4464-9234-7cd65b184d33&yys=1479354740241'], 'Cookie': ['_ntQIHLp=KMB6dQSbP8gB8XMglNeETnsw2W7WnXfIwI1hXS1Xb/Y=; qr_t=f; alc=HJH/jLHbMbojgspTx0uL/w==; _ntQIHLp=KMB6dQSbP8gB8XMglNeETnsw2W7WnXfIwI1hXS1Xb/Y='], 'Content-Type': ['application/x-www-form-urlencoded']}"]
