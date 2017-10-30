# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class JdItem(Item):

    #任务标识id
    jobid = Field()

    #爬取状态  0 正在爬取 1 ok 2需要手机验证码 3 图形验证码挂了或者密码错误 4 手机验证码错误
    status = Field()

    #爬虫爬行时间
    spidertime = Field()

    #用户名
    username = Field()

    #密码
    passwd = Field()

    #用户昵称

    usernickname = Field()

    #用户登录名
    userloginname = Field()

    #用户邮箱
    usermail = Field()

    #用户手机号
    userphone = Field()

    #用户身份证号
    useridcard = Field()

    #用户真实姓名
    userrealname = Field()

    #用户会员级别
    userrank = Field()

    #用户会员类型 企业用户或者个人用户
    usertype = Field()

    #余额
    balance = Field()

    #白条额度
    baitiaobalance = Field()

    #小金库
    wallet = Field()

    #昨天收益
    yesprofit = Field()

    #所有订单列表
    all_order_list = Field()

    #订单id
    orderid = Field()

    #订单时间
    ordertime = Field()

    #付款时间
    paytime = Field()

    #订单金额
    ordercount = Field()

    #订单状态
    orderstatus = Field()

    #实际支付金额
    paycount = Field()

    #收货人
    receivername = Field()

    #收货人手机号
    receiverphone = Field()

    #收货地址
    receiveraddress = Field()

    # 是否为默认收货地址 True 表示为默认收货地址 False 表示不是
    defaultaddress = Field()

    # 收货人所在地区
    rceiverdistrict = Field()

    #收货人固定电话
    receivertelephone = Field()

    #收货人电子邮箱
    receivermail = Field()

    #发票类型
    billtype = Field()

    #发票抬头
    billtitle = Field()

    #发票内容
    billcontent = Field()

    #当前订单中所有商品
    items = Field()

    #商品名称
    itemname = Field()

    #商品价格
    itemprice = Field()

    #商品数量
    itemnum = Field()

    #商品id
    itemid = Field()

    #商品url
    itemurl= Field()

    #用户小白信用分
    userverscore = Field()

    #安全级别
    safelevel = Field()

    #实名认证 True 已认证 False 无认证
    namecert = Field()

    #快递类型
    expresstype= Field()

    #快递费用
    expressfee = Field()

    #收货地址列表
    all_address = Field()

    #登陆记录列表
    login_records = Field()

    #登陆时间
    login_time = Field()

    #登陆位置
    login_location = Field()

    #登陆ip
    login_ip = Field()

    #登陆类型
    login_type = Field()



