# coding=utf-8
from scrapy import Field,Item



class UnicomItem(Item):

    # 任务标识id
    jobid = Field()

    # 爬取状态  0 正在爬取 1 ok 2需要手机验证码 3 图形验证码挂了或者密码错误(联通只有五次密码输入错误的机会) 4 手机验证码错误 6已达到5次最大登陆次数 今天无法登陆
    status = Field()

    # 爬虫爬行时间
    spidertime = Field()

    # 用户名
    username = Field()

    # 密码
    passwd = Field()

    #最近七天登陆记录列表
    recentlyloginrecord = Field()

    #登录系统
    loginos = Field()

    #登陆时间
    logintime = Field()

    #登陆位置
    loginlocation = Field()

    #登陆类型
    logintype = Field()

    #登陆浏览器类型
    loginbrowertype = Field()

    #登陆用户id
    loginuserid = Field()

    #登陆ip
    loginip = Field()

    #用户证件号码
    usercertnum = Field()

    #用户手机号
    userphonenum = Field()

    #用户收件邮箱
    usersendemail = Field()

    #用户开卡日期
    useropendate = Field()

    #用户办卡支付类型
    userpaytype = Field()

    #用户城市code
    citycode = Field()

    #用户id
    custid = Field()

    #用户姓名
    custname = Field()

    #用户套餐品牌
    brand = Field()

    #用户套餐id
    productid = Field()

    #用户套餐名字
    productname = Field()

    #用户级别
    custlvl = Field()

    #用户状态
    subscrbstat = Field()

    #用户证件类型
    certtype = Field()

    #用户证件性别
    custsex = Field()

    #用户证件地址
    certaddr = Field()

    #通话类型
    landlvl = Field()

    #漫游类型
    roamstat = Field()

    #用户标识id
    subscrbid = Field()

    #用户SIM卡id
    simcard = Field()

    #客户经理
    managername = Field()

    #客户经理联系方式
    managercontact = Field()

    #收件人姓名
    sendname = Field()

    #收件邮编
    sendpost = Field()

    #收件地址
    sendaddr = Field()

    #用户通讯id
    transid = Field()

    #用户套餐订单id
    busiorder = Field()

    #用户PUK码
    pukcode = Field()

    #用户付费类型
    payType = Field()

    #用户套餐费用
    packageFee = Field()

    #是否是VIP用户
    is_vip = Field()

    #用户VIP级别
    vip_level = Field()

    #用户网络类型
    userNettype = Field()

    #当前可用余额
    currentbalance = Field()

    #实时话费
    realfee = Field()

    #账户余额
    accountbalance = Field()

    #欠费
    loanfee = Field()

    #近半年通话记录列表
    record_list = Field()

    #通话起始日期
    calldate = Field()

    #通话起始时间
    calltime = Field()

    #通话时长
    calllonghour = Field()

    #呼叫类型
    calltypeName = Field()

    #通话号码
    othernum = Field()

    #本机通话地
    homeareaName = Field()

    #对方归属地
    calledhome = Field()

    #通话类型
    landtype = Field()

    #通话费用
    totalfee = Field()
