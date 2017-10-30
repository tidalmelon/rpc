#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
"""
Date: 2017/05/04 11:17:17
"""

import os
import logging
import json
import re
import datetime


from scrapy.http import Request
#from scrapy.spiders import CrawlSpider
from QbSpider.scrapy_redis.spiders import Spiders
from scrapy import signals
from scrapy.exceptions import DontCloseSpider


import sys
sys.path.append(os.path.abspath("../../"))
from QbSpider.utils.hbcommon import HBClient


logger = logging.getLogger(__name__)


#class XMDDZDPSpider(CrawlSpider):
class XMDDZDPSpider(Spiders):

    name = 'xmddzdp'

    allowed_domains = ['dianping.com']

    redis_key = "QUEUE_XMD_DZDP"

    #custom_settings = {
    #    'USELOCALIP': 1
    #}

    #start_urls = ['https://www.dianping.com/search/keyword/2/0_%E5%BA%B7%E4%BA%8C%E5%A7%90%E4%B8%B2%E4%B8%B2']
    #start_urls = ['https://www.dianping.com/search/keyword/2/0_%E8%82%AF%E5%BE%B7%E5%9F%BA']
    #start_urls = ['https://www.baidu.com/']
    start_urlss = ['https://www.baidu.com']

    tb = HBClient()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(XMDDZDPSpider, cls).from_crawler(crawler,
                                                       *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def __init__(self, *a, **kw):
        # 这个要从配置文件读取
        DAY_FETCH_COMMENT = 180
        now = datetime.date.today()
        end = now - datetime.timedelta(days=DAY_FETCH_COMMENT)
        # 这个日期要每次都变
        self.DATE_COM_TERMINAL = end.strftime('%Y-%m-%d')

    def __gettxt(self, e, x, r=None):
        if r:
            e_list = e.xpath(x).re(r)
        else:
            e_list = e.xpath(x).extract()
        e_list = [x.strip() for x in e_list]
        txt = ''.join(e_list)
        return txt

    def parse(self, response):
        try:
            self.userinfo = response.meta.get('metass', '')
            logging.debug(msg='userinfo: %s' % self.userinfo)

            if 'shopId' in self.userinfo:
                shopid = self.userinfo.get('shopId', '')
                outlink = 'https://www.dianping.com/shop/%s' % shopid
                print outlink
                yield Request(outlink, callback=self.parse_detail, meta={'shopid': shopid})
            elif 'shopname' in self.userinfo and 'cityid' in self.userinfo:
                # 未测试
                # 可以缩小范围
                shopname = self.userinfo.get('shopname', '')
                cityid = self.userinfo.get('cityid', '')
                outlink = 'https://www.dianping.com/search/keyword/%s/0_%s' % (cityid, shopname)
                yield Request(outlink, callback=self.parse_listl)

        except Exception as e:
            logging.exception(e)
    
    def parse_list(self, response):

        def getpromo(e_li):
            a_promo_list = e_li.xpath("./div[@class='txt']/div[@class='tit']/div[@class='promo-icon']/a")
            dic_promo = {}
            for a_p in a_promo_list:
                promo = self.__gettxt(a_p, './@class')
                promo_url = self.__gettxt(a_p, './@href')
                if promo_url:
                    promo_url = response.urljoin(promo_url)
                dic_promo[promo] = promo_url
            if dic_promo:
                return dic_promo
            return ''

        x_li = "//div[@id='shop-all-list']/ul/li"
        list_li = response.xpath(x_li)

        records = []

        for e_li in list_li:
            anchorinfo = {}
            href = self.__gettxt(e_li, "./div[@class='txt']/div[@class='tit']/a[1]/@href")
            if not href:
                continue
            outlink = response.urljoin(href)
            # 外链
            anchorinfo['outlink'] = outlink
            # 锚点信息
            anchor = self.__gettxt(e_li, "./div[@class='txt']/div[@class='tit']/a[1]//text()")
            anchorinfo['anchor'] = anchor
            # 所有优惠， 1, 目前仅发现团购与外卖 2 这里的数据要抓取 , 从hbase回捞抓取？
            dic_promo = getpromo(e_li)
            anchorinfo['promo'] = dic_promo
            # 是否营业
            istoptrade = self.__gettxt(e_li, "./div[@class='txt']/div[@class='tit']/span[@class='istopTrade']/text()", '\((.*?)\)')
            anchorinfo['istoptrade'] = istoptrade
            # 分店url
            # 是否抓取全部分店信息
            # 详情页也有, 在详情页抓取吧
            branch_url = self.__gettxt(e_li, "./div[@class='txt']/div[@class='tit']/a[@class='shop-branch']/@href")
            if branch_url:
                branch_url = response.urljoin(branch_url)
            anchorinfo['branchurl'] = branch_url
            # 星级
            star = self.__gettxt(e_li, "./div[@class='txt']/div[@class='comment']/span/@class", '(\d+)')
            anchorinfo['star'] = star
            # 评论数
            num_comments = self.__gettxt(e_li, "./div[@class='txt']/div[@class='comment']/a[@class='review-num']/b/text()")
            anchorinfo['numcomments'] = num_comments
            # 均价
            mean_price = self.__gettxt(e_li, "./div[@class='txt']/div[@class='comment']/a[@class='mean-price']/b/text()", '(\d+)')
            anchorinfo['meanprice'] = mean_price
            # 分类
            tag_cate = self.__gettxt(e_li, "./div[@class='txt']/div[@class='tag-addr']/a[1]//text()")
            anchorinfo['cate'] = tag_cate
            # 分类url
            tag_cate_url = self.__gettxt(e_li, "./div[@class='txt']/div[@class='tag-addr']/a[1]/@href")
            if tag_cate_url:
                tag_cate_url = response.urljoin(tag_cate_url)
            anchorinfo['cateurl'] = tag_cate_url
            # 地区
            tag_region = self.__gettxt(e_li, "./div[@class='txt']/div[@class='tag-addr']/a[2]//text()")
            anchorinfo['region'] = tag_region
            # 地区url
            tag_region_url = self.__gettxt(e_li, "./div[@class='txt']/div[@class='tag-addr']/a[2]/@href")
            if tag_region_url:
                tag_region_url = response.urljoin(tag_region_url)
            anchorinfo['regionurl'] = tag_region_url
            # 地址
            addr = self.__gettxt(e_li, "./div[@class='txt']/div[@class='tag-addr']/span[@class='addr']//text()")
            anchorinfo['addr'] = addr

            records.append((outlink, anchorinfo))

        for outlink, anchor in records:
            logging.debug(msg='extract outlink: %s' % outlink)
            logging.debug(msg='anchor: %s' % json.dumps(anchor))
            yield Request(outlink, callback=self.parse_detail, meta={'anchor': anchor})
            # 测试

    def parse_detail(self, response):

        def getscore(input, pat=re.compile(u'\|口味：([0-9\.]*)\|环境：([0-9\.]*)\|服务：([0-9\.]*)')):
            m = pat.search(input)
            if m:
                return m.group(1), m.group(2), m.group(3)
            return '', '', ''

        def getbranch(div_branch):
            dic = {}
            if not div_branch:
                return dic

            # 分店列表地址
            branch_url = self.__gettxt(div_branch, "//div[@id='shop-branchs']/a[@class='more-shop']/@href")
            if branch_url:
                branch_url = response.urljoin(branch_url)
            dic['branchurl'] = branch_url

            # 分店总数量
            branch_num = self.__gettxt(div_branch, "//div[@id='shop-branchs']/a[@class='more-shop']/text()", '(\d+)')
            dic['branchnum'] = branch_num

            div_list = div_branch.xpath('./div')
            branchlist = []
            for div in div_list:
                subdic = {}
                name = self.__gettxt(div, "./h3/a/text()")
                subdic['name'] = name
                href = self.__gettxt(div, "./h3/a/@href")
                if href:
                    href = response.urljoin(href)
                subdic['url'] = href
                addr = self.__gettxt(div, "./p/text()")
                subdic['addr'] = addr
                star = self.__gettxt(div, "./p/span/@class", '(\d+)')
                subdic['star'] = star
                branchlist.append(subdic)
            dic['branches'] = branchlist
            return dic

        def getshopconfig(txt, pat=re.compile("<script>[\S\s]+?window\.shop_config=([\s\S]*?)</script>"), pat_1=re.compile("(\w+?):\{(\w+?:.*?,\w+:.*?)\}")):
            try:
                m = pat.search(txt)
                if not m:
                    return None
                shop = m.group(1)
                shop = re.sub('\s+', '', shop)
                shop = shop.strip('{}')

                dic = {}

                # 移除一级二级键
                m_1 = pat_1.search(shop)
                if m_1:
                    old = m_1.group(0) + ','
                    shop = shop.replace(old, '')
                    key = m_1.group(1)
                    dic[key] = {}
                    k_2_arr = [e.split(':') for e in m_1.group(2).split(',')]
                    for k, v in k_2_arr:
                        dic[key][k] = eval(v)

                k_1_arr = [e.split(':', 1) for e in shop.split(',')]
                for k, v in k_1_arr:
                    dic[k] = eval(v)

                a_dic = {}
                for key, val in dic.items():
                    key1 = 'c_' + key.lower()
                    a_dic[key1] = val


                return a_dic
            except Exception as e:
                logging.exception(e)

        def getpromo(e_li):
            a_promo_list = e_li.xpath("//div[@class='promosearch-wrapper']//a")
            dic_promo = {}
            for a_p in a_promo_list:
                promo = self.__gettxt(a_p, './@class')
                promo_url = self.__gettxt(a_p, './@href')
                if promo_url:
                    promo_url = response.urljoin(promo_url)
                dic_promo[promo] = promo_url
            if dic_promo:
                return dic_promo
            return ''

        shopid = response.meta.get('shopid', '')
        dic_json = {}
        dic_json['currurl'] = response.url

        # 类别信息
        cates = self.__gettxt(response, "//div[@class='breadcrumb']//text()")
        dic_json['cates'] = cates
        #logging.debug(msg='cates: %s' % cates)

        # 店名
        shopname = self.__gettxt(response, "//h1[@class='shop-name']/text()")
        dic_json['shopname'] = shopname
        #logging.info(msg='shopname: %s' % shopname)

        # 是否表V
        vshop = self.__gettxt(response, "//h1[@class='shop-name']/a[@class='icon v-shop']/@title")
        dic_json['vshop'] = vshop
        #logging.info(msg='vshop: %s' % vshop)

        # 分店数量
        numbranch = self.__gettxt(response, "//h1[@class='shop-name']/a[@class='branch J-branch']/text()", '(\d+)')
        dic_json['numbranch'] = numbranch
        #logging.info(msg='numbranch: %s' % numbranch)

        # 星级
        star = self.__gettxt(response, "//div[@class='brief-info']/span[1]/@class", '(\d+)')
        dic_json['star'] = star
        #logging.info(msg='star: %s' % star)

        # 评论数
        numcomments = self.__gettxt(response, "//div[@class='brief-info']/span[@id='reviewCount']/text()", '(\d+)')
        dic_json['numcomments'] = numcomments
        #logging.info(msg='numcomments: %s' % numcomments)

        # 平均价格
        meanprice = self.__gettxt(response, "//div[@class='brief-info']/span[@id='avgPriceTitle']/text()", '(\d+)')
        dic_json['meanprice'] = meanprice
        #logging.info(msg='meanprice: %s' % meanprice)

        # 口味 环境 服务
        commentscore = self.__gettxt(response, "//div[@class='brief-info']/span[@id='comment_score']//text()")
        #logging.info(msg='commentscore: %s' % commentscore)
        taste, env, service = getscore(commentscore)
        dic_json['taste'] = taste 
        dic_json['env'] = env 
        dic_json['service'] = service
        #logging.info('taste: %s env: %s service: %s' % (taste, env, service))

        # 地址
        addr = self.__gettxt(response, "//div[@class='expand-info address']/span[@itemprop='street-address']//text()")
        dic_json['addr'] = addr
        logging.info(msg='address: %s' % addr)

        # 电话: 可能是两个， 在houtai中会给出
        tel = self.__gettxt(response, "//span[@itemprop='tel']/text()")
        dic_json['tel'] = tel
        #logging.info(msg='tel: %s' % tel)

        # 优惠信息:见parse_promo
        #promo = getpromo(response)
        #logging.info(msg='promo: %s' % promo)

        # 别名(不需要吧) 
        # 营业时间 
        # 停车信息(在评论里抓取)
        # 简介

        # 汇总
        shopinfo = self.__gettxt(response, "//p[@class='info info-indent']//text()")
        dic_json['shopinfosum'] = shopinfo
        #logging.info(msg='shophour: %s' % shopinfo)

        # 营业时间-hour
        busihour = self.__gettxt(response, u"//p[@class='info info-indent']/span[text()='营业时间：']/following::span[1]/text()")
        dic_json['busihour'] = busihour
        #logging.info(msg='busihour: %s' % busihour)

        # 别名1
        alias = self.__gettxt(response, u"//p[@class='info info-indent']/span[starts-with(text(),'别')]/following::span[1]/text()")
        dic_json['alias'] = alias
        #logging.info(msg='alias: %s' % alias)

        # 简介
        intro = self.__gettxt(response, u"//p[@class='info info-indent']/span[text()='餐厅简介：']/../text()")
        dic_json['intro'] = intro
        #logging.info(msg='intro: %s' % intro)

        #branch 非全部(获取发起请求)
        # 暂时体统部分
        div_branch = response.xpath("//div[@id='shop-branchs']")
        branch = getbranch(div_branch)
        dic_json['branches'] = branch
        #logging.debug(msg='branches: %s' % json.dumps(branch))

        # 是否营业
        dic_json['istoptrade'] = self.__gettxt(response, "//p[@class='shop-closed']/text()")

        # 图片数量
        piccount = self.__gettxt(response, "//*[@id='pic-count']/text()")
        dic_json['piccount'] = piccount
        #logging.info(msg='piccount: %s' % piccount)

        # 隐藏字段, 如何使用这个字段（给不出实际意义)
        dic_base = getshopconfig(response.body)
        #for ck, cv in dic_base.items():
        #    dic_json[ck] = cv
        dic_json['basic'] = dic_base
        #logging.debug(msg='shop config: %s' % json.dumps(dic_base))

        #shopId = dic_base.get('c_shopid', '')
        shopId = shopid
        logging.info('shopid %s' % shopId)

        # 抓取评论
        url_comment = 'https://www.dianping.com/shop/%s/review_more_latest' % shopId
        # 暂时用这个shopId
        yield Request(url_comment, callback=self.parse_comments, meta={'shopid': shopId})

        power = dic_base.get('c_power', '')
        cityId = dic_base.get('c_cityid', '')
        shopType = dic_base.get('c_shoptype', '')

        print power, cityId, shopType

        outlinks = []
        # ajax 优惠信息
        if shopId and power and cityId and shopType:
            url_promo = 'https://www.dianping.com/ajax/json/shopDynamic/searchPromo?shopId=%s&power=%s&cityId=%s&shopType=%s' % (shopId, power, cityId, shopType)

            outlinks.append(url_promo)
            yield Request(url_promo, callback=self.parse_promo)

        shopName = dic_base.get('c_shopname', '')
        mainCategoryId = dic_base.get('c_maincategoryid', '')
        shopCityId = dic_base.get('c_shopcityid', '')

        #if shopId and power and cityId and shopType and shopName and mainCategoryId and shopCityId:
        #    url_dish = 'https://www.dianping.com/ajax/json/shopDynamic/shopTabs?shopId=%s&cityId=%s&shopName=%s&power=%s&mainCategoryId=%s&shopType=%s&shopCityId=%s' % (shopId, cityId, shopName, power, mainCategoryId, shopType,shopCityId)
        #    outlinks.append(url_dish)
        #    yield Request(url_dish, callback=self.parse_pic)

        if shopId:
            url_houtai = 'https://www.dianping.com/ajax/json/shopfood/wizard/BasicHideInfoAjaxFP?_nr_force=1494238106490&shopId=%s' % shopId
            outlinks.append(url_houtai)
            yield Request(url_houtai, callback=self.parse_basic)

        try:
            anchor = response.meta.get('anchor', '')
            if anchor:
                dic_json['_anchor'] = anchor

            ol = None
            if outlinks:
                ol = '|'.join(outlinks)

            self.tb.insertdetail(response.url, anchor, response.body, struct_dic=dic_json, outlinks=ol)
            logging.debug(msg='insert detail success %s' % response.url)
        except Exception as e:
            logging.exception(e)
    

    def parse_promo(self, response):
        dic_promo = json.loads(response.body)
        try:
            dic = {}
            for key, val in dic_promo.items():
                key1 = 'p_' + key.lower()                
                dic[key1] = val

            self.tb.insertdetail(response.url, None, response.body, struct_dic=dic)
            logging.debug(msg='insert promo success %s' % response.url)
        except Exception as e:
            logging.exception(e)


        # 这个整个入库即可
        #logging.debug(msg='promo: %s' % json.dumps(dic_promo))

    def parse_pic(self, response):

        try:
            j_read = json.loads(response.body)

            allpic = {}

            # 官方相册
            officialalbumList = j_read.get('officialAlbumList', '')
            albumllist = []
            if officialalbumList:
                for pic in officialalbumList:
                    dic = {}
                    dic['id'] = pic.get('id', '')
                    dic['shopid'] = pic.get('shopId', '')
                    dic['name'] = pic.get('name', '')
                    dic['albumtype'] = pic.get('albumType', '')
                    dic['picpath'] = pic.get('picPath', '')
                    dic['piccount'] = pic.get('picCount', '')
                    dic['addtime'] = pic.get('addTime', '')
                    dic['updatetime'] = pic.get('updateTime', '')
                    albumllist.append(dic)
            #officialalbumList = {'officialalbumlist': albumllist}
            #print 'res: album album album %s' % json.dumps(officialalbumList)
            allpic['officialalbumlist'] = albumllist

            # 环境
            envpics = j_read.get('picsShopPic', '')
            envinfos = []
            if envpics:
                for envpic in envpics:
                    envinfo = {}
                    envinfo['picid'] = envpic.get('picId', '')
                    envinfo['userid'] = envpic.get('userId', '')
                    envinfo['shopid'] = envpic.get('shopId', '')
                    envinfo['hits'] = envpic.get('hits', '')
                    envinfo['addtime'] = envpic.get('addTime', '')
                    envinfo['lasttime'] = envpic.get('lastTime', '')
                    envinfo['lastip'] = envpic.get('lastIp', '')
                    envinfo['cityid'] = envpic.get('cityId', '')
                    envinfo['shoptype'] = envpic.get('shopType', '')
                    envinfo['shopgroupid'] = envpic.get('shopGroupId', '')
                    envinfo['pictype'] = envpic.get('picType', '')
                    envinfo['clienttype'] = envpic.get('clientType', '')
                    envinfo['url'] = envpic.get('url', '')
                    envinfo['status'] = envpic.get('status', '')
                    envinfo['statuscode'] = envpic.get('statusCode', '')
                    envinfo['clienttypename'] = envpic.get('clientTypeName', '')
                    envinfo['bigpicture'] = envpic.get('bigPicture', '')
                    envinfo['middlepicture'] = envpic.get('middlePicture', '')
                    envinfo['smallpicture'] = envpic.get('smallPicture', '')

                    envinfos.append(envinfo)
            #env = {'envinfo': envinfos}
            #print 'res: env env env env %s' % json.dumps(env)
            allpic['env'] = envinfos

            # 价目表
            picpricelist = j_read.get('picsPriceList', '')
            pricelist = []
            if picpricelist:
                for pic in picpricelist:
                    picinfo = {}
                    picinfo['picid'] = pic.get('picId', '')
                    picinfo['userid'] = pic.get('userId', '')
                    picinfo['shopid'] = pic.get('shopId', '')
                    picinfo['hits'] = pic.get('hits', '')
                    picinfo['addtime'] = pic.get('addTime', '')
                    picinfo['lasttime'] = pic.get('lastTime', '')
                    picinfo['lastip'] = pic.get('lastIp', '')
                    picinfo['cityid'] = pic.get('cityId', '')
                    picinfo['shoptype'] = pic.get('shopType', '')
                    picinfo['shopgroupid'] = pic.get('shopGroupId', '')
                    picinfo['pictype'] = pic.get('picType', '')
                    picinfo['clienttype'] = pic.get('clientType', '')
                    picinfo['url'] = pic.get('url', '')
                    picinfo['status'] = pic.get('status', '')
                    picinfo['statuscode'] = pic.get('statusCode', '')
                    picinfo['clienttypename'] = pic.get('clientTypeName', '')
                    picinfo['bigpicture'] = pic.get('bigPicture', '')
                    picinfo['middlepicture'] = pic.get('middlePicture', '')
                    picinfo['smallpicture'] = pic.get('smallPicture', '')

                    pricelist.append(picinfo)
            #picpricelist = {'picpricelist': pricelist}
            #print 'res: price price price %s' % json.dumps(picpricelist)
            allpic['pricelist'] = pricelist
            
            # 品牌故事
            shopbrand = j_read.get('poiShopBrand', '')
            brandinfo = {}
            if shopbrand:
                brandinfo['shopid'] = shopbrand.get('shopId', '')
                brandinfo['brandid'] = shopbrand.get('brandId', '')
                brandinfo['story'] = shopbrand.get('story', '')
                brandinfo['auditstatus'] = shopbrand.get('auditStatus', '')
                brandinfo['adduser'] = shopbrand.get('addUser', '')
                brandinfo['updateuser'] = shopbrand.get('updateUser', '')
                brandinfo['addtime'] = shopbrand.get('addTime', '')
                brandinfo['updatetime'] = shopbrand.get('updateTime', '')
                # 先使用这个吧
                brandinfo['brandpic1'] = shopbrand.get('brandPic1', '')

            #print 'res: brand brand brand %s' % json.dumps(brandinfo)
            allpic['brand'] = brandinfo

            # 推荐菜
            alldishes = j_read.get('allDishes', '')
            dishlist = []
            if alldishes:
                for dish in alldishes:
                    dic = {}
                    dic['menuid'] = dish.get('menuId', '')
                    dic['shopid'] = dish.get('shopId', '')
                    dic['tagname'] = dish.get('dishTagName', '')
                    dic['tagcount'] = dish.get('tagCount', '')
                    dic['finalprice'] = dish.get('finalPrice', '')
                    dic['officialprice'] = dish.get('officialPrice', '')
                    dic['addtime'] = dish.get('addTime', '')
                    dic['lasttime'] = dish.get('lastTime', '')
                    dic['defaultpicurl'] = dish.get('defaultPicURL', '')
                    dishlist.append(dic)

            #res = {'dishlist': dishlist}
            #print 'res: dish dish dish %s' % json.dumps(res)
            allpic['dishlist'] = dishlist
            #logging.debug(msg='allpic: %s' % json.dumps(allpic))

            try:
                self.tb.insertdetail(response.url, None, response.body, struct_dic=allpic)
                logging.debug(msg='insert allpic success %s' % response.url)
            except Exception as e:
                logging.exception(e)


        except Exception as e:
            logging.exception(e)


    def parse_basic(self, response):
        try:
            j_read = json.loads(response.body)

            shopinfo = j_read.get('msg', '').get('shopInfo', '')
            # 字段全部保留
            if shopinfo:
                info = {}
                for key in shopinfo.keys():
                    key1 = 'b_' + key.lower()
                    info[key1] = shopinfo[key]

                #logging.debug(msg='shop basic param %s' % json.dumps(info))

                if not info:
                    return
                try:
                    self.tb.insertdetail(response.url, None, response.body, struct_dic=info)
                    logging.debug(msg='insert shopinfo success %s' % response.url)
                except Exception as e:
                    logging.exception(e)

        except Exception as e:
            logging.exception(e)


    def parse_comments(self, response):

        def getstarnum(response):
            span_list = response.xpath("//div[@class='comment-star']/dl/dd/span")
            dic = {}
            for span in span_list:
                name = self.__gettxt(span, "./a//text()")
                num  = self.__gettxt(span, "./em//text()", '(\d+)')
                dic[name] = num
            return dic

        def getcommentrst(li, pat=re.compile("味(\d+)\(.*?\)环境(\d+)\(.*?\)服务(\d+)\(.*?\)")):
            comment_rst = self.__gettxt(li, "./div[@class='content']/div[@class='user-info']/div[@class='comment-rst']//text()")
            m = pat.search(comment_rst)
            if m:
                return m.group(1), m.group(2), m.group(3)
            return '', '', ''

        def getcomcom(li, pat=re.compile('(.*?)(\d+)'), chi={u'赞': 'r_zan', u'回应': 'r_huiying', u'不当内容': 'r_budangneirong', u'收藏': 'r_shoucang'}):
            # 评论的评价
            comcom = self.__gettxt(li, "./div[@class='content']/div[@class='misc-info']/span[@class='col-right']//text()")
            logging.debug(msg='comcom: %s' % comcom)
            arr = comcom.split('|')
            dic = {}
            for e in arr:
                e = e.replace('(', '').replace(')', '')
                m = pat.search(e)
                if m:
                    key = m.group(1)
                    val = m.group(2)
                    dic[key] = val
                else:
                    dic[e] = ''
            res = {}
            for k, v in dic.items():
                k1 = chi.get(k, '')
                if k1:
                    res[k1] = v
                else:
                    res[k] = v
            return res

        def gettime(li, pat=re.compile("\d+-\d+(-\d+)?")):
            year = str(datetime.datetime.now().year)
            line = self.__gettxt(li, "./div[@class='content']/div[@class='misc-info']/span[@class='time']/text()")
            m = pat.search(line)
            if m:
                dt = m.group(0)
                num = dt.count('-')
                if num == 1:
                    dt = year + '-' + dt
                elif num == 2:
                    dt = '20' + dt
                return dt
            return ''

        try:

            meta = response.meta
            shopid = meta.get('shopid', '')
            # 这里需要有异常处理
            allll = {}

            # 先处理main
            starnum = getstarnum(response)
            allll['starnum'] = starnum

            ########
            # 公共信息（做冗余处理)
            #######
            # 带车位评论
            numtrans = self.__gettxt(response, "//label[@for='cbTrans']", '(\d+)')
            #logging.debug(msg='numtrans: %s' % numtrans)
            allll['transnum'] = numtrans

            # 带图片评论
            numpic = self.__gettxt(response, "//label[@for='cbPic']", '(\d+)')
            allll['picnum'] = numpic
            #logging.debug(msg='numpic: %s' % numpic)

            comlist = []
            li_list = response.xpath("//div[@class='comment-list']/ul/li")
            is_terminal = False
            for li in li_list:
                comdic = {}
                ##########
                # 用户信息
                ##########
                # id
                userid = self.__gettxt(li, "./div[@class='pic']/a[@class='J_card']/@user-id")
                #logging.debug(msg='userid: %s' % userid)
                comdic['userid'] = userid

                # url
                userurl = self.__gettxt(li, "./div[@class='pic']/a[@class='J_card']/@href")
                if userurl:
                    userurl = response.urljoin(userurl)
                #logging.debug(msg='userurl: %s' % userurl)
                comdic['userurl'] = userurl

                # 头像
                userimg = self.__gettxt(li, "./div[@class='pic']/a[@class='J_card']/img/@src")
                comdic['userimg'] = userimg
                #logging.debug(msg='userimg: %s' % userimg)

                # iconVIP
                iconvip = self.__gettxt(li, "./div[@class='pic']//i/@class")
                comdic['uservip'] = iconvip
                #logging.debug(msg='iconvip: %s' % iconvip)

                # 用户名
                username = self.__gettxt(li, "./div[@class='pic']/p[@class='name']/a/text()")
                comdic['username'] = username
                #logging.debug(msg='username: %s' % username)

                # 用户星级及贡献值
                rank = self.__gettxt(li, "./div[@class='pic']/p[@class='contribution']/span/@class", '(\d+)')
                comdic['userrank'] = rank
                #logging.debug(msg='rank: %s' % rank)

                # 这个直接用用户星级即可，二者意义一致
                #contribution = self.__gettxt(li, "./div[@class='pic']/p[@class='contribution']/span/@title")
                #logging.debug(msg='contribution: %s' % contribution)
                # 标准化

                ##########
                # 评论内容
                ##########
                # 用户评论星级
                ustar = self.__gettxt(li, "./div[@class='content']/div[@class='user-info']/span[1]/@class", '(\d+)')
                #logging.debug(msg='ustar: %s' % ustar)
                comdic['cstar'] = ustar

                # 均价
                mean_price = self.__gettxt(li, "./div[@class='content']/div[@class='user-info']/span[@class='comm-per']/text()", '(\d+)')
                comdic['cmeanprice'] = mean_price
                #logging.debug(msg='mean price: %s' % mean_price)

                # 口味，环境 服务
                tatse, env, service = getcommentrst(li)
                comdic['ctaste'] =  tatse
                comdic['cenv'] = env 
                comdic['cservice'] = service
                #logging.debug(msg='tatse:%s env:%s service:%s' % (tatse, env, service))

                # 评论正文
                comment_txt = self.__gettxt(li, "./div[@class='content']/div[@class='comment-txt']//text()")
                #logging.debug(msg='comment txt: %s' % comment_txt)
                comdic['ccnt'] = comment_txt

                # 时间
                dt = gettime(li)
                #logging.debug(msg='time: %s' % dt)
                comdic['ctime'] = dt

                # 评论的评价
                diccom = getcomcom(li)
                #logging.debug(msg='comcom: %s' % json.dumps(diccom))
                #comdic['creply'] = diccom
                for k, v in diccom.items():
                    comdic[k] = v


                # 如果达到阈值，则停止
                # 目前假设严格按照时间排序, 80%
                if dt < self.DATE_COM_TERMINAL:
                    logging.info(msg='fetch comments terminal: %s' % dt)
                    is_terminal = True
                    break

                comlist.append(comdic)

                try:
                    code = self.tb.insertcom(id=shopid, tm=dt, uname=userid, cnt=comment_txt, struct_dic=comdic)
                    if code == 1:
                        logging.debug(msg='insert success')
                    elif code == 2:
                        logging.debug(msg='repeated comment, fetch comments terminal: %s' % dt)
                        is_terminal = True
                        break

                except Exception as e:
                    logging.exception(e)

            allll['comlist'] = comlist

            #logging.debug(msg='comment info: %s' % json.dumps(allll))

            # 评论的存储
            # 严重依赖 日期的抽取。

            # 评论的翻页
            # 如果没有终止，则继续抓
            if not is_terminal:
                nexthref = self.__gettxt(response, "//a[@class='NextPage']/@href")
                nexturl = response.urljoin(nexthref)
                yield Request(nexturl, callback=self.parse_comments, meta={'shopid': shopid})
            else:
                logging.info(msg='fetch comments terminal, donot fetch next page')

        except Exception as e:
            logging.exception(e)

    def spider_closed(self, spider):
        logger.info(msg="-------spider_closed")
        pass


    def spider_idle(self):
        logger.info(msg="-------------spider_idle")
        self.schedule_next_requests()
        raise DontCloseSpider
