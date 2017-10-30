# coding=utf-8
import sys,os
sys.path.append(os.path.abspath("../"))
import logging
import time
from scrapy.http import Request,FormRequest
from scrapy.selector.lxmlsel import HtmlXPathSelector
from scrapy.spiders import CrawlSpider
import json
import requests
from scrapy import signals
import csv
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
con = rcu().get_redis()

class XindaiyunSpider(CrawlSpider):

    name = "xindaiyun"

    allowed_domains = []

    start_urls = []

    logins_url = "http://ep.duohaojr.com/signOnAuto.do"

    loginout_url = "http://ep.duohaojr.com/signOut.do"

    custom_settings = {
        "COOKIES_ENABLED": True,
        "REDIRECT_ENABLED": False,
        "RETRY_ENABLE":False,
        "REFERER_ENABLED": False,
        "USEPROXYHIGHLEVEL": False,
        "DOWNLOAD_DELAY":0,
        #"USELOCALIP":True
    }

    pay_type = {u'M':u'月',u'Q':u'季',u'W':u'周',u'Y':u'年',u'':u''}

    tag = {u'N':u'否', u'Y':u'是',u'':u''}

    all_item = []

    loan_items = {}

    cont_items = {}

    surp_items = {}

    loan_type_name = {u'':u'',u'00101_P001':u'一般消费贷款',u'00101_P002':u'汽车消费贷款',u'00221_P001':u'现金贷',u'00221_P093':u'现金贷',u'Z100034':u'惠农贷专案',u'Z100102':u'惠农贷专案-0.29%',u'Z100084':u'升级助业贷(15期,27期)',u'Z100183':u'白领贷二(0.9%账管费无利息)',u'Z100192':u'渠道业务专案-0.29%',u'Z100193':u'渠道业务专案-0.49%',u'Z100207':u'定制助业贷(15/27)',u'00724_P001':u'安房贷（一抵）先息后本',u'00724_P002':u'安房贷（一抵）等本等息',u'00724_P004':u'安牧贷-按季先息后本',u'00724_P003':u'安牧贷-先息后本',u'00724_P005':u'安银贷-等本等息',u'00724_P006':u'安企贷（抵押）先息后本',u'00724_P007':u'安企贷（信用）等本等息',u'00724_P008':u'安车贷（长期GPS）等本等息',u'00724_P009':u'安车贷（短期质押）-先息后本',u'00724_P010':u'安薪贷-等本等息',u'Z100281':u'按月付息（12+0.29）',u'00724_P011':u'惠付通白条业务',u'Z100004':u'应急贷3期',u'00724_P012':u'渠道千诚',u'00724_P013':u'安农贷-先息后本',u'00724_P014':u'安农贷-按季付息到期还本',u'00221_P094':u'尊享时贷',u'00944_P001':u'房产抵押贷款',u'00944_P002':u'房产抵押贷款（加按）',u'00944_P003':u'车辆质押贷款',u'00724_P015':u'杭州久昌车贷',u'01061_P002':u'商户贷（大众—好贷宝）',u'01061_P001':u'商户贷（美团—好贷宝）',u'01061_P003':u'商户贷（美团—廊坊银行）',u'01061_P004':u'商户贷（大众—廊坊银行）',u'01061_P005':u'商户贷（客如云分期-6期）',u'00724_P016':u'轻松贷',u'01061_P006':u'商户贷（客如云分期-9期）',u'01061_P007':u'商户贷（客如云分期-3期）',u'00944_P004':u'新车配资',u'01061_P008':u'商户贷（客如云商户贷）',u'01061_P009':u'商户贷（客如云分期-12期）',u'01061_P010':u'C/好贷宝:商户贷-IPOS-助业贷（30天）',u'01061_P011':u'C/好贷宝:商户贷-IPOS-经营贷（30天）',u'01061_P012':u'C/廊坊银行:商户贷-IPOS-经营贷（6个月）',u'01061_P013':u'C/廊坊银行:商户贷-IPOS-租金贷（6个月）',u'01061_P014':u'C/好贷宝:商户贷-客如云-流水贷（30天）',u'01061_P015':u'C/廊坊银行:商户贷-客如云-流水贷（6个月）',u'00724_P017':u'汽车后市场贷款',u'01061_P016':u'C/小贷:现金贷（1期）',u'01061_P017':u'C/小贷:现金贷（3/6期）',u'01061_P018':u'C/好贷宝:商户贷-IPOS-经营贷（90天）',u'01061_P019':u'C/廊坊银行:商户贷-IPOS-经营贷（12个月）',u'01061_P020':u'C/廊坊银行:商户贷-IPOS-租金贷（12个月）',u'01061_P022':u'C/好贷宝:商户贷-客如云-流水贷（90天）',u'01061_P021':u'C/好贷宝:商户贷-客如云-流水贷（60天）',u'01061_P023':u'C/廊坊银行:商户贷-客如云-流水贷（12个月）',u'01061_P024':u'现金贷测试',u'00101_P003':u'一般消费贷款',u'00101_P004':u'个人经营性贷款',u'01141_P001':u'担保贷款融资产品',u'01141_P002':u'预付款融资产品',u'01141_P003':u'抵质押贷款融资产品',u'01141_P004':u'缩短账期',u'01141_P005':u'员工信托贷款产品',u'00101_P001':u'一般消费贷款',u'00101_P002':u'汽车消费贷款',u'00101_P003':u'一般消费贷款',u'00101_P004':u'个人经营性贷款',u'00221_P001':u'现金贷',u'00221_P093':u'现金贷',u'00221_P094':u'尊享时贷',u'00724_P001':u'安房贷（一抵）先息后本',u'00724_P002':u'安房贷（一抵）等本等息',u'00724_P003':u'安牧贷-先息后本',u'00724_P004':u'安牧贷-按季先息后本',u'00724_P005':u'安银贷-等本等息',u'00724_P006':u'安企贷（抵押）先息后本',u'00724_P007':u'安企贷（信用）等本等息',u'00724_P008':u'安车贷（长期GPS）等本等息',u'00724_P009':u'安车贷（短期质押）-先息后本',u'00724_P010':u'安薪贷-等本等息',u'00724_P011':u'惠付通白条业务',u'00724_P012':u'渠道千诚',u'00724_P013':u'安农贷-先息后本',u'00724_P014':u'安农贷-按季付息到期还本',u'00724_P015':u'杭州久昌车贷',u'00724_P016':u'轻松贷',u'00724_P017':u'汽车后市场贷款',u'00944_P001':u'房产抵押贷款',u'00944_P002':u'房产抵押贷款（加按）',u'00944_P003':u'车辆质押贷款',u'00944_P004':u'新车配资',u'01061_P001':u'商户贷（美团—好贷宝）',u'01061_P002':u'商户贷（大众—好贷宝）',u'01061_P003':u'商户贷（美团—廊坊银行）',u'01061_P004':u'商户贷（大众—廊坊银行）',u'01061_P005':u'商户贷（客如云分期-6期）',u'01061_P006':u'商户贷（客如云分期-9期）',u'01061_P007':u'商户贷（客如云分期-3期）',u'01061_P008':u'商户贷（客如云商户贷）',u'01061_P009':u'商户贷（客如云分期-12期）',u'01061_P010':u'C/好贷宝:商户贷-IPOS-助业贷（30天）',u'01061_P011':u'C/好贷宝:商户贷-IPOS-经营贷（30天）',u'01061_P012':u'C/廊坊银行:商户贷-IPOS-经营贷（6个月）',u'01061_P013':u'C/廊坊银行:商户贷-IPOS-租金贷（6个月）',u'01061_P014':u'C/好贷宝:商户贷-客如云-流水贷（30天）',u'01061_P015':u'C/廊坊银行:商户贷-客如云-流水贷（6个月）',u'01061_P016':u'C/小贷:现金贷（1期）',u'01061_P017':u'C/小贷:现金贷（3/6期）',u'01061_P018':u'C/好贷宝:商户贷-IPOS-经营贷（90天）',u'01061_P019':u'C/廊坊银行:商户贷-IPOS-经营贷（12个月）',u'01061_P020':u'C/廊坊银行:商户贷-IPOS-租金贷（12个月）',u'01061_P021':u'C/好贷宝:商户贷-客如云-流水贷（60天）',u'01061_P022':u'C/好贷宝:商户贷-客如云-流水贷（90天）',u'01061_P023':u'C/廊坊银行:商户贷-客如云-流水贷（12个月）',u'01061_P024':u'现金贷测试',u'01141_P001':u'担保贷款融资产品',u'01141_P002':u'预付款融资产品',u'01141_P003':u'抵质押贷款融资产品',u'01141_P004':u'缩短账期',u'01141_P005':u'员工信托贷款产品',u'Z100004':u'应急贷3期',u'Z100034':u'惠农贷专案',u'Z100084':u'升级助业贷(15期,27期)',u'Z100102':u'惠农贷专案-0.29%',u'Z100183':u'白领贷二(0.9%账管费无利息)',u'Z100192':u'渠道业务专案-0.29%',u'Z100193':u'渠道业务专案-0.49%',u'Z100207':u'定制助业贷(15/27)',u'Z100281':u'按月付息（12+0.29）'}
    
    id_type = {u'20':u'身份证',u'22':u'护照',u'23':u'军官证',u'24':u'士兵证',u'25':u'港澳居民来往内地通行证',u'26':u'台湾居民来往大陆通行证',u'2X':u'其他证件',u'':u''}

    relation_type = {u'':u'',u'01':u'父母',u'02':u'子女及兄弟姐妹',u'03':u'同事',u'04':u'同学',u'05':u'朋友',u'06':u'配偶',u'99':u'其他'}

    prooerty_type = {u'':u'',u'1001':u'房产',u'1002':u'土地使用权',u'1003':u'在建工程',u'1004':u'机动车辆',u'1005':u'机械设备',u'1006':u'船舶',u'1099':u'其他抵押品',u'2001':u'股权',u'2002':u'存货',u'2003':u'应收账款',u'2099':u'其他质押品',u'4001':u'房地产留置',u'4002':u'动产留置',u'4099':u'其他押品',u'5004':u'机动车辆（杭州车贷）'}

    business_type = {u'':u'',u"10":u"国有企业",u"20":u"集体所有制企业",u"30":u"联营企业",u"40":u"三资企业",u"50":u"私营企业",u"60":u"个体工商户",u"70":u"其他企业"}

    company_type = dict([[u'',u''],[u"01",u"生产型"],[u"02",u"贸易型"],[u"03",u"服务型"],[u"04",u"其他"]])

    house_type = dict([[u'',u''],[u"01",u"自有"],[u"02",u"租赁"]])

    company_member_type = dict([[u'',u''],[u"01",u"法人代表"],[u"02",u"控股股东"],[u"03",u"未持股的实际控制人"],[u"04",u"无贷款卡"]])

    interest_type = dict([[u'',u''],[u"00101_M001",u"等额本息"],[u"00101_M002",u"等额本金"],[u"00101_M003",u"利随本清"],[u"00101_M004",u"按期还息到期还本（按天计息）"],[u"00101_M005",u"按期还息到期还本（按月计息）"],[u"00221_M001",u"等额本息"],[u"00221_M002",u"等额本金"],[u"00221_M003",u"利随本清"],[u"00221_M004",u"按期还息到期还本"],[u"00241_M001",u"等额本息"],[u"00241_M002",u"等额本金"],[u"00241_M003",u"利随本清"],[u"00241_M004",u"按期还息到期还本"],[u"00242_M001",u"等额本息"],[u"00242_M002",u"等额本金"],[u"00242_M003",u"利随本清"],[u"00242_M004",u"按期还息到期还本"],[u"00261_M001",u"等额本息"],[u"00261_M002",u"等额本金"],[u"00261_M003",u"利随本清"],[u"00261_M004",u"按期还息到期还本"],[u"00262_M001",u"等额本息"],[u"00262_M002",u"等额本金"],[u"00262_M003",u"利随本清"],[u"00262_M004",u"按期还息到期还本"],[u"00263_M001",u"等额本息"],[u"00263_M002",u"等额本金"],[u"00263_M003",u"利随本清"],[u"00263_M004",u"按期还息到期还本"],[u"00264_M001",u"等额本息"],[u"00264_M002",u"等额本金"],[u"00264_M003",u"利随本清"],[u"00264_M004",u"按期还息到期还本"],[u"00265_M001",u"等额本息"],[u"00265_M002",u"等额本金"],[u"00265_M003",u"利随本清"],[u"00265_M004",u"按期还息到期还本"],[u"00281_M001",u"等额本息"],[u"00281_M002",u"等额本金"],[u"00281_M003",u"利随本清"],[u"00281_M004",u"按期还息到期还本"],[u"00282_M001",u"等额本息"],[u"00282_M002",u"等额本金"],[u"00282_M003",u"利随本清"],[u"00282_M004",u"按期还息到期还本"],[u"00283_M001",u"等额本息"],[u"00283_M002",u"等额本金"],[u"00283_M003",u"利随本清"],[u"00283_M004",u"按期还息到期还本"],[u"00528_M001",u"等额本息"],[u"00528_M002",u"利随本清"],[u"00724_M001",u"按期还息到期还本"],[u"00724_M002",u"等本等息，配等额本金，利息部分费用里显示"],[u"00724_M003",u"按天计息到期还款(白条业务)"],[u"00724_M004",u"等额本息"],[u"00724_M005",u"体验1"],[u"00724_M006",u"jjj"],[u"00724_M007",u"按期还息到期还本（按月算）"],[u"00944_M001",u"按月付息，到期还本"],[u"00944_M002",u"到期一次性还本付息"],[u"00944_M003",u"等额本息"],[u"00944_M004",u"按月付息，到期还本"],[u"01061_M001",u"按期还息到期还本-按日"],[u"01061_M002",u"等额本息"],[u"01061_M003",u"等额本金"],[u"01061_M004",u"测试"],[u"01061_M005",u"利随本清"],[u"01061_M006",u"按期还息到期还本-按还款周期"],[u"01061_M007",u"测试2"],[u"01141_M001",u"一次扣息到期还本（按天计息）"],[u"01141_M002",u"一次扣息到期还本（按每月30天计息）"],[u"01141_M003",u"贷款抵扣"]])

    bank_type = dict([[u'',u''],[u"PSBC",u"邮储银行"],[u"CGB",u"广发银行"],[u"SPDB",u"浦发银行"],[u"CIB",u"兴业银行"],[u"PAB",u"平安银行"],[u"CMBC",u"民生银行"],[u"CEB",u"光大银行"],[u"CITIC",u"中信银行"],[u"BOB",u"北京银行"],[u"BOC",u"中国银行"],[u"HubeiBank",u"湖北银行"],[u"CCB",u"建设银行"],[u"ICBC",u"工商银行"],[u"CMB",u"招商银行"],[u"BCM",u"交通银行"],[u"ABC",u"农业银行"],[u"OTH",u"其他银行"]])
    
    _members = dict([[u'',u''],[u"010067",u"张安琪"],[u"010104",u"宋鹏洁"],[u"010109",u"马丽卿"],[u"010114",u"陶姝琳"],[u"010190",u"李飞霞"],[u"010193",u"张伟"],[u"BH0825",u"韩宇航"],[u"BH1061",u"翟馨芳"],[u"BH2548",u"智莉"],[u"BH3210",u"王如杰"],[u"BH4922",u"卫丹丹"],[u"BH5826",u"王晓芬"],[u"BHS0000",u"任建挺"],[u"BHS0710",u"张凌军"],[u"BHS1000",u"房东兴"],[u"BHS2000",u"王晓红"],[u"BHS3019",u"张伟"],[u"BHS3668",u"李飞霞"],[u"BHS3912",u"曹长江"],[u"BHS7000",u"薛春梅"],[u"BHS7513",u"黄肖兵"],[u"BJDX01",u"种颖"],[u"BJDX011",u"种颖"],[u"BJDX02",u"刘晓琪"],[u"BJDX03",u"刘芬"],[u"BJDX04",u"胥萍"],[u"BJDX05",u"斗青青"],[u"BJDX06",u"仰教梅"],[u"BJDX07",u"王蕊"],[u"BJDX08",u"加成平"],[u"BJDX09",u"张坤"],[u"BJDX10",u"陈鹏飞"],[u"BJFD01",u"BJFD01"],[u"BJFD02",u"BJFD02"],[u"BJFD03",u"BJFD03"],[u"BJFD04",u"BJFD04"],[u"BJFD06",u"BJFD06"],[u"BJWG01",u"陈鹏飞"],[u"BJYQCD01",u"BJYQCD01"],[u"BN4856",u"杨尚龙"],[u"BN5129",u"马蔺娜"],[u"BNZ0035",u"王宇"],[u"BNZ0320",u"王津晶"],[u"BNZ035",u"王涛"],[u"BNZ0518",u"李文虎"],[u"BNZ0835",u"谭黎锋"],[u"BNZ1467",u"李雪峰"],[u"BNZ1714",u"庞超"],[u"BNZ3911",u"石起飞"],[u"BNZ471X",u"尹延鲁"],[u"BNZ7320",u"翟秋雅"],[u"CCWSCD01",u"CCWSCD01"],[u"CDFD01",u"CDFD01"],[u"CPJL",u"产品经理"],[u"FC0028",u"刘童"],[u"FC0033",u"南征"],[u"FC00331",u"南征"],[u"FC0049",u"陈丽竹"],[u"GZWG01",u"方昌"],[u"GZWG02",u"郭晓华"],[u"GZWG03",u"黄睿明"],[u"GZWG04",u"徐丹凤"],[u"GZWG05",u"黄天珍"],[u"HB0187",u"王雪娟"],[u"HB0244",u"刘慧"],[u"HB0854",u"张兴"],[u"HB0926",u"HB0926"],[u"HB1254",u"崔彦军"],[u"HB1583",u"邬倩文"],[u"HB1810",u"黄斌"],[u"HB256X",u"林海霞"],[u"HB3028",u"王梦"],[u"HB3355",u"朱小克"],[u"HB3626",u"魏春华"],[u"HB3629",u"张春春"],[u"HB5020",u"王佩璇"],[u"HB5422",u"冯敏"],[u"HB804X",u"黄平"],[u"HR0031",u"侯召会"],[u"HR0428",u"刘胜男"],[u"HR0823",u"刘佳"],[u"HR1511",u"熊希鑫"],[u"HR2522",u"张兆辉"],[u"HR3249",u"梁宵"],[u"HZFD01",u"HZFD01"],[u"HZFD02",u"HZFD02"],[u"HZY012",u"刘学"],[u"HZY013X",u"韩国斌"],[u"HZY016",u"邢冰"],[u"HZY027",u"杜晶宇"],[u"HZY065",u"甘霖"],[u"HZY0920",u"赵伊"],[u"HZY621",u"朱嘉武"],[u"JHY1515",u"马东"],[u"JHY816",u"王博"],[u"JJ0022",u"杨扬"],[u"JJ013X",u"韩国斌"],[u"JJ3220",u"郭盖薇"],[u"JNBank",u"江南银行"],[u"JSadmin",u"JSadmin"],[u"JY001",u"刘俊全"],[u"KK1816",u"郭之玮"],[u"KKL6528",u"张安琪"],[u"KKZ013X",u"韩国斌"],[u"KKZ1039",u"刘俊全"],[u"KKZ1633",u"王晨旭"],[u"KKZ2949",u"郭芳"],[u"MBHT0012",u"李永春"],[u"MBHT0015",u"何小飞"],[u"MBHT0938",u"龙康"],[u"MBHT1522",u"王筝"],[u"MBHT2112",u"卜庆国"],[u"MBHT254x",u"闫小艳"],[u"MBHT3215",u"罗志伟"],[u"MDD0043",u"汪梅"],[u"MDD4442",u"孙雅君"],[u"MTB001",u"曹辉"],[u"MWL0043",u"汪梅"],[u"MWL4442",u"孙雅君"],[u"MXF001",u"汪梅"],[u"MXF002",u"孙雅君"],[u"MYY001",u"汪梅"],[u"MYY002",u"孙雅君"],[u"NK0014",u"王长浩"],[u"NK0428",u"裴婷"],[u"NK0429",u"刘丹"],[u"NK0511",u"王春柳"],[u"NK0715",u"李瑞文"],[u"NK1060",u"郭佳宁"],[u"NK1274",u"赵成龙"],[u"NK1979",u"杨海峰"],[u"NK2262",u"栾明莉"],[u"NK2279",u"杨庆华"],[u"QBadmin",u"QBadmin"],[u"SHWG01",u"张乔"],[u"SHWG02",u"胡蒙蒙"],[u"SJcszh",u"SJ测试账号"],[u"SXZD0029",u"詹阳"],[u"SXZD1535",u"郑玉华"],[u"SXZD5455",u"钱晋"],[u"SXZD5718",u"周保峰"],[u"SYWG01",u"刘倩"],[u"SYWG02",u"程宏宇"],[u"SZCZHPZ01",u"SZCZHPZ01"],[u"SZFD01",u"SZFD01"],[u"SZFD02",u"SZFD02"],[u"TJBLCD01",u"TJBLCD01"],[u"TZY2511",u"郭林正"],[u"TZY2517",u"王国忠"],[u"TZY3737",u"王志远"],[u"TZY4537",u"潘仙送"],[u"TZY6946",u"王云云"],[u"WT3932",u"林波"],[u"WTR545",u"刘春云"],[u"WZ221X",u"陈秋"],[u"WZ2613",u"潘瑞熠"],[u"WZ5317",u"曾平相"],[u"XAMSadmin",u"XAMSadmin"],[u"XHB0012",u"黄波波"],[u"XHB0028",u"刘童"],[u"XHB0069",u"黄莉婷"],[u"XHB0219",u"朱辉"],[u"XHB0317",u"王宏斌"],[u"XHB0548",u"刘琬"],[u"XHB0636",u"朱楠"],[u"XHB0844",u"肖颖"],[u"XHB0987",u"张欢"],[u"XHB1334",u"陈博"],[u"XHB1525",u"庆文婧"],[u"XHB2208",u"唐高飞"],[u"XHB252X",u"牛彦翠"],[u"XHB2538",u"李晓彬"],[u"XHB2718",u"宫振文"],[u"XHB4316",u"李昊"],[u"XHB4943",u"聂希桂"],[u"XHB5226",u"唐艳梅"],[u"XHB5663",u"吴鸾洁"],[u"XHB6126",u"史雯雯"],[u"XHB6721",u"朱泽"],[u"XHB8642",u"孙璐"],[u"XHB878X",u"滕双妍"],[u"XMNTsy",u"XMNT试用"],[u"XMTLsy",u"XMTL试用"],[u"XP4312",u"童飞澎"],[u"YHLZ01",u"周保峰"],[u"YHLZ02",u"郑玉华"],[u"YHLZ03",u"詹阳"],[u"YHLZ04",u"钱晋"],[u"YHXY01",u"周保峰"],[u"YHXY02",u"郑玉华"],[u"YHXY03",u"詹阳"],[u"YHXY04",u"钱晋"],[u"YHZ1536",u"苏冰鑫"],[u"YHZ2618",u"潘文明"],[u"YHZ5168",u"谭小妹"],[u"YHZ6916",u"陈必彬"],[u"YK0822",u"李诗瑶"],[u"YL0013",u"王军"],[u"YL0020",u"张鑫"],[u"YL0034",u"冯永永"],[u"YL0069",u"刘慧芳"],[u"YL0213",u"牛刚"],[u"YL0822",u"李诗瑶"],[u"YL1028",u"张娜"],[u"YL3018",u"原晓波"],[u"YL3927",u"陈丽朵"],[u"YL7922",u"王芳媛"],[u"YL8325",u"侯旭燕"],[u"YL918X",u"杨泓"],[u"YX0311",u"冯雷"],[u"YX0512",u"郑继"],[u"YX0825",u"余琴"],[u"YX0826",u"刘晓燕"],[u"YX092X",u"韦兴星"],[u"YX1763",u"胡月"],[u"YX2416",u"李九序"],[u"YX2525",u"王志雅"],[u"YX282X",u"郭沐霖"],[u"YX2975",u"刘疆"],[u"YX3244",u"赵俊"],[u"YX4811",u"罗鹏飞"],[u"YX5276",u"韩润石"],[u"YX5416",u"卢小彬"],[u"YX5501",u"蒋娟"],[u"YX6019",u"秦谊"],[u"YXB0012",u"赵晓光"],[u"YXB0718",u"杨洋"],[u"YXB1264",u"董娜"],[u"YXB4746",u"张小雪"],[u"YXC1818",u"王佳宁"],[u"YXC2012",u"王学锋"],[u"YXC3726",u"陈彩月"],[u"YXC402x",u"邵丽丽"],[u"YXD021x",u"万煜鹏"],[u"YXD0244",u"郝爽"],[u"YXF0012",u"李晓波"],[u"YXF0028",u"高慧"],[u"YXF0118",u"魏国荣"],[u"YXF1124",u"刘春美"],[u"YXF1564",u"吴玥"],[u"YXF2717",u"于磊"],[u"YXF3228",u"陶佳"],[u"YXH0126",u"张晟铭"],[u"YXH1607",u"高阳"],[u"YXH3019",u"宁艳宾"],[u"YXH6017",u"张斌"],[u"YXL0933",u"于潾"],[u"YXL1222",u"杨超颖"],[u"YXL2414",u"王泽鹏"],[u"YXL2420",u"王金兰"],[u"YXL2912",u"刘亚楠"],[u"YXL3023",u"李楠"],[u"YXL6538",u"张磊"],[u"YXL8027",u"解佳会"],[u"YXQ1038",u"程广如"],[u"YXQ1513",u"王利鹏"],[u"YXQ5144",u"张思平"],[u"YXQ7821",u"郭艳"],[u"YXT0041",u"郝晶"],[u"YXT242x",u"王慧"],[u"YXT411x",u"刘全旺"],[u"YXW1722",u"张明"],[u"YXZ2425",u"康慧"],[u"YXZ3510",u"杜云丰"],[u"YXZ6047",u"魏巧丽"],[u"YZ102X",u"王红玉"],[u"YZ7618",u"李康"],[u"ZF0024",u"刘雨嫣"],[u"ZF0057",u"孙炎"],[u"ZF0169",u"姚海燕"],[u"ZF0420",u"刘益含"],[u"ZF0425",u"张露"],[u"ZF0940",u"李佳"],[u"ZF1255",u"郭猛"],[u"ZF1812",u"宋亮"],[u"ZF1915",u"保和佳"],[u"ZF2518",u"陶锡键"],[u"ZF2971",u"冯小平"],[u"ZF3019",u"蔡二成"],[u"ZF3893",u"赵燕飞"],[u"ZF5048",u"郑斌玲"],[u"ZF5428",u"童婷婷"],[u"ZF6047",u"邬黎炜"],[u"ZF6181",u"杨星"],[u"ZF6213",u"林喜龙"],[u"ZF8446",u"陈媛媛"],[u"ZW0022",u"胡嫚嫚"],[u"ZW0024",u"杨孝圆"],[u"ZW0027",u"张静敏"],[u"ZW032X",u"胡夏映"],[u"ZW0510",u"麻建平"],[u"ZW0685",u"刘宁珂"],[u"ZW0801",u"黄笑雨"],[u"ZW0846",u"汤晶晶"],[u"ZW0923",u"蔡艳红"],[u"ZW1406",u"王月"],[u"ZW1522",u"单巧云"],[u"ZW1524",u"兰芸"],[u"ZW1821",u"萧丽华"],[u"ZW1842",u"何云"],[u"ZW2027",u"韦方美"],[u"ZW2229",u"张梅"],[u"ZW2427",u"陈小贝"],[u"ZW3021",u"曹雅丽"],[u"ZW3222",u"翟妍曦"],[u"ZW452X",u"陈洁"],[u"ZW4629",u"王慧琴"],[u"ZW5363",u"苏楚玲"],[u"ZW5725",u"李妍"],[u"ZW5733",u"黄杨"],[u"ZW5925",u"卢秋玲"],[u"ZW6037",u"徐益星"],[u"ZW702X",u"沈晓丹"],[u"ZW7042",u"梁卉卉"],[u"ZW8120",u"王婷"],[u"ZW8416",u"刘振亚"],[u"ZW8625",u"陈雅艳"],[u"ZW8726",u"王璇"],[u"admin",u"超级管理员"],[u"ahbgadm",u"ahbgadm"],[u"ahfdadm",u"ahfdadm"],[u"ahfjjradmin",u"ahfjjradmin"],[u"ahhzadm",u"ahhzadm"],[u"ahjyadm",u"ahjyadm"],[u"aihy",u"艾贺勇"],[u"aihy1",u"艾贺勇"],[u"ancl",u"安崇磊"],[u"ancl1",u"安崇磊"],[u"anhs",u"安贺山"],[u"anhs1",u"安贺山"],[u"arjradmin",u"arjradmin"],[u"asayadm",u"asayadm"],[u"asxmadm",u"asxmadm"],[u"baijl",u"白皎龙"],[u"bailq",u"白灵巧"],[u"bailq1",u"白灵巧"],[u"baiming",u"白明"],[u"baiming1",u"白明"],[u"baiming2",u"白明"],[u"baiming3",u"白明"],[u"baixc",u"白新翠"],[u"baiyb",u"白艳兵"],[u"baiyb1",u"白艳兵"],[u"baohw",u"包红伟"],[u"baohw1",u"包红伟"],[u"bdcfadm",u"bdcfadm"],[u"bddzadm",u"bddzadm"],[u"beilang",u"北浪"],[u"beiygly",u"北银管理员"],[u"biance",u"边策"],[u"bianwj",u"边文娟"],[u"bianxh",u"卞晓海"],[u"bixl",u"毕晓林"],[u"bj2248",u"张小培"],[u"bjqcadm",u"bjqcadm"],[u"blnadmin",u"blnadmin"],[u"bomg",u"柏名光"],[u"bomg1",u"柏名光"],[u"bxladm",u"bxladm"],[u"byadmin",u"byadmin"],[u"caicy",u"蔡春阳"],[u"caijf",u"蔡军峰"],[u"caijl",u"蔡嘉玲"],[u"caijl1",u"蔡嘉玲"],[u"caijp",u"蔡晋普"],[u"caiwh",u"蔡卫华"],[u"caixh",u"蔡晓红"],[u"caiyq",u"蔡勇球"],[u"cangsq",u"仓胜奇"],[u"caocs",u"曹春笋"],[u"caokuo",u"曹阔"],[u"caolei",u"曹磊"],[u"caoqs",u"曹秋实"],[u"caoqs1",u"曹秋实"],[u"caoshun",u"曹顺"],[u"caosy",u"曹思远"],[u"caosy1",u"曹思远"],[u"caowz",u"曹伟志"],[u"caoxp",u"曹熙鹏"],[u"caoyd",u"曹永东"],[u"caoyd1",u"曹永东"],[u"caoyy",u"曹越勇"],[u"caoyy1",u"曹越勇"],[u"caozj",u"曹志军"],[u"cc0081",u"吴君"],[u"cd0018",u"李军"],[u"cd001X",u"王了一"],[u"cd0028",u"王英舰"],[u"cd0081",u"吴君"],[u"cd041X",u"黄浩"],[u"cd1411",u"吴挺鹏"],[u"cd1825",u"王语传"],[u"cd2264",u"黄露"],[u"cd247X",u"田洪"],[u"cd2633",u"潘文斌"],[u"cd2972",u"黄果"],[u"cd5785",u"甘林"],[u"cd6011",u"苏磊"],[u"cd7030",u"李英林"],[u"cd7627",u"郭勤学"],[u"cd7719",u"王帮明"],[u"cd779X",u"赵江"],[u"cedadm",u"cedadm"],[u"cenghm",u"曾惠美"],[u"cengsn",u"曾思娜"],[u"cengzw",u"曾昭伟"],[u"ceszh",u"测试账户"],[u"chaijk",u"柴锦科"],[u"changcl",u"常春龙"],[u"changcl1",u"常春龙"],[u"changcl2",u"常春龙"],[u"changcl3",u"常春龙"],[u"changhd",u"朱可"],[u"changll",u"常利利"],[u"changwl",u"常文龙"],[u"changxian",u"常贤"],[u"changyk",u"常亚可"],[u"chaxry",u"查询人员"],[u"chaxyh",u"查询用户"],[u"chenchao",u"陈超（杭州）"],[u"chencs",u"陈才山"],[u"chencs1",u"陈才山"],[u"chendh",u"陈玬华"],[u"chendh1",u"陈玬华"],[u"chendy",u"陈迪勇"],[u"chendy1",u"陈迪勇"],[u"chenfg",u"陈福刚"],[u"chenfg1",u"陈福刚"],[u"chenfm",u"陈方敏"],[u"chengfan",u"程帆"],[u"chengfan1",u"程帆"],[u"chenghy",u"程红煜"],[u"chengling",u"程玲"],[u"chengmj",u"程美津"],[u"chengx2",u"陈国雄"],[u"chengxue",u"程雪"],[u"chengxue1",u"程雪"],[u"chengyi",u"程毅"],[u"chengyong",u"成勇"],[u"chengyong1",u"成勇"],[u"chengyy",u"程圆圆"],[u"chengyy1",u"程圆圆"],[u"chenhan",u"陈涵"],[u"chenhf",u"陈惠锋"],[u"chenhh",u"陈惠惠"],[u"chenhl",u"陈红亮"],[u"chenhq",u"陈海奇"],[u"chenhq1",u"陈海奇"],[u"chenhui",u"陈辉"],[u"chenjh",u"陈杰华"],[u"chenjh1",u"陈杰华"],[u"chenjia2",u"陈佳"],[u"chenjiao",u"陈娇"],[u"chenjiao1",u"陈娇"],[u"chenjie",u"陈洁"],[u"chenjie1",u"陈洁"],[u"chenjing",u"陈靖"],[u"chenjing1",u"陈靖"],[u"chenjp",u"陈金平"],[u"chenjuan",u"陈娟"],[u"chenlei",u"红蚂蚁"],[u"chenlei1",u"陈蕾"],[u"chenlei2",u"陈蕾"],[u"chenlm",u"陈莉敏"],[u"chenming",u"陈明"],[u"chenmo",u"陈漠"],[u"chenmy",u"陈牧宇"],[u"chenmy1",u"陈牧宇"],[u"chennn",u"陈南南"],[u"chenquan",u"陈全"],[u"chenquan1",u"陈全"],[u"chenran",u"陈冉"],[u"chenrong",u"陈荣"],[u"chensf",u"陈双凤"],[u"chensf1",u"陈双发"],[u"chensh",u"陈素红"],[u"chensi",u"陈思"],[u"chensq",u"陈思奇"],[u"chensq1",u"陈思奇"],[u"chenss",u"陈胜生"],[u"chensw",u"陈思葳"],[u"chensy",u"陈丝雨"],[u"chensy1",u"陈丝雨"],[u"chensy2",u"陈丝雨"],[u"chensy3",u"陈丝雨"],[u"chenwj",u"陈文静"],[u"chenwj1",u"陈维佳"],[u"chenxd",u"陈旭东"],[u"chenxf",u"陈小飞"],[u"chenxf1",u"陈小飞"],[u"chenxia",u"陈霞"],[u"chenxian",u"陈娴"],[u"chenxian1",u"谌贤"],[u"chenxl",u"陈小丽"],[u"chenxl1",u"陈小丽"],[u"chenxu1",u"陈旭"],[u"chenxu2",u"陈旭"],[u"chenxue",u"陈雪"],[u"chenxue1",u"陈雪"],[u"chenyang",u"陈阳"],[u"chenyb",u"陈炎彬"],[u"chenyf",u"陈韵芳"],[u"chenyh",u"陈永红"],[u"chenyh1",u"陈永红"],[u"chenyl",u"陈妍琳"],[u"chenyl1",u"陈妍琳"],[u"chenym",u"陈艳梅"],[u"chenym1",u"陈一蒙"],[u"chenyong",u"陈勇"],[u"chenzf",u"陈治凡"],[u"chenzj",u"陈政军"],[u"chenzj1",u"陈政军"],[u"chenzy",u"陈志勇"],[u"chenzy1",u"陈长源"],[u"chifx",u"迟凤霞"],[u"chiql",u"池巧玲"],[u"chujz",u"楚建忠"],[u"chuoyx",u"啜燕雄"],[u"chyadm2",u"chyadm"],[u"cq0017",u"李彬"],[u"cq3468",u"尹义静"],[u"cqcfadm",u"cqcfadm"],[u"cqhfadmin",u"cqhfadmin"],[u"cssyadm",u"cssyadm"],[u"cszyadmin",u"cszyadmin"],[u"cuifh",u"崔付华"],[u"cuihao",u"崔皓"],[u"cuihao1",u"崔皓"],[u"cuijl",u"崔建岭"],[u"cuilei",u"崔磊"],[u"cuilei1",u"崔磊"],[u"cuimeng",u"崔萌"],[u"cuiqiang",u"崔强"],[u"cuiwei",u"崔伟"],[u"cuiwei1",u"崔伟"],[u"cuiwt",u"崔婉婷"],[u"cuiwt1",u"崔婉婷"],[u"cuiwt2",u"崔婉婷"],[u"cuiwt3",u"崔婉婷"],[u"cuixd",u"崔晓东"],[u"cuixd1",u"崔晓东"],[u"cuixn",u"崔向南"],[u"cuiyang",u"崔洋"],[u"cuiyang1",u"崔洋"],[u"cuiyb",u"崔燕兵"],[u"cuiyj",u"崔艳君"],[u"cuiyj1",u"崔艳君"],[u"cuiyp",u"崔云鹏"],[u"cuiyp1",u"崔云鹏"],[u"cxdadm",u"cxdadm"],[u"czryadmin",u"czryadmin"],[u"dailei",u"代磊"],[u"daitian",u"代天"],[u"daitian1",u"代天"],[u"daiyuan",u"戴媛"],[u"daizheng",u"戴征"],[u"daizheng1",u"戴征"],[u"dangkk",u"党轲轲"],[u"danxc",u"单小春"],[u"ddmxadm",u"ddmxadm"],[u"dengbx",u"邓柏祥"],[u"dengjy",u"邓杰洋"],[u"dengly",u"邓丽亚"],[u"dengly1",u"邓丽亚"],[u"dengme",u"邓美娥"],[u"dengqx",u"邓桥雪"],[u"dengqx1",u"邓桥雪"],[u"dengrg",u"邓日桂"],[u"dengrg1",u"邓日桂"],[u"dengting",u"邓婷"],[u"dengting1",u"邓婷"],[u"dengzhe",u"邓哲"],[u"dfjcadmin",u"dfjcadmin"],[u"diaojh",u"刁建华"],[u"diaojh1",u"刁建华"],[u"diaoqm",u"刁清明"],[u"dinghh",u"丁焕红"],[u"dinghh1",u"丁焕红"],[u"dingsb",u"定胜斌"],[u"dingws",u"丁文生"],[u"dingws1",u"丁文生"],[u"dingxz",u"丁晓哲"],[u"djhtadm",u"djhtadm"],[u"dk001X",u"杜康"],[u"dljdadmin",u"dljdadmin"],[u"dlwtadm",u"dlwtadm"],[u"dlykfadm",u"dlykfadm"],[u"dongfw",u"董峰伟"],[u"donghs",u"冬海松"],[u"dongjb",u"董继波"],[u"dongjb1",u"董继波"],[u"dongjf",u"董继芳"],[u"dongjie",u"董杰"],[u"dongjie1",u"董杰"],[u"dongjq",u"董继琴"],[u"donglq",u"董立强"],[u"donglq1",u"董立强"],[u"dongpl",u"董鹏亮"],[u"dongtao",u"董涛"],[u"dongtz",u"董天增"],[u"dongwu",u"董武"],[u"dongxiao",u"董潇"],[u"dongxue",u"董雪"],[u"dongyy",u"董一颖"],[u"dongyy1",u"董一颖"],[u"dougx",u"窦国仙"],[u"dougx1",u"窦国仙"],[u"douyb",u"窦艳波"],[u"dqlhadm",u"dqlhadm"],[u"duangs",u"段广双"],[u"duangs1",u"段广双"],[u"duanll",u"段蕾蕾"],[u"duantt",u"段婷婷"],[u"duanyz",u"段元柱"],[u"duanyz1",u"段元柱"],[u"duanyz2",u"段元柱"],[u"duanyz3",u"段元柱"],[u"dubz",u"杜宝忠"],[u"dufy",u"杜风英"],[u"dufy1",u"杜风英"],[u"dufy2",u"杜风英"],[u"dufy3",u"杜风英"],[u"dugj",u"杜国军"],[u"dugj1",u"杜国军"],[u"duht",u"杜海涛"],[u"duhw",u"杜红伟"],[u"duhw1",u"杜红伟"],[u"duhy",u"杜航宇"],[u"dulm",u"杜黎明"],[u"dulm1",u"杜黎明"],[u"dulp",u"杜丽萍"],[u"duxh",u"杜学会"],[u"duxh1",u"杜学会"],[u"duxia",u"杜霞"],[u"duxia1",u"杜霞"],[u"duxy",u"杜晓英"],[u"duxy1",u"杜晓英"],[u"duyl",u"杜沿霖"],[u"duyl1",u"杜沿霖"],[u"duzj",u"杜长健"],[u"dysmadm",u"dysmadm"],[u"dyzradm",u"dyzradm"],[u"ejl1",u"鄂家俐"],[u"exrhadm",u"exrhadm"],[u"fanggw",u"方国伟"],[u"fanggw1",u"方国伟"],[u"fangru",u"方茹"],[u"fangru1",u"方茹"],[u"fangyan",u"房艳"],[u"fangyan1",u"房艳"],[u"fangyz",u"方源珍"],[u"fangzhe",u"方哲"],[u"fanlh",u"樊立红"],[u"fanpw",u"范盼望"],[u"fanql",u"范庆龙"],[u"fanxx",u"范习喜"],[u"fanyq",u"范永情"],[u"feibo",u"费波"],[u"feibo1",u"费波"],[u"fengchun",u"冯春"],[u"fengfl",u"冯福来"],[u"fengfl1",u"冯福来"],[u"fenggang",u"冯刚"],[u"fengkai",u"冯凯"],[u"fengkai1",u"冯凯"],[u"fengkai2",u"冯凯"],[u"fengkai3",u"冯凯"],[u"fengky",u"冯康又"],[u"fengkys",u"风控一审"],[u"fengli",u"冯莉（深圳）"],[u"fenglm",u"封利美"],[u"fengmz",u"冯明珠"],[u"fengsj",u"冯士江"],[u"fengtt",u"冯桃桃"],[u"fengtt1",u"冯桃桃"],[u"fengtt2",u"冯桃桃"],[u"fengtt3",u"冯桃桃"],[u"fengxx",u"冯欣欣"],[u"fgadm",u"fgadm"],[u"fjfadm",u"fjfadm"],[u"fudm",u"付冬梅"],[u"fudy",u"付东亚"],[u"fuhh",u"付欢欢"],[u"fuhl",u"付翰林"],[u"fujf",u"傅建飞"],[u"fujie",u"付婕"],[u"fulm",u"付利明"],[u"fulm1",u"付利明"],[u"fulx",u"付流星"],[u"fuzx",u"付佐旭"],[u"fuzx1",u"付佐旭"],[u"fynyadm",u"fynyadm"],[u"ganxx",u"甘献新"],[u"gaocl",u"高春林"],[u"gaocl1",u"高春林"],[u"gaocl2",u"高纯林"],[u"gaodz",u"高道芝"],[u"gaofei",u"高飞"],[u"gaofeng",u"高峰"],[u"gaohl",u"高海玲"],[u"gaojj",u"高晶晶"],[u"gaojp",u"高江平"],[u"gaomei",u"高梅"],[u"gaomn",u"高美娜"],[u"gaomn1",u"高美娜"],[u"gaomn2",u"高梦楠"],[u"gaomn3",u"高梦楠"],[u"gaomn4",u"高孟楠"],[u"gaomn5",u"高孟楠"],[u"gaorong",u"高荣"],[u"gaorong1",u"高荣"],[u"gaowei",u"高伟"],[u"gaowj",u"郜闻杰"],[u"gaowj1",u"郜闻杰"],[u"gaowj2",u"郜闻杰"],[u"gaowj3",u"郜闻杰"],[u"gaoxue",u"高雪"],[u"gaoxue1",u"高雪"],[u"gaoxx",u"高鑫鑫"],[u"gaoxy",u"高馨雨"],[u"gaoyd",u"高玉娣"],[u"gaoyj",u"高永军"],[u"gaoyj1",u"高永军"],[u"gaoyy",u"高艺源"],[u"gaozj",u"高志坚"],[u"gaozj1",u"高志坚"],[u"gdhlzcadmin",u"gdhlzcadmin"],[u"gdysadmin",u"gdysadmin"],[u"gengbf",u"耿保丰"],[u"gengbf1",u"耿保丰"],[u"genghs",u"耿会生"],[u"gengxw",u"耿协伟"],[u"gengyan",u"耿颜"],[u"gengyf",u"耿亚芳"],[u"gengyf1",u"耿亚飞"],[u"gexh",u"葛小焕"],[u"ghadm",u"ghadm"],[u"glcydzadmin",u"glcydzadmin"],[u"glmxadmin",u"glmxadmin"],[u"gongcf",u"龚彩凤"],[u"gongcf1",u"龚彩凤"],[u"gongwb",u"龚伟斌"],[u"gongzh",u"拱中辉"],[u"gongzh1",u"拱中辉"],[u"gongzhen",u"龚珍"],[u"gqadm",u"gqadm"],[u"guanff",u"关发发"],[u"guanss",u"关珊珊"],[u"guanss1",u"关珊珊"],[u"gule1",u"谷乐"],[u"gule2",u"谷乐"],[u"gulei",u"谷磊"],[u"gumy",u"顾明月"],[u"gumy1",u"顾明月"],[u"guochao",u"郭超"],[u"guochao1",u"郭超"],[u"guocong",u"郭聪"],[u"guogw",u"郭盖薇"],[u"guojc",u"郭建彩"],[u"guojy",u"郭競谣"],[u"guolei",u"郭蕾"],[u"guomin",u"郭敏"],[u"guomin1",u"郭敏"],[u"guopei",u"郭沛"],[u"guopei1",u"郭沛"],[u"guopeng",u"郭鹏"],[u"guopeng1",u"郭鹏"],[u"guosp",u"郭圣平"],[u"guosp1",u"郭圣平"],[u"guott",u"郭婷婷"],[u"guotz",u"郭田芝"],[u"guowc",u"郭伟超"],[u"guowz",u"郭文忠"],[u"guoxd",u"郭绪东"],[u"guoxh",u"郭新豪"],[u"guoxj（bj）",u"郭晓靓（北京）"],[u"guoxl",u"郭晓靓（北京）"],[u"guoxm",u"郭祥明"],[u"guoxx",u"郭鑫鑫"],[u"guoxx1",u"郭鑫鑫"],[u"guoxy",u"郭新义"],[u"guoxy1",u"郭秀颖"],[u"guozheng",u"郭峥"],[u"guozs",u"郭志水"],[u"guozs1",u"郭志水"],[u"guozs2",u"郭长顺"],[u"guozs3",u"郭长顺"],[u"guozs4",u"郭志水"],[u"guozs5",u"郭志水"],[u"guqing",u"顾庆"],[u"gusy",u"顾守彦"],[u"gutao",u"顾涛"],[u"gutao1",u"顾涛"],[u"guxc",u"顾昕晨"],[u"guyf",u"辜跃飞"],[u"guyf1",u"辜跃飞"],[u"gxhadm",u"gxhadm"],[u"gxjwadmin",u"gxjwadmin"],[u"gxqladmin",u"gxqladmin"],[u"gxtyadm",u"gxtyadm"],[u"gxxzhyadmin",u"gxxzhyadmin"],[u"gz0081",u"吴君"],[u"gzjdzadmin",u"gzjdzadmin"],[u"gztwadm",u"gztwadm"],[u"ha1848",u"孙明艳"],[u"ha3468",u"尹义静"],[u"hancy",u"韩彩英"],[u"hanff",u"韩芳芳"],[u"hanff1",u"韩芳芳"],[u"hangx2",u"韩国玺"],[u"hangx3",u"韩国玺"],[u"hangx8",u"韩国玺"],[u"hangx9",u"韩国玺"],[u"hangyj1",u"杭毅君"],[u"hangzjc",u"杭州久昌"],[u"hanhan",u"韩涵"],[u"hanhan1",u"韩涵"],[u"hanhan2",u"韩涵"],[u"hanhan3",u"韩涵"],[u"hankk",u"韩康康"],[u"hanshuai",u"韩帅"],[u"hanwei1",u"韩玮"],[u"hanxu",u"韩旭"],[u"hanyy",u"韩盈盈"],[u"hanyy1",u"韩盈盈"],[u"haocm",u"郝超美"],[u"haojx",u"郝建秀"],[u"haolj",u"郝刘佳"],[u"haolj1",u"郝刘佳"],[u"haowj",u"郝文军"],[u"haozg",u"郝治国"],[u"haozg1",u"郝治国"],[u"hapcadm",u"hapcadm"],[u"hbadm",u"hbadm"],[u"hchyadm",u"hchyadm"],[u"hcwladm",u"hcwladm"],[u"hebb",u"贺贝贝"],[u"hebing",u"何兵"],[u"hecy",u"何翠英"],[u"hecy1",u"何翠英"],[u"hefs",u"贺逢升"],[u"hefs1",u"贺逢升"],[u"hefs2",u"贺逢升"],[u"hehuan",u"贺欢"],[u"hehui",u"何辉"],[u"hekx",u"何可心"],[u"helb",u"何凌斌"],[u"helin",u"何琳"],[u"helt",u"何立婷"],[u"hepeng",u"何鹏"],[u"hepeng1",u"何鹏"],[u"heqin",u"何琴"],[u"hesm",u"何思敏"],[u"hewh",u"何文辉"],[u"hewh1",u"何文辉"],[u"hewq1",u"何文起"],[u"hewq2",u"何文起"],[u"heyan",u"何燕"],[u"heyh",u"何耀华"],[u"heyh1",u"何耀华"],[u"heyong",u"何勇"],[u"hflradmin",u"hflradmin"],[u"hhhxadm",u"hhhxadm"],[u"hhlbadm",u"hhlbadm"],[u"hhradm",u"hhradm"],[u"hhsmadm",u"hhsmadm"],[u"hjadm",u"hjadm"],[u"hjsadmin",u"hjsadmin"],[u"hk292X",u"康小姝"],[u"hntradmin",u"hntradmin"],[u"hnwsjadm",u"hnwsjadm"],[u"hnxhadm",u"hnxhadm"],[u"hnxtadmin",u"hnxtadmin"],[u"honglp",u"洪璐萍"],[u"hongxj",u"洪溪娟"],[u"houdi",u"侯迪"],[u"houfeng",u"侯锋"],[u"houhuan",u"侯欢"],[u"houhuan1",u"侯欢"],[u"houmy2",u"侯美玉"],[u"houmy3",u"侯美玉"],[u"housj",u"侯仕杰"],[u"housj1",u"侯仕杰"],[u"houtao",u"侯涛"],[u"houwt",u"侯文婷"],[u"houzl",u"侯志良"],[u"hqsmadm",u"hqsmadm"],[u"hsadmin",u"hsadmin"],[u"huangcm",u"黄诚妙"],[u"huangfeng",u"黄锋"],[u"huangjf",u"黄敬福"],[u"huangjl",u"黄建玲"],[u"huangjq",u"黄俊强"],[u"huangjq1",u"黄俊强"],[u"huangjq2",u"黄俊强"],[u"huangjq3",u"黄俊强"],[u"huangjq4",u"黄俊秋"],[u"huangjuan",u"黄娟（广州）"],[u"huangjx",u"黄久杏"],[u"huangli",u"黄丽"],[u"huangli1",u"黄丽"],[u"huangli2",u"黄丽"],[u"huanglong",u"黄龙"],[u"huanglong1",u"黄龙"],[u"huanglong2",u"黄龙"],[u"huangly",u"黄龙宇"],[u"huangning",u"黄宁"],[u"huangning1",u"黄宁"],[u"huangning2",u"黄宁"],[u"huangning3",u"黄宁"],[u"huangning4",u"黄宁"],[u"huangqb",u"黄琼波"],[u"huangst",u"黄诗婷"],[u"huangtt",u"黄婷婷"],[u"huangtt1",u"黄婷婷"],[u"huangxb",u"黄晓冰"],[u"huangxb1",u"黄晓冰"],[u"huangxh",u"黄晓红"],[u"huangxh1",u"黄晓红"],[u"huangxh2",u"黄兴华"],[u"huangxh3",u"黄向煌"],[u"huangxl",u"黄雪兰"],[u"huangyg",u"黄以庚"],[u"huangyi",u"黄怡"],[u"huangyw",u"黄炎伟"],[u"huangzf",u"黄真福"],[u"huangzf1",u"黄梓福"],[u"huangzh",u"黄振桓"],[u"huangzj",u"黄正军"],[u"huaw",u"胡爱唯"],[u"huaw1",u"胡爱唯"],[u"huaw2",u"胡爱唯"],[u"huaxy",u"花晓燕"],[u"huaxy1",u"花晓燕"],[u"hujf",u"胡俊峰"],[u"hujie",u"胡杰"],[u"hujj",u"胡家俊"],[u"hujj1",u"胡家俊"],[u"hujs",u"胡佳森"],[u"hujs1",u"胡佳森"],[u"hujy1",u"胡嘉莹"],[u"hujy2",u"胡嘉莹"],[u"hukk",u"胡科科"],[u"huliang",u"胡亮"],[u"humc",u"胡明超"],[u"humc1",u"胡明超"],[u"humc2",u"胡明超"],[u"humc3",u"胡明超"],[u"huofl",u"霍付玲"],[u"huoyy",u"霍玥媛"],[u"huoyy1",u"霍玥媛"],[u"hupx",u"胡培兴"],[u"husj",u"胡少剑"],[u"husp",u"胡锁朋"],[u"huxb",u"胡雄兵"],[u"huxb1",u"胡雄兵"],[u"huxb2",u"胡雄兵"],[u"huxb3",u"胡雄兵"],[u"huyj",u"胡玉静"],[u"huyj1",u"胡玉静"],[u"huyl",u"户艳玲"],[u"huyl1",u"户艳玲"],[u"huym",u"胡亚敏"],[u"huyx",u"胡亚勋"],[u"huyx1",u"胡亚勋"],[u"huzq",u"胡志强"],[u"hyadm6",u"hyadm"],[u"hyjjadm",u"hyjjadm"],[u"hz0081",u"吴君"],[u"jczadm",u"jczadm"],[u"jdtzadmin",u"jdtzadmin"],[u"jhsmadm",u"jhsmadm"],[u"jiahf",u"贾海峰"],[u"jiaht",u"贾鹤婷"],[u"jiaht1",u"贾鹤婷"],[u"jiakuan",u"贾宽"],[u"jiaman",u"贾曼"],[u"jiaman1",u"贾曼"],[u"jiana",u"贾娜"],[u"jiangbo",u"蒋波"],[u"jiangchen",u"蒋晨"],[u"jianghao",u"姜浩"],[u"jianghl",u"红蚂蚁"],[u"jianghua",u"姜华"],[u"jianghua1",u"姜华"],[u"jianghua2",u"姜华"],[u"jianghua3",u"姜华"],[u"jianghua4",u"江华"],[u"jiangjl",u"蒋金丽"],[u"jiangjun",u"蒋军"],[u"jiangjx",u"蒋金祥"],[u"jianglf",u"蒋令峰"],[u"jiangli",u"江丽"],[u"jiangling",u"姜凌"],[u"jiangmm",u"蒋敏敏"],[u"jiangtz",u"蒋太志"],[u"jiangtz1",u"蒋太志"],[u"jiangwy",u"姜文宇"],[u"jiangyan",u"蒋燕"],[u"jiangyi",u"江逸"],[u"jiangyong",u"蒋勇"],[u"jiangyuan",u"姜媛"],[u"jiangzw",u"蒋正武"],[u"jianmm",u"简明明"],[u"jiaohao",u"焦昊"],[u"jiawd",u"贾伟东"],[u"jiawd1",u"贾伟东"],[u"jiaxj",u"贾秀娟"],[u"jiaxj1",u"贾秀娟"],[u"jiaying",u"贾莹"],[u"jiayuan",u"贾源"],[u"jiayuan1",u"贾源"],[u"jiayuan2",u"贾源"],[u"jiayuan3",u"贾源"],[u"jiayuan4",u"贾源"],[u"jiayuan5",u"贾源"],[u"jiayuan6",u"贾源"],[u"jiayuan7",u"贾源"],[u"jiayue",u"贾越"],[u"jiayue1",u"贾越"],[u"jiazk",u"贾占凯"],[u"jiazk1",u"贾占凯"],[u"jiazl",u"贾竹林"],[u"jieqy",u"解庆艺"],[u"jifx",u"纪丰新"],[u"jifx1",u"纪丰新"],[u"jihm",u"季红梅"],[u"jilj",u"季灵君"],[u"jinggx",u"静国新"],[u"jinggx1",u"静国新"],[u"jingxf",u"景雪峰"],[u"jinhao",u"金浩"],[u"jinhl",u"金海兰"],[u"jinhl1",u"金海兰"],[u"jinkai",u"金恺"],[u"jinlh",u"金隆辉"],[u"jinliang",u"金亮"],[u"jinshuan",u"金拴"],[u"jinsw",u"金士伟"],[u"jinsw1",u"金士伟"],[u"jinyun",u"金芸"],[u"jiqiang",u"纪强"],[u"jjhadm",u"jjhadm"],[u"jjmyadm",u"jjmyadm"],[u"jjxadm",u"jjxadm"],[u"jltxadm",u"jltxadm"],[u"jmmadm",u"jmmadm"],[u"jn7166",u"陈雪梅"],[u"js258adm",u"js258adm"],[u"jsadm",u"jsadm"],[u"jsphadm",u"jsphadm"],[u"jsxcadmin",u"jsxcadmin"],[u"jsyfadm",u"jsyfadm"],[u"jujj",u"鞠佳静"],[u"jwtzadm",u"jwtzadm"],[u"jxjyadm",u"jxjyadm"],[u"jybdtzadmin",u"jybdtzadmin"],[u"jyqyadm",u"jyqyadm"],[u"jzhhcyadmin",u"jzhhcyadmin"],[u"jzkladm",u"jzkladm"],[u"kangdi",u"康迪"],[u"kangjh",u"亢景辉"],[u"kangjh1",u"亢景辉"],[u"km0326",u"袁丽萍"],[u"km292X",u"康小姝"],[u"kmrkadmin",u"kmrkadmin"],[u"kmybadm",u"kmybadm"],[u"kongbz",u"孔碧珍"],[u"kongrong",u"孔荣"],[u"kongrong1",u"孔荣"],[u"kongyf",u"孔亚峰"],[u"kuangliang",u"邝亮"],[u"langyn",u"郎亚男"],[u"lanxm",u"兰向美"],[u"lcadm",u"lcadm"],[u"lcgytzadmin",u"lcgytzadmin"],[u"ldxadm",u"ldxadm"],[u"leiguang",u"雷光"],[u"leijie",u"雷洁"],[u"leirui",u"雷睿"],[u"leirui1",u"雷睿"],[u"leirui2",u"雷睿"],[u"leiss",u"雷霜霜"],[u"leiss1",u"雷霜霜"],[u"leiyu",u"雷雨"],[u"leiyu1",u"雷雨"],[u"leiyu2",u"雷雨"],[u"leyh",u"乐映辉"],[u"lhsmadmin",u"lhsmadmin"],[u"lhyadm",u"lhyadm"],[u"liangjing",u"梁菁"],[u"liangjing1",u"梁菁"],[u"liangjing2",u"梁靖"],[u"liangjq",u"梁纪秋"],[u"liangjx",u"梁建霞"],[u"liangping",u"梁平"],[u"liangping1",u"梁平"],[u"liangww",u"梁伟文"],[u"liangying",u"梁影"],[u"liangying1",u"梁莹"],[u"liangying2",u"梁莹"],[u"lianyw",u"连永伟"],[u"lianyw1",u"连永伟"],[u"liaogj",u"廖国炬"],[u"liaogj1",u"廖国炬"],[u"liaoyl",u"廖银露"],[u"lias",u"李安顺"],[u"liay",u"李爱云"],[u"libj",u"李步剑"],[u"libm",u"李贝萌"],[u"licg",u"李春国"],[u"lich",u"李春红"],[u"lich3",u"李春红"],[u"lichang",u"李畅"],[u"lichang1",u"李畅"],[u"lichen",u"李臣"],[u"lichen1",u"李臣"],[u"lichen2",u"李臣"],[u"lichen3",u"李臣"],[u"lics",u"李成帅"],[u"licw",u"李成武"],[u"lidang",u"李宕"],[u"lidd",u"李丹丹"],[u"lidk",u"李多魁"],[u"lidm",u"李冬梅"],[u"lidong",u"李冬"],[u"lidong1",u"李冬"],[u"lidx",u"李德宣"],[u"lifei",u"李飞"],[u"lifeng",u"李峰"],[u"lifh",u"李凤华"],[u"lifh1",u"李芳慧"],[u"lifs",u"李方硕"],[u"lifs1",u"李方硕"],[u"lifx",u"李凤祥"],[u"lifx1",u"李凤祥"],[u"lifx2",u"李凤雪"],[u"ligang",u"李钢"],[u"ligen",u"李根"],[u"ligen1",u"李根"],[u"lihb",u"李会宾"],[u"lihe",u"李贺"],[u"lihe1",u"李贺"],[u"lihf",u"李恒飞"],[u"lihk",u"李宏坤"],[u"lihk1",u"李宏坤"],[u"lihm",u"李华敏"],[u"lihuan",u"李欢"],[u"lihui",u"李慧"],[u"lihui1",u"李慧"],[u"lihui2",u"李慧"],[u"lihui3",u"李慧"],[u"lihui4",u"李慧"],[u"lihui5",u"李徽"],[u"lihui6",u"李慧"],[u"lihx",u"李恒星"],[u"lihx1",u"李洪喜"],[u"lihz",u"李浩哲"],[u"lijf",u"黎军飞"],[u"lijg",u"栗建国"],[u"lijg1",u"栗建国"],[u"lijg2",u"栗建国"],[u"lijg3",u"栗建国"],[u"lijh",u"李静华"],[u"lijie",u"李婕"],[u"lijie1",u"李婕"],[u"lijing",u"李靖"],[u"lijing1",u"李京"],[u"lijing2",u"李京"],[u"lijing3",u"李静"],[u"lijj",u"李娇娇"],[u"lijj1",u"李晋江"],[u"lijj2",u"李晋江"],[u"lijj3",u"李娇娇"],[u"lijq",u"李嘉琪"],[u"lijs",u"李金姝"],[u"lijuan",u"李娟"],[u"lijw",u"李嘉威"],[u"lijx",u"李锦秀"],[u"likang",u"李康"],[u"likl",u"李昆林"],[u"lilin",u"李琳"],[u"lilin1",u"李琳"],[u"lilin4",u"李林"],[u"lilin5",u"李霖"],[u"liling",u"李玲"],[u"liling1",u"李玲"],[u"liliu",u"李柳"],[u"lilu",u"李露"],[u"limei",u"李梅"],[u"limeng",u"李猛"],[u"liming",u"李明"],[u"limj",u"李孟娇"],[u"limj1",u"李孟娇"],[u"limj2",u"李美军"],[u"limj3",u"李美军"],[u"limm",u"李敏敏"],[u"lina",u"李娜"],[u"lina1",u"李娜"],[u"lina2",u"李娜"],[u"lindj",u"林道静"],[u"lindj1",u"林道静"],[u"lingmin",u"凌敏"],[u"lingxn",u"凌学南"],[u"lingyd",u"凌远东"],[u"linhao",u"林浩"],[u"linhao1",u"林浩"],[u"linjh",u"林嘉惠"],[u"linjh1",u"林嘉惠"],[u"linly",u"林利燕"],[u"linrq",u"林瑞清"],[u"linsm",u"林思敏"],[u"linsm1",u"林思敏"],[u"lintq",u"林庭强"],[u"lintq1",u"林庭强"],[u"lintt",u"林婷婷"],[u"linxin",u"林鑫"],[u"linxiong",u"林雄"],[u"linyong",u"林勇"],[u"liping",u"李平"],[u"liping1",u"李平"],[u"lipo",u"李坡"],[u"lipo1",u"李坡"],[u"liqh",u"李庆贺"],[u"liqiang",u"李强"],[u"liqq",u"李清清"],[u"liqq1",u"李清清"],[u"liqy",u"李强燕"],[u"liqy1",u"李强燕"],[u"liqz",u"李奇智"],[u"lirui",u"李芮"],[u"lisa",u"李世安"],[u"lisen",u"李森"],[u"lishan",u"李杉"],[u"lishen",u"朝盈"],[u"lisj",u"大连旺泰"],[u"lisj1",u"李绍军"],[u"lisq",u"朝盈"],[u"lisr",u"李水荣"],[u"lisr1",u"李水荣"],[u"lisuo",u"李锁"],[u"litao",u"李涛"],[u"liting",u"李婷"],[u"liuap",u"刘爱平"],[u"liuaw",u"刘爱文"],[u"liubin",u"刘斌"],[u"liubin1",u"刘斌"],[u"liubin2",u"刘斌"],[u"liubin3",u"刘斌"],[u"liubin4",u"刘斌"],[u"liubj",u"刘保军"],[u"liubj1",u"刘保军"],[u"liuby",u"刘冰瑶"],[u"liuchao",u"刘超"],[u"liuchao1",u"刘潮"],[u"liucj",u"刘春杰"],[u"liucj1",u"刘春杰"],[u"liucj2",u"刘春杰"],[u"liucq",u"刘超群"],[u"liudan",u"刘丹"],[u"liudd",u"刘丹丹"],[u"liudm",u"刘冬明"],[u"liufc",u"刘福成"],[u"liugh",u"刘国华"],[u"liugz",u"刘广泽"],[u"liuhao",u"刘浩"],[u"liuhao1",u"刘浩"],[u"liuhao2",u"刘浩"],[u"liuhao3",u"刘浩"],[u"liuheng",u"刘恒"],[u"liuhh",u"刘欢欢"],[u"liuhh1",u"刘欢欢"],[u"liuht",u"刘海涛"],[u"liuht1",u"刘海涛"],[u"liuht2",u"刘海涛"],[u"liuht3",u"刘会涛"],[u"liuht4",u"刘海涛"],[u"liuhu",u"刘虎"],[u"liuhuan",u"刘欢"],[u"liuhy",u"刘红燕"],[u"liujc",u"刘建成"],[u"liujc1",u"刘建成"],[u"liujh",u"刘靖华"],[u"liujh1",u"刘靖华"],[u"liujia",u"刘嘉"],[u"liujia1",u"刘嘉"],[u"liujie",u"刘杰"],[u"liujie1",u"刘杰"],[u"liujie2",u"刘杰"],[u"liujie3",u"刘杰"],[u"liujie4",u"刘杰"],[u"liujie5",u"刘杰"],[u"liujq",u"刘建青"],[u"liujq1",u"刘建青"],[u"liujx",u"刘俊希"],[u"liujx1",u"刘俊希"],[u"liujx2",u"刘俊希"],[u"liujy",u"刘景岩"],[u"liujy1",u"刘景岩"],[u"liujy2",u"刘家园"],[u"liuke",u"刘珂"],[u"liule",u"刘乐"],[u"liulf",u"刘林风"],[u"liuli",u"刘利"],[u"liulq",u"刘浪其"],[u"liulu",u"刘璐"],[u"liulu1",u"刘璐"],[u"liuly",u"刘玲燕"],[u"liuly1",u"刘玲燕"],[u"liumg",u"刘明刚"],[u"liuming",u"刘明"],[u"liumm",u"刘明明"],[u"liumq",u"刘美青"],[u"liumq1",u"刘美青"],[u"liupan",u"刘攀"],[u"liupb",u"刘鹏波"],[u"liuqiang",u"刘强"],[u"liuqiang1",u"刘强"],[u"liuqq",u"刘倩倩"],[u"liuqy",u"刘清元"],[u"liuqy1",u"刘清元"],[u"liuqy2",u"刘清元"],[u"liuqy3",u"刘清元"],[u"liuqy4",u"刘清元"],[u"liushun",u"刘顺"],[u"liusj",u"刘四杰"],[u"liusn",u"刘胜男"],[u"liuss",u"刘珊珊"],[u"liuss1",u"刘珊珊"],[u"liust",u"刘书亭"],[u"liusy",u"刘燧银"],[u"liusy1",u"刘燧银"],[u"liusy2",u"刘思吟"],[u"liutao",u"刘涛"],[u"liutao1",u"刘涛"],[u"liutao2",u"刘涛"],[u"liutao3",u"刘涛"],[u"liutf",u"刘腾飞"],[u"liutf1",u"刘腾飞"],[u"liutong",u"刘彤"],[u"liutong1",u"刘彤"],[u"liuwei",u"刘伟"],[u"liuwj",u"刘文娟"],[u"liuwq",u"刘维岐"],[u"liuww",u"刘微微"],[u"liuwx",u"刘卫星"],[u"liuwz",u"刘文哲"],[u"liuxf",u"刘小凡"],[u"liuxf1",u"刘小凡"],[u"liuxh",u"刘小花"],[u"liuxin1",u"刘鑫"],[u"liuxin2",u"刘鑫"],[u"liuxing",u"刘行"],[u"liuxl",u"刘小龙"],[u"liuxq",u"刘晓清"],[u"liuxt",u"刘雪婷"],[u"liuxuan",u"刘旋"],[u"liuxz",u"刘学智"],[u"liuxz1",u"刘学智"],[u"liuyan6",u"刘焱"],[u"liuyang",u"刘洋"],[u"liuyang1",u"刘洋"],[u"liuyang2",u"刘洋"],[u"liuyang3",u"刘洋"],[u"liuyang4",u"刘洋"],[u"liuyang5",u"刘洋"],[u"liuyb",u"刘亚冰"],[u"liuyc",u"刘永常"],[u"liuyc1",u"刘永常"],[u"liuye",u"刘烨"],[u"liuye1",u"刘烨"],[u"liuyh",u"刘应虎"],[u"liuyj",u"刘玉洁"],[u"liuyq",u"刘应强"],[u"liuys",u"刘耀帅"],[u"liuyt",u"刘永涛"],[u"liuyu",u"刘宇"],[u"liuyx",u"刘云鑫"],[u"liuyx1",u"刘云鑫"],[u"liuyy",u"刘洋洋"],[u"liuyy1",u"刘瑶瑶"],[u"liuyz",u"刘玉珠"],[u"liuyz1",u"刘玉珠"],[u"liuzb",u"刘志斌"],[u"liuzd",u"刘振铎"],[u"liuzd1",u"刘振铎"],[u"liuzl",u"刘字玲"],[u"liuzl1",u"刘长龙"],[u"liuzm",u"刘志敏"],[u"liuzx",u"刘泽新"],[u"liuzx1",u"刘子旭"],[u"liwei",u"李伟"],[u"liwei1",u"李伟"],[u"liwp",u"李武平"],[u"lixb",u"李小贝"],[u"lixb1",u"李晓彬"],[u"lixd",u"李小东"],[u"lixd1",u"李小东"],[u"lixd2",u"李小东"],[u"lixi",u"李蹊"],[u"lixi1",u"李蹊"],[u"lixi2",u"李肸"],[u"lixj",u"李雪静"],[u"lixj1",u"李雪静"],[u"lixl",u"李小兰"],[u"lixl1",u"李小兰"],[u"lixl2",u"李晓丽"],[u"lixl3",u"李昔良"],[u"lixp",u"李显平"],[u"lixp1",u"李晓平"],[u"lixp2",u"李晓平"],[u"lixq",u"李晓芹"],[u"lixq1",u"李仙琦"],[u"lixq2",u"李仙琦"],[u"lixq3",u"李晓芹"],[u"lixu3",u"李旭"],[u"lixuan",u"黎宣"],[u"lixue",u"李雪"],[u"lixue1",u"李雪"],[u"lixx",u"李晓霞"],[u"lixx1",u"李晓霞"],[u"lixy",u"李肖云"],[u"liyan2",u"李艳"],[u"liyang",u"李阳"],[u"liyang1",u"李阳"],[u"liyc",u"李英超"],[u"liyc1",u"李英超"],[u"liyc2",u"李昀城"],[u"liyc3",u"李迎晨"],[u"liyd",u"李延东"],[u"liyd1",u"李延东"],[u"liyd2",u"李玉东"],[u"liyd3",u"李玉东"],[u"liying",u"李英"],[u"liying1",u"李影"],[u"liying2",u"李影"],[u"liying3",u"李瑛"],[u"liyj",u"李玉佳"],[u"liyl",u"李雁伦"],[u"liym",u"李奕民"],[u"liym1",u"李奕民"],[u"liym2",u"李奕民"],[u"liym3",u"李奕民"],[u"liyong",u"李涌"],[u"liyong1",u"李涌"],[u"liyong2",u"李勇"],[u"liyu1",u"李玉"],[u"liyuan",u"李媛"],[u"liyun",u"李赟"],[u"liyw",u"李玉伟"],[u"liyw1",u"李玉伟"],[u"liyy",u"李亚云"],[u"liyy1",u"李媛媛"],[u"liyz",u"李一洲"],[u"lizb",u"李增宝"],[u"lizb1",u"李智博"],[u"lizb2",u"李增宝"],[u"lizb3",u"李智博"],[u"lizf",u"李章福"],[u"lizf1",u"李章福"],[u"lizf2",u"李章福"],[u"lizf3",u"李章福"],[u"lizf4",u"李章福"],[u"lizf5",u"李章福"],[u"lizf6",u"李章福"],[u"lizf7",u"李章福"],[u"lizh",u"李哲海"],[u"lizh1",u"李仲慧"],[u"lizhe",u"李哲"],[u"lizhe1",u"李哲"],[u"lizl",u"李长领"],[u"lizl1",u"李长领"],[u"lizq",u"李智权"],[u"lizt",u"李智婷"],[u"lizt1",u"李智婷"],[u"lizw",u"李智伟"],[u"lizw1",u"李智伟"],[u"lizw2",u"李智伟"],[u"lizw3",u"李智伟"],[u"lnadm2",u"lnadm"],[u"lnhyadmin",u"lnhyadmin"],[u"longmeng",u"隆梦"],[u"longmeng1",u"隆梦"],[u"longqj",u"龙权军"],[u"longqj1",u"龙权军"],[u"longwei",u"龙伟"],[u"longwei1",u"龙伟"],[u"longwei2",u"龙伟"],[u"longwei3",u"龙伟"],[u"lpadm",u"lpadm"],[u"lrtzadmin",u"lrtzadmin"],[u"lu:hy",u"吕焕勇"],[u"lufy",u"鲁凤英"],[u"lufy1",u"鲁凤英"],[u"lufy2",u"鲁芳怡"],[u"luhs",u"卢宏硕"],[u"luhs1",u"卢宏硕"],[u"luhz",u"陆惠桢"],[u"luhz1",u"陆惠桢"],[u"lujing",u"卢静"],[u"lujun",u"卢军"],[u"lujun1",u"卢军"],[u"lujun2",u"卢军"],[u"lujun3",u"卢军"],[u"lujun4",u"陆军"],[u"luml",u"卢明隆"],[u"luocl",u"罗乘露"],[u"luocl1",u"罗乘露"],[u"luohy",u"罗鸿宇"],[u"luojh",u"罗建华"],[u"luojh1",u"罗建华"],[u"luojh2",u"罗建华"],[u"luojh3",u"罗建华"],[u"luold",u"罗丽达"],[u"luold1",u"罗丽达"],[u"luosb",u"洛神保"],[u"luoshan",u"罗山"],[u"luoshan1",u"罗山"],[u"luosl",u"罗尚龙"],[u"luowl",u"罗婉玲"],[u"luoxing",u"罗星"],[u"luoxing1",u"罗星"],[u"luozb",u"罗智彬"],[u"luozb1",u"罗智彬"],[u"lupeng",u"路鹏"],[u"lupeng1",u"路鹏"],[u"lusk",u"卢世康"],[u"lut",u"路婷"],[u"luxd",u"陆晓东"],[u"luxf",u"陆晓丰"],[u"luxf1",u"路晓峰"],[u"luxf2",u"路晓峰"],[u"luxun",u"卢洵"],[u"luyan",u"陆衍"],[u"luyan1",u"陆衍"],[u"luyh",u"卢燕红"],[u"luyh1",u"卢彦辉"],[u"luyj",u"陆亦君"],[u"lvdy",u"吕丹阳"],[u"lvdy1",u"吕丹阳"],[u"lvting",u"吕婷"],[u"lvxb",u"吕雪冰"],[u"lvxb1",u"吕雪冰"],[u"lvxb2",u"吕雪冰"],[u"lvxc",u"吕绪超"],[u"lvxc1",u"吕绪超"],[u"lxdadm",u"lxdadm"],[u"lyadm",u"lyadm"],[u"lygadadm",u"lygadadm"],[u"lymjadm",u"lymjadm"],[u"lz3468",u"尹义静"],[u"lzzdadmin",u"lzzdadmin"],[u"macc",u"马超超"],[u"mach",u"马朝惠"],[u"madf",u"马登峰"],[u"maff",u"马芳芳"],[u"mahf",u"马红芳"],[u"mahh",u"马浩鸿"],[u"mahz",u"马海贞"],[u"mahz1",u"马海贞"],[u"majia",u"马佳"],[u"majia1",u"马佳"],[u"majun",u"马骏"],[u"mamh",u"马明晧"],[u"mamy",u"马孟远"],[u"maoeq",u"毛恩强"],[u"maoqiang",u"毛强"],[u"maosb",u"毛世波"],[u"maoxh",u"毛翔辉"],[u"maoxl",u"毛星力"],[u"maozy",u"毛振宇"],[u"maqiang",u"马强"],[u"maql",u"马庆林"],[u"maqy",u"马秋亚"],[u"maqy1",u"马秋亚"],[u"masheng",u"马胜"],[u"masheng1",u"马胜"],[u"mateng",u"马腾"],[u"math",u"马天昊"],[u"matuo",u"马托"],[u"maxiao",u"马霄"],[u"maxr",u"马新荣"],[u"mazhen",u"马朕"],[u"mazj",u"马占军"],[u"mazj1",u"马占军"],[u"mazx",u"马长新"],[u"mccadm",u"mccadm"],[u"meixue",u"梅雪"],[u"mengdi",u"孟迪"],[u"mengdi1",u"孟迪"],[u"mengff",u"孟凡凤"],[u"menggen",u"孟根"],[u"mengguang",u"孟光"],[u"mengling",u"孟玲"],[u"mengmeng",u"孟梦"],[u"mengmy",u"孟美玉"],[u"mengqb",u"孟青宝"],[u"mengxiang",u"孟想"],[u"mengxiang1",u"孟想"],[u"mengym",u"孟勇明"],[u"mengze",u"孟泽"],[u"mengze1",u"孟泽"],[u"mengzx",u"孟忠晓"],[u"menhf",u"门慧芳"],[u"menmr",u"门茂荣"],[u"miaofy",u"苗方月"],[u"miaogl",u"苗国莉"],[u"miaoyz",u"苗永壮"],[u"miaoyz1",u"苗永壮"],[u"mina",u"米娜"],[u"mina1",u"米娜"],[u"mohd",u"莫华东"],[u"morf",u"莫仁发"],[u"mosl",u"莫诗莉"],[u"msbadm",u"msbadm"],[u"mujt",u"牧金婷"],[u"mutong",u"穆桐"],[u"nangx",u"南国祥"],[u"nangx1",u"南国祥"],[u"nanying",u"南颖"],[u"nanying1",u"南颖"],[u"nanying2",u"南颖"],[u"nanying3",u"南颖"],[u"ncdqadm",u"ncdqadm"],[u"neixin",u"那欣"],[u"nids",u"倪东升"],[u"niehr",u"聂华荣"],[u"niepf",u"聂鹏飞"],[u"nieql",u"聂青利"],[u"nieql1",u"聂青利"],[u"nieql2",u"聂青利"],[u"nieql3",u"聂青利"],[u"nierong",u"聂茸"],[u"nierong1",u"聂茸"],[u"nierong2",u"聂茸"],[u"nierong3",u"聂茸"],[u"niess",u"聂莎莎"],[u"niess1",u"聂莎莎"],[u"niess2",u"聂莎莎"],[u"niess3",u"聂莎莎"],[u"ninghl",u"宁慧琳"],[u"ningrui",u"宁锐"],[u"ningwei",u"宁伟"],[u"ningyl",u"宁耀龙"],[u"ningyl1",u"宁耀龙"],[u"niugx",u"牛桂祥"],[u"niugx1",u"牛桂祥"],[u"niujing",u"牛敬"],[u"niujing1",u"牛敬"],[u"niuping",u"牛平"],[u"niuqi",u"牛琪"],[u"niuqun",u"牛群"],[u"niuwj",u"牛皖军"],[u"niuying",u"牛莹"],[u"niuyj",u"牛勇炬"],[u"niuyp",u"牛银平"],[u"niuyp1",u"牛银平"],[u"niuyp2",u"牛银平"],[u"niuyp3",u"牛银平"],[u"nj0819",u"朱吉"],[u"nj1617",u"俞泽轩"],[u"nj2038",u"王辉"],[u"nj2248",u"张小培"],[u"nj2438",u"李磊"],[u"nj2633",u"潘文斌"],[u"nj3632",u"娄嵩"],[u"nj4214",u"袁飞"],[u"njlbsadmin",u"njlbsadmin"],[u"nn292X",u"康小姝"],[u"nnpxadmin",u"nnpxadmin"],[u"nnyhadmin",u"nnyhadmin"],[u"owdzadm",u"owdzadm"],[u"panglj",u"庞隆俊"],[u"panglj1",u"庞隆俊"],[u"pangsq",u"庞世强"],[u"pangsq1",u"庞世强"],[u"pangyy",u"庞营营"],[u"pangyy1",u"庞圆圆"],[u"panlei",u"潘雷"],[u"panqi",u"潘琪"],[u"panqi1",u"潘琪"],[u"panwb",u"潘文斌"],[u"panxc",u"潘学聪"],[u"panzh",u"潘志华"],[u"pdsrqadm",u"pdsrqadm"],[u"peijx",u"裴嘉兴"],[u"peiys",u"裴永社"],[u"peiyy",u"裴颖盈"],[u"peizz",u"裴长泽"],[u"pengbin",u"彭滨"],[u"pengbin1",u"彭滨"],[u"pengpj",u"彭丽娟"],[u"pengpj1",u"彭丽娟"],[u"pengqq",u"彭琦钦"],[u"pengqq1",u"彭琦钦"],[u"pengqq2",u"彭琦钦"],[u"pengyong",u"彭勇（武汉）"],[u"pingtcw",u"平台财务"],[u"pingtxsjl",u"平台销售经理"],[u"pingtxszj",u"平台销售总监"],[u"pingtyyry",u"平台运营人员"],[u"posgly",u"pos管理员"],[u"ptdadm",u"ptdadm"],[u"pzadm",u"pzadm"],[u"pzjadmin",u"pzjadmin"],[u"qdmyadm",u"qdmyadm"],[u"qianckf",u"千诚客服"],[u"qiangang",u"钱钢"],[u"qiangmy",u"强明阳"],[u"qiaoaz",u"乔奥哲"],[u"qiaomeng",u"乔梦"],[u"qijq",u"齐景泉"],[u"qijq1",u"齐景泉"],[u"qilryh",u"奇乐融用户"],[u"qingll",u"卿亮亮"],[u"qingll1",u"卿亮亮"],[u"qinhong",u"秦宏"],[u"qinjie",u"秦捷"],[u"qinqiao",u"秦俏"],[u"qinqiao1",u"秦俏"],[u"qinsi",u"秦思"],[u"qinww",u"秦唯唯"],[u"qinww1",u"秦唯唯"],[u"qinwy",u"秦玮钰"],[u"qinxw",u"秦小文"],[u"qinyan",u"秦岩"],[u"qinyan1",u"秦岩"],[u"qinyf",u"秦月芬"],[u"qinyy",u"秦妍妍"],[u"qinzb",u"秦志斌"],[u"qinzf",u"秦志凤"],[u"qinzz",u"秦振中"],[u"qinzz1",u"秦振中"],[u"qiuchen",u"邱晨"],[u"qiuchen1",u"邱晨"],[u"qiuhm",u"邱海明"],[u"qiujx",u"邱建新"],[u"qiujx1",u"邱建新"],[u"qiushi",u"邱石"],[u"qiushi1",u"邱石"],[u"qiushuang",u"邱爽"],[u"qiycf",u"起源财富"],[u"qiyh",u"齐艳辉"],[u"qiyh1",u"齐艳辉"],[u"qjxdyadmin",u"qjxdyadmin"],[u"quanwei",u"权威"],[u"quanyi",u"全毅"],[u"quhf",u"屈浩锋"],[u"qumy",u"屈美英"],[u"qumy1",u"屈美英"],[u"qyfadm",u"qyfadm"],[u"ranmn",u"冉茂楠"],[u"ranmn1",u"冉茂楠"],[u"ranmn2",u"冉茂楠"],[u"ranpeng",u"惠付科技"],[u"renjun",u"任俊"],[u"renshe",u"任涉"],[u"renty",u"任天源"],[u"renyan",u"任燕"],[u"renyp",u"任远鹏"],[u"renyy",u"任艳颖"],[u"renyy1",u"任艳颖"],[u"renzh",u"任志寒"],[u"rjtzadmin",u"rjtzadmin"],[u"ronghao",u"荣昊"],[u"ronghao1",u"荣昊"],[u"rongxy",u"荣小跃"],[u"rongxy1",u"荣小跃"],[u"rtqcadm",u"rtqcadm"],[u"ruanlb",u"阮立班"],[u"ruanlf",u"阮力奋"],[u"ruanlf1",u"阮力奋"],[u"ruanxy",u"阮雪玉"],[u"rytzadmin",u"rytzadmin"],[u"scshadm",u"scshadm"],[u"scyxadm",u"scyxadm"],[u"sdwaadm",u"sdwaadm"],[u"sgmadm",u"sgmadm"],[u"sh3468",u"尹义静"],[u"shamc",u"沙明春"],[u"shangchong",u"尚冲"],[u"shangchong1",u"尚冲"],[u"shangqq",u"尚倩倩"],[u"shangsj",u"尚树俊"],[u"shangtt",u"无"],[u"shangyd",u"尚亚东"],[u"shangyf",u"尚亚芳"],[u"shangyong",u"尚勇"],[u"shangyq",u"尚雅倩"],[u"shangyq1",u"尚雅倩"],[u"shaoby",u"邵博宇"],[u"shaodi",u"邵迪"],[u"shaomo",u"邵默"],[u"shaomo1",u"邵默"],[u"shaoxl",u"邵晓龙"],[u"shaoxl1",u"邵晓龙"],[u"shaozx",u"邵长雪"],[u"sharh",u"沙瑞华"],[u"sharh1",u"沙瑞华"],[u"sharh2",u"沙瑞华"],[u"sharh3",u"沙瑞华"],[u"shengliang",u"笙亮"],[u"shengm",u"申光明"],[u"shengm1",u"申光明"],[u"shengsy",u"盛诗雅"],[u"shengye",u"盛野"],[u"shengye1",u"盛野"],[u"shengye2",u"盛野"],[u"shengye3",u"盛野"],[u"shenjie",u"沈杰"],[u"shenjj",u"沈俭军"],[u"shenjr",u"沈金荣"],[u"shenli",u"沈莉"],[u"shenling",u"沈伶"],[u"shenqh",u"沈琼华"],[u"shenst",u"沈淑婷"],[u"shenzj",u"沈正军"],[u"shenzj1",u"沈长军"],[u"shewq",u"佘五七"],[u"shicheng",u"史秤"],[u"shicj",u"施崇军"],[u"shicj1",u"施崇军"],[u"shicy",u"石存燕"],[u"shihh",u"史海华"],[u"shiwc",u"施宛辰"],[u"shiwc1",u"施宛辰"],[u"shixia",u"史霞"],[u"shixia1",u"史霞"],[u"shixia2",u"史霞"],[u"shixia3",u"史霞"],[u"shixl",u"史晓琳"],[u"shixy",u"施晓宇"],[u"shiyl",u"时艳丽"],[u"shiyq",u"施亚琴"],[u"shqwadmin",u"shqwadmin"],[u"sijia",u"司嘉"],[u"songchen",u"宋晨"],[u"songdan",u"宋丹"],[u"songdan1",u"宋丹"],[u"songdan2",u"宋丹"],[u"songdan3",u"宋丹"],[u"songduo",u"宋铎"],[u"songjb",u"宋佳宾"],[u"songjf",u"宋竞飞"],[u"songlt",u"宋龙涛"],[u"songmg",u"宋明桂"],[u"songmin",u"宋敏"],[u"songmin1",u"宋敏"],[u"songmin2",u"宋敏"],[u"songmin3",u"宋敏"],[u"songmin4",u"宋敏"],[u"songmin5",u"宋敏"],[u"songmy",u"宋明颖"],[u"songmy1",u"宋明颖"],[u"songwei",u"宋伟"],[u"songwp",u"宋伟鹏"],[u"songxc",u"宋晓晨"],[u"songyang",u"宋阳"],[u"songyang1",u"宋阳"],[u"songyf",u"宋亚范"],[u"songyf1",u"宋亚范"],[u"spbadm",u"spbadm"],[u"sqrsadm",u"sqrsadm"],[u"sqwyadm",u"sqwyadm"],[u"ssjadm",u"ssjadm"],[u"ssmyadm",u"ssmyadm"],[u"suec",u"苏尔岑"],[u"sufeng",u"苏峰"],[u"suhl",u"苏衡丽"],[u"sulei",u"苏磊"],[u"sunan",u"苏楠"],[u"sunbin",u"孙斌"],[u"suncf",u"孙春芳"],[u"suncf1",u"孙春芳"],[u"sundr",u"孙德荣"],[u"sundr1",u"孙德荣"],[u"sunfeng",u"孙峰"],[u"sunff",u"孙菲菲"],[u"sungh",u"孙光虹"],[u"sungq",u"孙刚乾"],[u"sungq1",u"孙刚乾"],[u"sunhb",u"孙海滨"],[u"sunhb1",u"孙海滨"],[u"sunhb2",u"孙海滨"],[u"sunhb3",u"孙海滨"],[u"sunhc",u"孙海超"],[u"sunkun",u"孙坤"],[u"sunlm",u"孙丽敏"],[u"sunme",u"孙蒙恩"],[u"sunmj",u"孙明杰"],[u"sunpb",u"孙平波"],[u"sunqi",u"孙祺"],[u"sunqi1",u"孙祺"],[u"sunwei",u"孙微"],[u"sunwei1",u"孙微"],[u"sunxs",u"孙许帅"],[u"sunxun",u"孙逊"],[u"sunyang",u"孙杨"],[u"sunyang1",u"孙扬"],[u"sunyi",u"孙一"],[u"sunyi1",u"孙一"],[u"sunyu",u"孙宇"],[u"sunyu1",u"孙宇"],[u"sunzd",u"孙志东"],[u"sunzh",u"孙振华"],[u"sunzj",u"孙中菊"],[u"sunzj1",u"孙中菊"],[u"suobd",u"索秉铎"],[u"suobd1",u"索秉铎"],[u"suqy",u"苏庆亚"],[u"suqy1",u"苏庆亚"],[u"suss",u"苏硕硕"],[u"suxuan",u"粟炫"],[u"swadm",u"swadm"],[u"sy292X",u"康小姝"],[u"sz2825",u"储玲玲"],[u"szaycadmin",u"szaycadmin"],[u"szgrhtadmin",u"szgrhtadmin"],[u"szjyxadmin",u"szjyxadmin"],[u"szltsadmin",u"szltsadmin"],[u"szxtfadmin",u"szxtfadmin"],[u"szxyxadm",u"szxyxadm"],[u"szyfadm",u"szyfadm"],[u"szywladm",u"szywladm"],[u"szywxxadmin",u"szywxxadmin"],[u"tancy",u"谭春媛"],[u"tangcc",u"唐超超"],[u"tanghw",u"唐怀文"],[u"tangjm",u"唐金梅"],[u"tangju",u"汤菊"],[u"tangju1",u"汤菊"],[u"tangju2",u"汤菊"],[u"tangju3",u"汤菊"],[u"tanglu",u"唐璐"],[u"tangwei",u"唐伟"],[u"tangwei1",u"唐伟"],[u"tangwen",u"汤雯"],[u"tangxy",u"汤兴宇"],[u"tangxy1",u"汤兴宇"],[u"tangyj",u"唐勇军"],[u"tangym",u"唐玉梅"],[u"tangyun",u"唐云"],[u"tangyw",u"汤扬威"],[u"tangzheng",u"汤正"],[u"tanhz",u"覃汉周"],[u"tanjian",u"覃健"],[u"tanjw",u"覃继往"],[u"tankx",u"谈开仙"],[u"tankx1",u"谈开仙"],[u"tankx2",u"谈开仙"],[u"tanlu",u"谭璐"],[u"tanlu1",u"谭璐"],[u"tanxl",u"覃小玲"],[u"tanxm",u"谭小妹"],[u"tanyf",u"覃业锋"],[u"tanyx",u"覃云祥"],[u"tanzy",u"檀正艺"],[u"taojh",u"陶佳慧"],[u"taomh",u"陶明浩"],[u"taosl",u"陶姝琳"],[u"taosl1",u"陶姝琳"],[u"taoyi",u"陶毅"],[u"taoyj",u"陶叶静"],[u"tenglong",u"滕龙"],[u"tenglong1",u"滕龙"],[u"tianjie",u"田洁"],[u"tianjing",u"田静"],[u"tiankai",u"田凯"],[u"tianyh",u"田跃华"],[u"tianzf",u"田志凤"],[u"tianzg",u"田志刚"],[u"tianzw",u"田志舞"],[u"tj0015",u"王东"],[u"tongji",u"统计"],[u"tongzd",u"佟振冬"],[u"tongzw",u"仝芷玮"],[u"tuqing",u"屠青"],[u"tzgcadm",u"tzgcadm"],[u"tzjszadmin",u"tzjszadmin"],[u"tzkyadmin",u"tzkyadmin"],[u"wangbo",u"王博"],[u"wangbo1",u"王博"],[u"wangbo2",u"王博"],[u"wangbq",u"王卜勤"],[u"wangcf",u"王超峰"],[u"wangch",u"王晨晖"],[u"wangchuan",u"王川"],[u"wangcj",u"王成娟"],[u"wangcl",u"王春玲"],[u"wangcl1",u"王春玲"],[u"wangcl2",u"王春雷"],[u"wangcl3",u"王春雷"],[u"wangcy",u"汪彩艳"],[u"wangcy1",u"汪彩艳"],[u"wangcy2",u"王呈云"],[u"wangcy3",u"王呈云"],[u"wangcy4",u"王川野"],[u"wangdd",u"王丹丹"],[u"wangdn",u"王段娜"],[u"wangfang",u"王芳"],[u"wangfl",u"王福龙"],[u"wanggang",u"王刚"],[u"wanggang1",u"王刚"],[u"wanggang2",u"王刚"],[u"wanggang3",u"王刚"],[u"wanghb",u"王怀波"],[u"wanghb1",u"王怀波"],[u"wanghl",u"王海龙"],[u"wanghl1",u"王海龙"],[u"wanghl2",u"王海龙"],[u"wanghuan",u"王焕"],[u"wanghui",u"王徽"],[u"wanghui1",u"王会"],[u"wanghui2",u"王慧"],[u"wanghw",u"王洪伍"],[u"wanghw1",u"王洪伍"],[u"wanghw2",u"王洪伍"],[u"wanghw3",u"王洪伍"],[u"wanghy",u"王鸿雁"],[u"wangjc",u"王君程"],[u"wangjc1",u"王君程"],[u"wangjd",u"王冀东"],[u"wangje",u"王金娥"],[u"wangje1",u"王金娥"],[u"wangjian",u"王健"],[u"wangjian1",u"王健"],[u"wangjian2",u"王健"],[u"wangjiao",u"王娇"],[u"wangjie",u"王杰"],[u"wangjie1",u"王杰"],[u"wangjing",u"王晶"],[u"wangjing1",u"王晶"],[u"wangjing2",u"王静"],[u"wangjing3",u"王静"],[u"wangjj",u"王姣姣"],[u"wangjl",u"王金磊"],[u"wangjl1",u"王金磊"],[u"wangjp",u"王建鹏"],[u"wangjp1",u"王军朋"],[u"wangjp2",u"王建鹏"],[u"wangjs",u"王金栓"],[u"wangjun",u"王俊"],[u"wangjun1",u"王军"],[u"wangjun2",u"王军"],[u"wangjx",u"王金鑫"],[u"wangjx1",u"王金鑫"],[u"wangjz",u"王俭忠"],[u"wangjz1",u"王俭忠"],[u"wangkang",u"王康"],[u"wangkang1",u"王康"],[u"wangkl",u"王克玲"],[u"wangkl1",u"王克玲"],[u"wanglan",u"王兰"],[u"wanglei",u"王磊"],[u"wanglei1",u"王磊"],[u"wanglei2",u"王磊"],[u"wanglei3",u"王雷"],[u"wanglei4",u"王磊"],[u"wanglei5",u"王雷"],[u"wanglh",u"王莲红"],[u"wanglh1",u"王连合"],[u"wangliang",u"汪亮"],[u"wanglin",u"王林"],[u"wangling",u"王玲"],[u"wangling1",u"王玲"],[u"wanglj",u"王丽娟"],[u"wanglj1",u"王丽娟"],[u"wangll",u"王黎黎"],[u"wanglong",u"王龙"],[u"wanglong1",u"王龙"],[u"wanglong2",u"王龙"],[u"wanglong3",u"王龙"],[u"wanglu",u"王露"],[u"wanglx",u"王立学"],[u"wanglx1",u"王立学"],[u"wanglx2",u"王立新"],[u"wanglx3",u"王立新"],[u"wangming",u"丹东美翔"],[u"wangmm",u"王茂民"],[u"wangmx",u"王敏霞"],[u"wangmy",u"王梦雅"],[u"wangpeng",u"王鹏"],[u"wangpu",u"王璞"],[u"wangqiang",u"王强"],[u"wangqing",u"王晴"],[u"wangqj",u"王秋菊"],[u"wangql",u"王庆玲"],[u"wangqm",u"王秋梅"],[u"wangqs",u"王秋硕"],[u"wangqy",u"王巧玉"],[u"wangqz",u"王全中"],[u"wangrb",u"王荣彬"],[u"wangrh",u"王若海"],[u"wangrh1",u"王汝豪"],[u"wangs",u"王双"],[u"wangss",u"王顺顺"],[u"wangss1",u"王顺顺"],[u"wangss2",u"王双双"],[u"wangss3",u"王双双"],[u"wangsy",u"王世勇"],[u"wangsy1",u"王世勇"],[u"wangtao",u"王涛"],[u"wangtao1",u"王涛"],[u"wangtao2",u"王涛"],[u"wangting",u"王婷"],[u"wangting1",u"王婷"],[u"wangts",u"王天时"],[u"wangtt",u"王婷婷"],[u"wangtt1",u"王婷婷"],[u"wangwb",u"王文博"],[u"wangwb1",u"王文博"],[u"wangwc",u"王伟才"],[u"wangwei",u"王薇"],[u"wangwj",u"王文娟"],[u"wangwj1",u"王文娟"],[u"wangwj2",u"王唯嘉"],[u"wangwj3",u"王唯嘉"],[u"wangwj4",u"王文娟"],[u"wangwj5",u"王文娟"],[u"wangwl",u"王文龙"],[u"wangwl1",u"王文龙"],[u"wangwl2",u"王文磊"],[u"wangwl3",u"王文磊"],[u"wangwz",u"王汪哲"],[u"wangxd",u"王旭东"],[u"wangxd1",u"王旭东"],[u"wangxg",u"王新贵"],[u"wangxg1",u"王新贵"],[u"wangxg2",u"王新贵"],[u"wangxg3",u"王新贵"],[u"wangxg4",u"王新贵"],[u"wangxg5",u"王新贵"],[u"wangxg6",u"王新贵"],[u"wangxg7",u"王新贵"],[u"wangxh",u"王兴海"],[u"wangxi4",u"王稀"],[u"wangxi5",u"王曦"],[u"wangxin",u"王欣"],[u"wangxin2",u"王欣"],[u"wangxing",u"王兴"],[u"wangxing1",u"王兴"],[u"wangxj",u"王雪静"],[u"wangxj1",u"王雪静"],[u"wangxj2",u"王兴杰"],[u"wangxj3",u"王兴杰"],[u"wangxj4",u"王兴杰"],[u"wangxl",u"王晓丽"],[u"wangxl1",u"王晓蕾"],[u"wangxl2",u"王晓蕾"],[u"wangxl3",u"汪相立"],[u"wangxm",u"王兴梅"],[u"wangxr",u"王希仁"],[u"wangxr1",u"王希仁"],[u"wangxs",u"王晓双"],[u"wangxt",u"华商"],[u"wangxt1",u"王雪婷"],[u"wangxun",u"王迅"],[u"wangxun1",u"王讯"],[u"wangxx",u"王新霞"],[u"wangxy",u"王鑫禹"],[u"wangyan2",u"王岩"],[u"wangyang",u"王洋"],[u"wangyang1",u"王阳"],[u"wangyb",u"王颖博"],[u"wangyb1",u"王颖博"],[u"wangyc",u"王艳昌"],[u"wangyc1",u"王颖超"],[u"wangyc2",u"王艳昌"],[u"wangye",u"王晔"],[u"wangyf",u"王依帆"],[u"wangyf1",u"王依帆"],[u"wangying",u"王影"],[u"wangying1",u"王迎"],[u"wangyj",u"王艳杰"],[u"wangyj1",u"王艳杰"],[u"wangyj2",u"王婴杰"],[u"wangyj3",u"王艳杰"],[u"wangyj4",u"王亚杰"],[u"wangyl",u"王姚丽"],[u"wangyl1",u"王亚丽"],[u"wangym",u"王焰蒙"],[u"wangyong",u"王勇"],[u"wangyong1",u"王勇"],[u"wangyong2",u"王勇"],[u"wangyp",u"王燕平"],[u"wangyq",u"王漪清"],[u"wangyq1",u"王云勤"],[u"wangyq2",u"王云勤"],[u"wangyq3",u"王云勤"],[u"wangyq5",u"王云勤"],[u"wangys",u"王元帅"],[u"wangyt",u"王翼天"],[u"wangyu",u"王裕"],[u"wangyu2",u"王玉"],[u"wangyue",u"王悦"],[u"wangyx",u"王怡心"],[u"wangyy",u"王瑛瑛"],[u"wangyy1",u"王瑛瑛"],[u"wangyy2",u"王瑛瑛"],[u"wangyy3",u"王瑛瑛"],[u"wangzg",u"王志刚"],[u"wangzg1",u"王治国"],[u"wangzg2",u"王治国"],[u"wangzg3",u"王之国"],[u"wangzg4",u"王之国"],[u"wangzhuang",u"王壮"],[u"wangzi",u"王梓"],[u"wangzl",u"王志玲"],[u"wangzl1",u"王子亮"],[u"wangzq",u"王自强"],[u"wangzq1",u"王自强"],[u"wangzw",u"王志伟"],[u"wangzx",u"王泽祥"],[u"wangzx1",u"王泽祥"],[u"wangzx2",u"王子绪"],[u"wangzy",u"王政一"],[u"wangzy1",u"王佐翼"],[u"wanjf",u"万俊峰"],[u"wanjuan",u"万娟"],[u"wanjuan1",u"万娟"],[u"wanjuan2",u"万娟"],[u"wanjuan3",u"万娟"],[u"wanjy",u"万金玉"],[u"wanjy1",u"万金玉"],[u"wantao",u"万涛"],[u"wantao1",u"万涛"],[u"wanxm",u"万雪梅"],[u"wanyi",u"万毅"],[u"wanyong",u"万勇"],[u"wanyong1",u"万勇"],[u"wbwladm",u"wbwladm"],[u"weicl",u"韦春兰"],[u"weieg",u"魏恩广"],[u"weifc",u"韦凤春"],[u"weihx",u"韦虹旭"],[u"weijin",u"魏进"],[u"weikj",u"魏凯杰"],[u"weikj1",u"魏凯杰"],[u"weiling",u"韦领"],[u"weixf",u"韦晓飞"],[u"weixin",u"魏欣"],[u"weixin1",u"魏欣"],[u"weiyl",u"魏云雷"],[u"weiyuan",u"魏源"],[u"weiyuan1",u"魏源"],[u"wenggh",u"翁官华"],[u"wengxx",u"翁星星"],[u"wenjp",u"文江平"],[u"wenmj",u"文孟君"],[u"wenmj1",u"文孟君"],[u"wg0011",u"肖毅"],[u"wg0013",u"张志恒"],[u"wg0015",u"张烜东"],[u"wg0016",u"马振顺"],[u"wg0017",u"陈金鑫"],[u"wg0019",u"陈元鸿"],[u"wg0025",u"丁晓梅"],[u"wg0029",u"孙甜甜"],[u"wg0034",u"黄羿翔"],[u"wg0040",u"林雪梅"],[u"wg0046",u"马晓燕"],[u"wg0081",u"吴君"],[u"wg0089",u"雷淑惠"],[u"wg0114",u"任锦星"],[u"wg0326",u"朱云红"],[u"wg0328",u"完敏"],[u"wg0460",u"伊兰"],[u"wg0521",u"丁杨"],[u"wg0820",u"李京瑞"],[u"wg1147",u"杨政冉"],[u"wg1326",u"岳秋月"],[u"wg1421",u"邓欣"],[u"wg1523",u"骆永华"],[u"wg1548",u"吕瑾晖"],[u"wg1629",u"杨彦"],[u"wg1749",u"陈凌波"],[u"wg1823",u"刘倩"],[u"wg1826",u"曹威威"],[u"wg1829",u"徐亚男"],[u"wg1841",u"岳秋月"],[u"wg1848",u"孙明艳"],[u"wg2018",u"张金金"],[u"wg2264",u"黄露"],[u"wg2325",u"夏凡"],[u"wg2415",u"白晋"],[u"wg2460",u"顾述翠"],[u"wg2610",u"王康程"],[u"wg2733",u"李睿"],[u"wg2761",u"黄天珍"],[u"wg3211",u"孟庆岩"],[u"wg3226",u"罗晓南"],[u"wg332X",u"谢玉敏"],[u"wg4023",u"秦霞"],[u"wg4716",u"付增升"],[u"wg5140",u"刘洋阳"],[u"wg5217",u"杨海东"],[u"wg5221",u"程霞"],[u"wg5387",u"王晓平"],[u"wg5464",u"杨芬"],[u"wg5519",u"张金龙"],[u"wg5714",u"荣胜松"],[u"wg581X",u"徐朋恩"],[u"wg6028",u"马海红"],[u"wg6433",u"朱学勤"],[u"wg6821",u"徐慧玲"],[u"wg7038",u"陈玉海"],[u"wg7108",u"徐丹凤"],[u"wg9020",u"李丽"],[u"whhladm",u"whhladm"],[u"whrgadm",u"whrgadm"],[u"whxhadm",u"whxhadm"],[u"wljcadm",u"wljcadm"],[u"wrcfadm",u"wrcfadm"],[u"wucheng",u"吴成"],[u"wucj",u"吴从建"],[u"wucx",u"吴春晓"],[u"wugm",u"吴广猛"],[u"wugm1",u"吴广猛"],[u"wuhao",u"吴皓"],[u"wuheng",u"吴恒"],[u"wuheng1",u"吴恒"],[u"wujh",u"伍江和"],[u"wujm",u"乌洁敏"],[u"wujm1",u"武金忙"],[u"wujm2",u"武金忙"],[u"wulei",u"吴磊"],[u"wuliang",u"吴亮"],[u"wuling",u"东源投资"],[u"wumeng",u"吴猛"],[u"wumx",u"吴美霞"],[u"wumx1",u"吴美霞"],[u"wupei",u"吴佩"],[u"wuqiang",u"吴强"],[u"wuqiang1",u"吴强"],[u"wuqiang2",u"吴强"],[u"wuqiong",u"吴琼"],[u"wusong",u"吴松"],[u"wuss",u"武树森"],[u"wutao",u"吴涛"],[u"wutao1",u"吴涛"],[u"wuting",u"吴婷"],[u"wutl",u"吴天龙"],[u"wuwei",u"吴为"],[u"wuwei1",u"吴为"],[u"wuxb",u"邬肖玢"],[u"wuxf",u"吴晓峰"],[u"wuxf1",u"吴晓峰"],[u"wuxl",u"吴秀领"],[u"wuxl1",u"吴秀领"],[u"wuxn",u"武晓妮"],[u"wuxy",u"吴晓勇"],[u"wuyf",u"巫勇帆"],[u"wuyj",u"巫玉洁"],[u"wuym",u"吴源明"],[u"wuzj",u"伍长敬"],[u"wuzs",u"伍长胜"],[u"wuzx",u"武振星"],[u"wxldadm",u"wxldadm"],[u"wxrgadmin",u"wxrgadmin"],[u"wxsmadm",u"wxsmadm"],[u"wxtladmin",u"wxtladmin"],[u"wxxadm2",u"wxxadm"],[u"wz0448",u"方茹"],[u"wz1025",u"屈美英"],[u"wz162X",u"陈冲"],[u"wz2826",u"韩盈盈"],[u"wz3039",u"李博文"],[u"wz4817",u"王栋"],[u"wz4822",u"刘洁"],[u"xagtadmin",u"xagtadmin"],[u"xcbfadm",u"xcbfadm"],[u"xcfadm",u"xcfadm"],[u"xclkadm",u"xclkadm"],[u"xcsmadm",u"xcsmadm"],[u"xcthadm",u"xcthadm"],[u"xdjadm",u"xdjadm"],[u"xfyadmin",u"xfyadmin"],[u"xi2248",u"张小培"],[u"xiajx",u"夏建雄"],[u"xiak",u"夏琨"],[u"xiakun",u"夏琨"],[u"xiakun1",u"夏琨"],[u"xiakun2",u"夏琨"],[u"xiakun3",u"夏琨"],[u"xialei",u"夏磊"],[u"xiamy",u"夏敏怡"],[u"xiamy1",u"夏敏怡"],[u"xiangjf",u"项峻峰"],[u"xiangqx",u"向秋霞"],[u"xiangyi",u"向毅"],[u"xiaoaj",u"肖爱娇"],[u"xiaoaj1",u"肖爱娇"],[u"xiaodi",u"肖迪"],[u"xiaogf",u"肖观发"],[u"xiaohua",u"肖华"],[u"xiaohua1",u"肖华"],[u"xiaohua2",u"肖华"],[u"xiaolh",u"肖里寒"],[u"xiaolh1",u"肖里寒"],[u"xiaolj",u"肖理娟"],[u"xiaomin",u"肖敏"],[u"xiaoqi",u"肖琦"],[u"xiaoxia",u"肖霞"],[u"xiaoxia1",u"肖霞"],[u"xiaozw",u"肖占武"],[u"xiasm",u"夏松梅"],[u"xiasm1",u"夏松梅"],[u"xiayb",u"夏元博"],[u"xiefang",u"谢芳"],[u"xiegl",u"谢国磊"],[u"xiejl",u"布鲁诺"],[u"xiejun",u"谢骏"],[u"xiejy",u"谢钧悦"],[u"xieli",u"谢立"],[u"xiewei",u"谢威"],[u"xiexiong",u"谢雄"],[u"xieym",u"谢一鸣"],[u"xinghsy",u"星湖试用"],[u"xingrong",u"邢荣"],[u"xingrong1",u"邢荣"],[u"xingzj",u"刑占江"],[u"xiongjq",u"熊建强"],[u"xiongjq1",u"熊建强"],[u"xiongjq2",u"熊建强"],[u"xiongjq3",u"熊建强"],[u"xionglei",u"熊磊"],[u"xiongll",u"熊林林"],[u"xiuln",u"修莉男"],[u"xlsmadmin",u"xlsmadmin"],[u"xmydadm",u"xmydadm"],[u"xswladmin",u"xswladmin"],[u"xubin",u"徐斌"],[u"xubin1",u"徐斌"],[u"xudy",u"许东月"],[u"xuebai",u"薛白"],[u"xuebai1",u"薛白"],[u"xuebai2",u"薛白"],[u"xuebai3",u"薛白"],[u"xuemh",u"薛敏华"],[u"xuexf",u"薛小飞"],[u"xuexl",u"薛孝雷"],[u"xueying",u"薛瀛"],[u"xueyuan",u"薛媛"],[u"xuezf",u"薛长富"],[u"xuhang",u"许航"],[u"xuhui",u"徐辉"],[u"xujian",u"徐键"],[u"xujian1",u"徐键"],[u"xujj",u"徐晶晶"],[u"xujj1",u"徐晶晶"],[u"xujl",u"润银投资"],[u"xujz",u"许加桢"],[u"xulc",u"徐俐晨"],[u"xule",u"徐乐"],[u"xulei",u"徐磊"],[u"xulin",u"徐林"],[u"xulin1",u"徐林"],[u"xumin",u"许敏"],[u"xumin1",u"许敏"],[u"xunmc",u"寻明初"],[u"xupp",u"徐培培"],[u"xuqing",u"徐庆"],[u"xuwei",u"徐维"],[u"xuwm",u"徐文明"],[u"xuww",u"徐伟伟"],[u"xuxin",u"徐鑫"],[u"xuxj",u"许小军"],[u"xuxj1",u"许小军"],[u"xuyn",u"徐杨楠"],[u"xuyn1",u"徐英男"],[u"xuyy",u"许杨洋"],[u"xuzg",u"许铮光"],[u"xuzn",u"徐子宁"],[u"xuzy",u"徐泽誉"],[u"xxdadm",u"xxdadm"],[u"xxqmadm",u"xxqmadm"],[u"xykladm",u"xykladm"],[u"xyxyxadm",u"xyxyxadm"],[u"xzbxadm",u"xzbxadm"],[u"yalei",u"亚磊"],[u"yangbo",u"杨柏"],[u"yangcc",u"杨昌春"],[u"yangch1",u"杨聪慧"],[u"yangch2",u"杨聪慧"],[u"yangch3",u"杨聪慧"],[u"yangch4",u"杨聪慧"],[u"yangchuan",u"杨川"],[u"yangds",u"杨大帅"],[u"yangdy",u"杨东阳"],[u"yangfei",u"杨飞"],[u"yangfei1",u"杨飞"],[u"yanggang",u"杨钢"],[u"yanggf",u"杨歌菲"],[u"yanggf1",u"杨歌菲"],[u"yanggs",u"杨国栓"],[u"yanggs1",u"杨国栓"],[u"yangguang",u"杨广"],[u"yangguang1",u"杨光"],[u"yanggy",u"杨广耀"],[u"yanggy1",u"杨广耀"],[u"yanghm",u"杨慧萌"],[u"yanghm1",u"杨慧萌"],[u"yanghs",u"杨慧生"],[u"yangjf",u"杨俊锋"],[u"yangjian",u"杨建"],[u"yangjian1",u"杨建"],[u"yangjian2",u"杨键"],[u"yangjian3",u"杨键"],[u"yangjian4",u"杨键"],[u"yangjing",u"杨婧"],[u"yangjx",u"杨家祥"],[u"yanglb",u"杨乐斌"],[u"yangli",u"杨丽"],[u"yangll",u"杨乐乐"],[u"yangll1",u"杨乐乐"],[u"yanglu",u"杨路"],[u"yangmeng",u"杨萌"],[u"yangmeng1",u"杨萌"],[u"yangmin",u"杨敏"],[u"yangpp",u"杨盼盼"],[u"yangrui",u"杨蕊"],[u"yangsf",u"杨思菲"],[u"yangss",u"杨莎莎"],[u"yangss1",u"杨莎莎"],[u"yangss2",u"杨书生"],[u"yangting",u"杨婷"],[u"yangwei",u"杨伟"],[u"yangwei1",u"杨伟"],[u"yangwei2",u"杨伟"],[u"yangwei4",u"杨伟"],[u"yangxb",u"杨晓滨"],[u"yangxh",u"杨先欢"],[u"yangxj",u"杨晓娇"],[u"yangxj1",u"杨晓娇"],[u"yangxj2",u"杨胥君"],[u"yangxue",u"杨雪"],[u"yangxue1",u"杨雪"],[u"yangxy",u"杨兴媛"],[u"yangyang",u"杨杨"],[u"yangyang1",u"杨旸"],[u"yangyang2",u"杨旸"],[u"yangyp",u"杨亚平"],[u"yangyq",u"杨雨晴"],[u"yangyu",u"杨宇"],[u"yanhao",u"闫浩"],[u"yanhao1",u"闫浩"],[u"yanhao2",u"闫浩"],[u"yanhao3",u"闫浩"],[u"yankun",u"闫坤"],[u"yankun1",u"闫坤"],[u"yanpl",u"阎培雷"],[u"yanpl1",u"阎培雷"],[u"yanrj",u"闫如进"],[u"yansf",u"闫上峰"],[u"yansgly",u"演示管理员"],[u"yansyh",u"演示用户"],[u"yanxm",u"鄢雪梅"],[u"yanxm1",u"鄢雪梅"],[u"yanxs",u"鄢小双"],[u"yanxue",u"闫雪（车贷）"],[u"yanyang",u"燕阳"],[u"yaocm",u"姚春梅"],[u"yaocm1",u"姚春梅"],[u"yaofei",u"姚飞"],[u"yaogg",u"姚盖盖"],[u"yaohx",u"姚宏秀"],[u"yaohx1",u"姚宏秀"],[u"yaosq",u"姚尚顷"],[u"yaowy",u"姚文勇"],[u"yaoyu",u"姚宇"],[u"yaoyu1",u"姚宇"],[u"ychmyadmin",u"ychmyadmin"],[u"ycxjadm",u"ycxjadm"],[u"ycxxadm",u"ycxxadm"],[u"yczxadm",u"yczxadm"],[u"yeqing",u"叶青"],[u"yeqing1",u"叶青"],[u"yexc",u"叶小翠"],[u"yexin",u"叶新"],[u"yfqcadm",u"yfqcadm"],[u"yfwladm",u"yfwladm"],[u"ygadm",u"ygadm"],[u"yihx",u"易海祥"],[u"yihx1",u"易海祥"],[u"yilcf",u"一路财富"],[u"yilh",u"易玲辉"],[u"yincc",u"殷楚楚"],[u"yindc",u"尹冬驰"],[u"yindc1",u"尹冬驰"],[u"yinhang",u"尹航"],[u"yinhw",u"阴红伟"],[u"yinjw",u"银俊玮"],[u"yinjw1",u"银俊玮"],[u"yinjw2",u"银俊玮"],[u"yinjw3",u"银俊玮"],[u"yinkun",u"尹坤"],[u"yinsk",u"殷树坤"],[u"yinsk1",u"殷树坤"],[u"yinxj",u"殷晓杰"],[u"yinxl",u"殷晓玲"],[u"yinxy",u"尹秀艳"],[u"yinxy1",u"尹秀艳"],[u"yinzhong",u"尹仲"],[u"yiwei",u"伊伟"],[u"yiwei1",u"伊伟"],[u"ylszhadmin",u"ylszhadmin"],[u"ylwladm",u"ylwladm"],[u"ylxdadm",u"ylxdadm"],[u"ynyhadm",u"ynyhadm"],[u"youws",u"茶马"],[u"youyd",u"游玉丹"],[u"youyd1",u"游玉丹"],[u"youzs",u"游祖驷"],[u"youzs1",u"游祖驷"],[u"ysadmin2",u"ysadmin"],[u"yuanbing",u"袁冰"],[u"yuandq",u"员栋琪"],[u"yuanfang",u"袁芳"],[u"yuanfeng",u"袁凤"],[u"yuanfeng1",u"袁凤"],[u"yuanhs",u"苑洪山"],[u"yuanll",u"袁琳琳"],[u"yuanql",u"苑清莲"],[u"yuanql1",u"苑清莲"],[u"yuanquan",u"袁权"],[u"yuansl",u"袁书林"],[u"yuanxf",u"原雪峰"],[u"yuanyg",u"袁玉刚"],[u"yuanyg1",u"袁玉刚"],[u"yuanyg2",u"袁玉刚"],[u"yuanyg3",u"袁玉刚"],[u"yuanzp",u"苑忠鹏"],[u"yubj",u"于博婧"],[u"yuchao",u"俞超"],[u"yuct",u"喻春堂"],[u"yuegj",u"岳国际"],[u"yuegj1",u"岳国际"],[u"yueguo",u"岳国（成都）"],[u"yuewh",u"岳文海"],[u"yuewh1",u"岳文海"],[u"yueyj",u"岳永金"],[u"yujj",u"喻娇娇"],[u"yujj1",u"喻娇娇"],[u"yujx",u"于金校"],[u"yull",u"于琳琳"],[u"yull1",u"于琳琳"],[u"yumin",u"余敏"],[u"yumin1",u"余敏"],[u"yunying",u"运营"],[u"yury",u"余让云"],[u"yury1",u"余让云"],[u"yusz",u"俞赛珍"],[u"yutd",u"于天东"],[u"yutd1",u"于天东"],[u"yuwen",u"余稳"],[u"yuxin",u"俞辛"],[u"yuyl",u"于亚丽"],[u"yuym",u"于沄孟"],[u"yuzc",u"余志超"],[u"yxdyadmin",u"yxdyadmin"],[u"yxposadmin",u"yxposadmin"],[u"yycxadm",u"yycxadm"],[u"yyhcadm",u"yyhcadm"],[u"yzadm",u"yzadm"],[u"zangdy",u"臧德跃"],[u"zangdy1",u"臧德跃"],[u"zcadm2",u"zcadm"],[u"zcsmadmin",u"zcsmadmin"],[u"zengtao",u"曾涛"],[u"zengxf",u"曾雪菲"],[u"zengying",u"曾莹"],[u"zf0025",u"梅莉"],[u"zf0049",u"孙倩雯"],[u"zf0070",u"张皓"],[u"zf0321",u"潘月智"],[u"zf0402",u"汪梅梅"],[u"zf0500",u"杨娟娟"],[u"zf0521",u"杨妍"],[u"zf0527",u"朱培华"],[u"zf0657",u"沙占华"],[u"zf0666",u"李婷"],[u"zf0729",u"吴永欢"],[u"zf0836",u"邓立"],[u"zf1013",u"晏倚琦"],[u"zf1014",u"黄冉冉"],[u"zf1016",u"赵俊华"],[u"zf1077",u"秦威"],[u"zf121X",u"冷国玉"],[u"zf1259",u"李伟"],[u"zf1307",u"岳燕"],[u"zf1315",u"时志强"],[u"zf1334",u"张力"],[u"zf1727",u"史娜"],[u"zf1865",u"梁贵梅"],[u"zf1921",u"赵华芬"],[u"zf1928",u"周倩"],[u"zf2013",u"龚灏"],[u"zf2552",u"李春成"],[u"zf256X",u"谭雨勤"],[u"zf2825",u"刘莉"],[u"zf3204",u"张立婷"],[u"zf3278",u"郭其辉"],[u"zf3316",u"李盛哲"],[u"zf3324",u"邹菲"],[u"zf3629",u"张道翠"],[u"zf4046",u"张秀芹"],[u"zf4128",u"付芳"],[u"zf4504",u"李成雨"],[u"zf4523",u"张凤婷"],[u"zf4615",u"姜鹏"],[u"zf4810",u"夏欢前"],[u"zf4832",u"黄胜"],[u"zf5054",u"向志东"],[u"zf5126",u"侯清华"],[u"zf5349",u"马艳"],[u"zf5423",u"李丹"],[u"zf5452",u"刘全"],[u"zf5837",u"尤顺"],[u"zf6334",u"蒋大伟"],[u"zf6577",u"孙文明"],[u"zf6607",u"杨杏"],[u"zf7419",u"李天亮"],[u"zf8017",u"黄楠楠"],[u"zf8110",u"徐伟伟"],[u"zf8225",u"蒋华"],[u"zhangbh",u"张碧红"],[u"zhangbin",u"张滨"],[u"zhangbn",u"张炳南"],[u"zhangbn1",u"张炳南"],[u"zhangbn2",u"张丙南"],[u"zhangbo",u"张博"],[u"zhangbp",u"张北平"],[u"zhangchao",u"张超"],[u"zhangchao1",u"张超"],[u"zhangchao2",u"张超"],[u"zhangchao3",u"张超"],[u"zhangchao4",u"张超"],[u"zhangchao5",u"张超"],[u"zhangchen",u"张晨"],[u"zhangcl",u"张春雷"],[u"zhangcm",u"张春梅"],[u"zhangcy",u"张春艳"],[u"zhangcy1",u"张春艳"],[u"zhangdb",u"张德兵"],[u"zhangdg",u"张大公"],[u"zhangdi",u"张迪"],[u"zhangdl",u"张大龙"],[u"zhangdl1",u"张大龙"],[u"zhangdm",u"张德民"],[u"zhangds",u"张定顺"],[u"zhangduo",u"张朵"],[u"zhangduo1",u"张朵"],[u"zhangdx",u"张德新"],[u"zhangdx1",u"张德新"],[u"zhangfan",u"张帆"],[u"zhangfan1",u"张帆"],[u"zhangfan2",u"张帆"],[u"zhangff",u"张方方"],[u"zhanggx",u"张广信"],[u"zhanggz",u"张广宗"],[u"zhanghan",u"张晗"],[u"zhanghao",u"张浩"],[u"zhanghao1",u"张浩"],[u"zhanghb",u"章洪宾"],[u"zhanghb1",u"章洪宾"],[u"zhanghc",u"张鸿驰"],[u"zhanghc1",u"张鸿驰"],[u"zhanghj",u"张红军"],[u"zhanghl",u"张豪磊"],[u"zhanghl1",u"张豪磊"],[u"zhanghn",u"张海宁"],[u"zhanght",u"张慧婷"],[u"zhanghua",u"张华"],[u"zhanghui",u"张慧"],[u"zhanghui1",u"张慧"],[u"zhanghx",u"张海祥"],[u"zhanghy",u"张海燕"],[u"zhangjb",u"张金波"],[u"zhangjh",u"张俊豪"],[u"zhangjian",u"张建"],[u"zhangjian1",u"张建"],[u"zhangjie",u"张杰"],[u"zhangjie1",u"张杰"],[u"zhangjing",u"张静"],[u"zhangjing1",u"张静"],[u"zhangjj",u"张晶京"],[u"zhangjj1",u"张晶京"],[u"zhangjl",u"张建良"],[u"zhangjp",u"张静萍"],[u"zhangjp1",u"张静萍"],[u"zhangju",u"张居"],[u"zhangju1",u"张居"],[u"zhangju2",u"张居"],[u"zhangju3",u"张居"],[u"zhangjx",u"张俊孝"],[u"zhangjy",u"张佳园"],[u"zhangjy1",u"张景颐"],[u"zhangjy2",u"张景颐"],[u"zhangkm",u"张克敏"],[u"zhangkm1",u"张克敏"],[u"zhangle1",u"张乐"],[u"zhangle2",u"张乐"],[u"zhangle5",u"张乐"],[u"zhangle7",u"张乐"],[u"zhanglei",u"张磊"],[u"zhanglei1",u"张垒"],[u"zhanglei2",u"张垒"],[u"zhanglei3",u"张垒"],[u"zhanglei4",u"张垒"],[u"zhanglei5",u"张雷"],[u"zhanglei6",u"张雷"],[u"zhanglei7",u"张磊"],[u"zhanglei8",u"张磊"],[u"zhangliang",u"张亮"],[u"zhangliang1",u"张亮"],[u"zhanglin",u"张琳"],[u"zhanglin1",u"张琳"],[u"zhanglin2",u"张琳"],[u"zhanglj",u"张琳洁"],[u"zhangll",u"张玲玲"],[u"zhangll1",u"章丽丽"],[u"zhanglm",u"张丽梅"],[u"zhanglong",u"张龙"],[u"zhanglong1",u"张龙"],[u"zhanglong2",u"张龙"],[u"zhanglong3",u"张龙"],[u"zhanglong4",u"张龙"],[u"zhangly",u"张良燕"],[u"zhangmeng",u"张蒙"],[u"zhangmeng1",u"张蒙"],[u"zhangmj",u"张敏娟"],[u"zhangml",u"张明丽"],[u"zhangml1",u"张明丽"],[u"zhangmy",u"张明月"],[u"zhangmz",u"张明占"],[u"zhangmz1",u"张明占"],[u"zhangning",u"张宁"],[u"zhangning1",u"张宁"],[u"zhangnn",u"张宁宁"],[u"zhangny",u"张乃奕"],[u"zhangpeng",u"张朋"],[u"zhangpeng1",u"张鹏"],[u"zhangpf",u"张鹏飞"],[u"zhangpf1",u"张鹏飞"],[u"zhangpp",u"张培培"],[u"zhangpy",u"张鹏云"],[u"zhangqiang",u"张强"],[u"zhangqx",u"张秋香"],[u"zhangrj",u"张仁吉"],[u"zhangrj1",u"张仁吉"],[u"zhangrui",u"张锐"],[u"zhangsj",u"张驷驹"],[u"zhangsj1",u"张驷驹"],[u"zhangsl",u"张绍亮"],[u"zhangsl1",u"张士龙"],[u"zhangtt",u"张婷婷"],[u"zhangwc",u"张文超"],[u"zhangwc1",u"张文超"],[u"zhangwei",u"张伟"],[u"zhangwei1",u"张伟"],[u"zhangwei2",u"张伟"],[u"zhangwei3",u"张威"],[u"zhangwei4",u"张伟"],[u"zhangwei5",u"张薇"],[u"zhangww",u"张雯雯"],[u"zhangwy",u"张文远"],[u"zhangxiang",u"张翔"],[u"zhangxin",u"张鑫"],[u"zhangxk",u"张晓柯"],[u"zhangxl",u"张秀丽"],[u"zhangxl1",u"张秀丽"],[u"zhangxl2",u"张晓龙"],[u"zhangxp",u"张秀萍"],[u"zhangxp1",u"张秀萍"],[u"zhangxq",u"张晓琦"],[u"zhangxq1",u"张晓琦"],[u"zhangxw",u"张馨文"],[u"zhangxy",u"张兴余"],[u"zhangxy1",u"张兴余"],[u"zhangyan",u"张岩"],[u"zhangyan1",u"张岩"],[u"zhangyan3",u"张燕"],[u"zhangyang",u"张杨"],[u"zhangyc",u"张艳超"],[u"zhangyc1",u"张艳超"],[u"zhangyc2",u"张艳超"],[u"zhangyf",u"章益飞"],[u"zhangyh",u"张远华"],[u"zhangyh1",u"张宇航"],[u"zhangyh2",u"张宇航"],[u"zhangyh3",u"张远海"],[u"zhangying",u"张英"],[u"zhangyj",u"张严君"],[u"zhangym",u"张远猛"],[u"zhangym1",u"张远猛"],[u"zhangyong",u"张勇"],[u"zhangys",u"张永松"],[u"zhangys1",u"张雨姝"],[u"zhangys2",u"张雨姝"],[u"zhangyu",u"张宇"],[u"zhangyu1",u"张宇"],[u"zhangyu2",u"张宇"],[u"zhangyu3",u"张宇"],[u"zhangyu4",u"张宇"],[u"zhangyw",u"张永旺"],[u"zhangzg",u"张志刚"],[u"zhangzg1",u"张志刚"],[u"zhangzhan",u"张展"],[u"zhangzhen",u"张震"],[u"zhangzx",u"张志学"],[u"zhangzz",u"张真真"],[u"zhangzz1",u"张真真"],[u"zhanhl",u"詹洪利"],[u"zhanhl1",u"詹洪利"],[u"zhanjian",u"战舰"],[u"zhanjian1",u"战舰"],[u"zhanln",u"詹琳娜"],[u"zhanwang",u"湛旺"],[u"zhanwei",u"詹伟"],[u"zhaobb",u"赵波波"],[u"zhaoby",u"赵贝余"],[u"zhaoby1",u"赵贝余"],[u"zhaodd",u"赵丹丹"],[u"zhaodd1",u"赵丹丹"],[u"zhaofq",u"赵枫淇"],[u"zhaogl",u"赵国良"],[u"zhaohj",u"赵海军"],[u"zhaohj1",u"赵海军"],[u"zhaohui",u"赵辉"],[u"zhaohui1",u"赵辉"],[u"zhaohy",u"赵海远"],[u"zhaojing",u"赵婧"],[u"zhaojp",u"赵金鹏"],[u"zhaojp1",u"赵金鹏"],[u"zhaojs",u"赵家帅"],[u"zhaojt",u"赵峻涛"],[u"zhaojt1",u"赵峻涛"],[u"zhaokun",u"赵昆"],[u"zhaolei",u"赵磊"],[u"zhaolei1",u"赵磊"],[u"zhaoln",u"赵丽娜"],[u"zhaoln1",u"赵丽娜"],[u"zhaolp",u"赵利平"],[u"zhaolp1",u"赵利平"],[u"zhaoman",u"赵曼"],[u"zhaoming",u"赵明"],[u"zhaoming1",u"赵明"],[u"zhaomy",u"赵蒙元"],[u"zhaopeng",u"赵鹏"],[u"zhaoqiao",u"赵桥"],[u"zhaoqiong",u"赵琼"],[u"zhaoqm",u"肇启明"],[u"zhaoqm1",u"肇启明"],[u"zhaoshan",u"赵珊"],[u"zhaowg",u"赵卫国"],[u"zhaowj",u"赵文静"],[u"zhaoxiang",u"赵响"],[u"zhaoxiang1",u"赵响"],[u"zhaoxl",u"赵雪莉"],[u"zhaoxm",u"赵旭萌"],[u"zhaoxm1",u"赵晓梅"],[u"zhaoxp",u"赵小平"],[u"zhaoxp1",u"赵小平"],[u"zhaoyf",u"赵云发"],[u"zhaoyf1",u"赵云发"],[u"zhaoyf2",u"赵云发"],[u"zhaoyf3",u"赵云发"],[u"zhaoyf4",u"赵云发"],[u"zhaoyf5",u"赵云发"],[u"zhaoying",u"赵颖"],[u"zhaoying1",u"赵颖（审查）"],[u"zhaoyl",u"赵艳龙"],[u"zhaoyong",u"赵勇"],[u"zhaoyong1",u"赵勇"],[u"zhaoyu",u"赵禹"],[u"zhaozhe",u"赵哲"],[u"zhaozj",u"赵长俊"],[u"zhaozk",u"赵志况"],[u"zhazg",u"查竹刚"],[u"zhengcb",u"郑传斌"],[u"zhengch",u"郑朝辉"],[u"zhengch1",u"郑朝辉"],[u"zhengcz",u"郑传芝"],[u"zhengcz1",u"郑传芝"],[u"zhenggy",u"郑光一"],[u"zhenggy1",u"郑光一"],[u"zhengjh",u"郑镜鸿"],[u"zhengjh1",u"郑镜鸿"],[u"zhengps",u"郑培生"],[u"zhengps1",u"郑培生"],[u"zhengqy",u"郑庆怡"],[u"zhengqy1",u"郑庆怡"],[u"zhengqy2",u"郑庆怡"],[u"zhengqy3",u"郑庆怡"],[u"zhengqy4",u"郑庆怡"],[u"zhengsl",u"郑三磊"],[u"zhengsl1",u"郑三磊"],[u"zhengts",u"瑞格"],[u"zhengwen",u"郑雯"],[u"zhengwen1",u"郑雯"],[u"zhengxy",u"郑小云"],[u"zhengyp",u"郑友萍"],[u"zhengzj",u"郑芝俊"],[u"zhengzj1",u"郑芝俊"],[u"zhengzj2",u"郑芝俊"],[u"zhengzj3",u"郑芝俊"],[u"zhengzw",u"郑志伟"],[u"zhladm",u"zhladm"],[u"zhnadm",u"zhnadm"],[u"zhongjw",u"钟进文"],[u"zhongqin",u"钟芹"],[u"zhongxw",u"添隆"],[u"zhongyq",u"钟艺琼"],[u"zhouchao",u"周超"],[u"zhoudl",u"周道利"],[u"zhouhj",u"周洪吉"],[u"zhouhu",u"周虎"],[u"zhouhy",u"周海洋"],[u"zhouhy1",u"周海洋"],[u"zhoujc",u"周健昌"],[u"zhoujc1",u"周健昌"],[u"zhoujd",u"周金丹"],[u"zhoujd1",u"周金丹"],[u"zhoujing",u"周静"],[u"zhoujing1",u"周静"],[u"zhoujp",u"周君平"],[u"zhoujun",u"周俊"],[u"zhoulj",u"周立静"],[u"zhoulong",u"周龙"],[u"zhoulong1",u"周龙"],[u"zhoulong2",u"周龙"],[u"zhoulong3",u"周龙"],[u"zhoulu",u"周璐"],[u"zhoumh",u"周明辉"],[u"zhoumh1",u"周明辉"],[u"zhoumn",u"周曼诺（大连）"],[u"zhoumn1",u"周曼诺（大连）"],[u"zhoumy",u"周明洋"],[u"zhoumy1",u"周明洋"],[u"zhouping",u"周平"],[u"zhouqm",u"周秋民"],[u"zhoush",u"周书惠"],[u"zhousong",u"周松"],[u"zhousong1",u"周松"],[u"zhoutian",u"周添"],[u"zhoutw",u"周添旺"],[u"zhouwei",u"周薇"],[u"zhouwt",u"周文婷"],[u"zhouyp",u"周宇鹏"],[u"zhouyp1",u"周宇鹏"],[u"zhouyp2",u"周宇鹏"],[u"zhouyp3",u"周宇鹏"],[u"zhouzg",u"邹振贵"],[u"zhouzg1",u"周志刚"],[u"zhouzhou",u"周舟"],[u"zhouzhou1",u"周舟"],[u"zhouzhou2",u"周舟"],[u"zhouzhou3",u"周舟"],[u"zhouzj",u"周志江"],[u"zhouzj1",u"周志江"],[u"zhubb",u"朱兵兵"],[u"zhubb1",u"朱兵兵"],[u"zhubg",u"朱保国"],[u"zhubg1",u"朱保国"],[u"zhubg2",u"朱保国"],[u"zhubg3",u"朱保国"],[u"zhubing",u"朱兵"],[u"zhubl",u"朱保霖"],[u"zhucy",u"朱春燕"],[u"zhudi",u"朱迪"],[u"zhudi1",u"朱迪"],[u"zhufx",u"朱飞雄"],[u"zhugly",u"诸葛林燕"],[u"zhuhb",u"朱海波"],[u"zhuhl",u"朱红亮"],[u"zhuhn",u"朱浩楠"],[u"zhuhn1",u"朱浩楠"],[u"zhujian",u"朱健"],[u"zhujt",u"朱金涛"],[u"zhujt1",u"朱金涛"],[u"zhujt2",u"朱江涛"],[u"zhujt3",u"朱江涛"],[u"zhujy",u"朱建阳"],[u"zhull",u"朱璐璐"],[u"zhumin1",u"朱敏"],[u"zhuming",u"朱明"],[u"zhumk",u"朱明康"],[u"zhuqg",u"朱庆国"],[u"zhuqg1",u"朱庆国"],[u"zhuqm",u"朱倩敏"],[u"zhuqm1",u"朱倩敏"],[u"zhutao",u"朱涛"],[u"zhutao1",u"朱涛"],[u"zhuwl",u"朱文龙"],[u"zhuxw",u"朱小文"],[u"zhuxx",u"朱先祥"],[u"zhuyb",u"朱玉波"],[u"zhuyn",u"朱韵妮"],[u"zhuys",u"朱亚树"],[u"zhuys1",u"朱亚树"],[u"zhuzt",u"朱占涛"],[u"zjgxrxadm",u"zjgxrxadm"],[u"zjlfadm",u"zjlfadm"],[u"zjpladmin",u"zjpladmin"],[u"zongsheng",u"宗生"],[u"zourx",u"邹荣鑫"],[u"zrxadm",u"zrxadm"],[u"zttadm",u"zttadm"],[u"zunym",u"遵亚明"],[u"zuofk",u"左放坤"],[u"zuofk1",u"左放坤"],[u"zuojw",u"左金伟"],[u"zuoliang",u"左亮"],[u"zuoliang1",u"左亮"],[u"zuoliang2",u"左亮"],[u"zuoliang3",u"左亮"],[u"zxdnadm",u"zxdnadm"],[u"zzcmadmin",u"zzcmadmin"],[u"zzjyadmin",u"zzjyadmin"],[u"zzxadm",u"zzxadm"]]
)
    
    department = {u'':u'',u'00101':u'演示小贷',u'00101_2000':u'演示机构',u'00221':u'宇信易诚(POS)科技有限公司',u'00221_2000':u'北京总部',u'00221_2001':u'无锡办事处',u'00221_2002':u'长沙办事处',u'00221_2003':u'南宁办事处',u'00221_2004':u'昆明办事处',u'00221_2005':u'沈阳办事处',u'00221_2006':u'大连办事处',u'00221_2007':u'郑州办事处',u'00221_2008':u'深圳办事处',u'00221_2009':u'西安办事处',u'00221_2010':u'重庆办事处',u'00221_2011':u'南京办事处',u'00221_2012':u'上海办事处',u'00221_2013':u'广州办事处',u'00221_2014':u'武汉办事处',u'00221_2015':u'苏州办事处',u'00221_2016':u'常州办事处',u'00221_2017':u'北京办事处',u'00221_2018':u'济南办事处',u'00221_3000':u'无锡办事处',u'00221_3001':u'长沙办事处株洲网点',u'00221_3002':u'长沙办事处郴州网点',u'00221_3003':u'长沙办事处南昌网点',u'00221_3004':u'长沙办事处南昌网点',u'00241':u'无锡布鲁诺信息技术有限公司',u'00242':u'无锡华商网络科技有限公司',u'00261':u'长沙朝盈投资咨询有限公司',u'00262':u'广西星之影网络科技有限公司',u'00263':u'广西启龙投资咨询服务有限公司',u'00264':u'宾阳县金旺商贸有限责任公司',u'00265':u'北京东方金诚信用管理有限公司',u'00281':u'柳州市臻鼎贸易有限公司',u'00282':u'湖南鑫彤科技发展有限公司',u'00283':u'南宁市品雄电子产品有限公司',u'00302':u'广西南宁亚航商贸有限责任公司',u'00303':u'曲靖市众筹商贸有限公司',u'00304':u'大连君鼎科技有限公司',u'00305':u'西安冠涛电子科技有限公司',u'00306':u'洛阳杏林商贸有限公司',u'00307':u'润银投资管理（大连）有限公司',u'00308':u'苏州易沃信息科技有限公司',u'00311':u'昆山金帝投资管理有限公司',u'00312':u'株洲市集云科技有限公司',u'00313':u'株洲茶马农业有限公司',u'00314':u'深圳市鑫腾飞汽车贸易有限公司',u'00315':u'昆明赢变商贸有限公司',u'00317':u'大连旺泰服饰有限公司',u'00321':u'昆明融凯网络科技有限公司',u'00323':u'曲靖市欣帝元商贸有限公司',u'00324':u'辽宁鸿运投资担保有限公司',u'00325':u'洛阳磐之锦网络科技有限公司',u'00327':u'深圳市广融汇通信息咨询有限公司',u'00328':u'深圳市佳裕鑫投资发展有限公司',u'00329':u'焦作市瀚海超亿商贸有限公司',u'00330':u'重庆惠付科技有限公司',u'00331':u'焦作市鑫飞源商贸有限公司',u'00332':u'台州快银电子商务有限公司',u'00334':u'广东颍硕投资管理有限公司',u'00336':u'杭州瑞迦投资管理有限公司',u'00337':u'合肥市联融投资管理有限公司第一分公司',u'00338':u'杭州喜刷网络科技有限公司',u'00339':u'安徽富甲金融信息咨询有限公司',u'00340':u'台州金算子信息咨询有限公司',u'00341':u'浙江普利金融信息服务有限公司',u'00342':u'上海齐伟信息科技有限公司',u'00343':u'南京蓝宝石资产管理有限公司',u'00344':u'桂林晨翊电子商务有限公司',u'00345':u'宜兴市东源投资咨询有限公司',u'00346':u'灵川县桂银投资咨询有限公司',u'00347':u'无锡瑞格投资咨询有限公司',u'00349':u'深圳奥优创科技有限公司',u'00350':u'广东汇联资产管理有限公司',u'00351':u'无锡市添隆投资咨询有限公司',u'00353':u'郑州六郝商贸有限公司',u'00354':u'广州玖点整信息科技有限公司',u'00355':u'深圳市福田区龙唐圣贸易商行',u'00356':u'盐城市红蚂蚁投资管理有限公司',u'00358':u'江苏联融投资有限公司',u'00359':u'江苏兴创金融信息服务有限公司',u'00360':u'江阴市博达投资咨询有限公司',u'00361':u'沅陵县水中花内衣店',u'00362':u'郴州市人缘科技信息咨询服务有限公司',u'00363':u'湖南通融贸易有限公司',u'00364':u'深圳益万联投资有限公司',u'00365':u'秀峰区东金衡泰家电经营部',u'00366':u'深圳逸凡盛世实业有限公司',u'00367':u'广西南宁兑盈商贸有限公司',u'00368':u'柳州市继往投资管理有限公司',u'00369':u'宜昌卓信科技有限公司',u'00370':u'苏州畅尔达电子科技有限公司',u'00371':u'宜昌枫冠信息技术有限公司',u'00372':u'湖北丰怡农业发展科技有限公司',u'00373':u'湖北鑫星贷投资有限公司',u'00374':u'桂林茂翔环保科技有限公司',u'00376':u'广西檀源贸易有限公司',u'00377':u'黄海蓉',u'00381':u'马超超',u'00383':u'何兵',u'00384':u'蒋敏敏',u'00386':u'张志学',u'00387':u'李德宣',u'00388':u'秦月芬',u'00389':u'刘超',u'00390':u'梁影',u'00391':u'刘红燕',u'00392':u'毛世波',u'00393':u'鲍向玲',u'00394':u'金拴',u'00398':u'孙平波',u'00399':u'陆晓东',u'00400':u'湖北宝德财富管理有限公司',u'00401':u'大秦联合网络科技襄阳有限公司',u'00402':u'丹东美翔商务有限公司',u'00403':u'武汉恒昌鸿运金融信息咨询有限公司',u'00404':u'城南开发区重信电脑经营部',u'00405':u'武汉万融财富金融服务有限公司',u'00427':u'华融普惠(北京)电子商务有限公司',u'00428':u'武汉市瀚凌商贸有限公司',u'00429':u'许昌路凯商贸有限公司',u'00443':u'许昌市天泓科技有限公司',u'00444':u'洛阳明俊网络信息服务有限公司',u'00445':u'深圳市湘益行科技发展有限公司',u'00446':u'南昌鼎祁实业有限公司',u'00447':u'陈旭东',u'00461':u'许昌市森美网络科技有限公司',u'00462':u'山东伟岸信息技术有限公司',u'00463':u'岳阳市创先数码科技发展有限公司',u'00464':u'襄阳市鑫亿行商务信息咨询有限公司',u'00465':u'徐州宝信企业管理咨询服务有限公司',u'00466':u'广州天旺投资管理有限公司',u'00467':u'华融普惠(北京)电子商务有限公司平顶山新华营业部',u'00468':u'华融普惠(北京)电子商务有限公司中山东区营业部',u'00469':u'华融普惠(北京)电子商务有限公司洛阳西工营业部',u'00470':u'常熟市虞山镇闪银手机软件技术咨询服务部',u'00481':u'新乡市启明电子技术有限公司',u'00502':u'武陵区金诚经济信息咨询服务部',u'00504':u'邹荣鑫',u'00505':u'许昌本凡商贸有限公司',u'00506':u'新乡市君利天下商贸有限公司',u'00507':u'华融普惠(北京)电子商务有限公司东莞常平营业部',u'00508':u'华融普惠(北京)电子商务有限公司东莞南城营业部',u'00509':u'华融普惠(北京)电子商务有限公司南宁青秀营业部',u'00510':u'华融普惠(北京)电子商务有限公司佛山禅城营业部',u'00511':u'华融普惠(北京)电子商务有限公司深圳龙华营业部',u'00512':u'华融普惠(北京)电子商务有限公司佛山南海营业部',u'00513':u'华融普惠(北京)电子商务有限公司北海海城营业部',u'00514':u'华融普惠(北京)电子商务有限公司天津南开营业部',u'00515':u'华融普惠(北京)电子商务有限公司武汉武昌营业部',u'00516':u'华融普惠(北京)电子商务有限公司许昌魏都营业部',u'00517':u'华融普惠(北京)电子商务有限公司广州天河营业部',u'00518':u'华融普惠(北京)电子商务有限公司贵港港北营业部',u'00519':u'华融普惠(北京)电子商务有限公司阳江江城营业部',u'00520':u'华融普惠(北京)电子商务有限公司海口龙华营业部',u'00521':u'华融普惠(北京)电子商务有限公司湛江霞山营业部',u'00522':u'华融普惠(北京)电子商务有限公司惠州惠城营业部',u'00523':u'华融普惠(北京)电子商务有限公司肇庆端州营业部',u'00524':u'华融普惠(北京)电子商务有限公司江门蓬江营业部',u'00525':u'华融普惠(北京)电子商务有限公司郑州金水营业部',u'00526':u'华融普惠(北京)电子商务有限公司柳州柳北营业部',u'00527':u'华融普惠(北京)电子商务有限公司西安未央营业部',u'00528':u'北银消费金融公司',u'00528_2000':u'中亿普惠天津营业部',u'00528_3000':u'安徽金管资产管理有限公司',u'00528_3001':u'中亿普惠辽宁丹东营业部',u'00528_3002':u'中亿普惠湖南长沙营业部',u'00528_3003':u'北京金辰杰投资有限公司',u'00528_3004':u'北京鸿翔伟业投资管理有限公司',u'00528_3005':u'北京金兆泰丰投资管理有限公司',u'00528_3006':u'北京中海昌盛科贸有限公司',u'00528_3007':u'国鼎日盛投资（北京）有限公司',u'00528_3008':u'内蒙古金管资产管理有限公司',u'00528_3009':u'河南金管资产管理有限责任公司',u'00528_3010':u'山西金管资产管理有限公司',u'00528_3011':u'中亿普惠陕西西安营业部',u'00528_3012':u'云南金管资产管理有限公司',u'00528_3013':u'绵阳鑫管企业管理有限公司',u'00528_3014':u'国鼎日盛投资（北京）有限公司',u'00528_3015':u'广州聚焦网络技术有限公司',u'00528_3016':u'深圳市科御医疗健康服务有限公司',u'00528_3017':u'深圳市特美笛贸易有限公司',u'00528_3018':u'东营宝昌投资有限公司',u'00528_3019':u'烟台华恒投资有限公司',u'00528_3020':u'四川汇金易融商务咨询有限公司',u'00528_3021':u'浙江央联资产管理有限公司',u'00528_3022':u'珠海市宏伟园林景观设计工程有限公司',u'00528_3023':u'天津诚成中盛财务管理咨询有限公司',u'00528_3024':u'天津金池津成资产管理有限公司',u'00528_3025':u'赤峰金管资产管理有限公司',u'00528_3026':u'咸宁朝发投资管理有限公司',u'00528_3027':u'郑州二四正弘金融服务外包有限公司',u'00528_3028':u'登封市元祥铝业有限公司',u'00528_3029':u'河南省大爱资产管理有限责任公司',u'00528_3030':u'河南省汇金易融信息技术有限公司',u'00528_3031':u'河南腾远机械设备有限公司',u'00528_3032':u'河南云阁网络科技有限公司',u'00528_3033':u'平顶山市万耀商贸有限公司',u'00528_3034':u'濮阳迈瑞司抗震住宅技术有限公司',u'00528_3035':u'濮阳市卡纳装饰工程有限公司',u'00528_3036':u'郑州凌之峰商贸有限公司',u'00528_3037':u'郑州络胜科技有限公司',u'00528_3038':u'鹤壁市帝华商贸有限公司',u'00528_3039':u'内黄县树红建筑材料经营部',u'00528_3040':u'许昌络胜网络技术有限公司',u'00528_3041':u'鼎鑫（大连）资产管理有限公司',u'00528_3042':u'黑龙江鼎鑫资产管理有限公司',u'00528_3043':u'融金河南郑州签约二部',u'00528_3044':u'融金江苏南通签约一部',u'00528_3045':u'融金河南许昌签约一部',u'00528_3046':u'融金河北邢台签约一部',u'00528_3047':u'融金河北石家庄签约一部',u'00528_3048':u'融金黑龙江哈尔滨签约一部',u'00528_3049':u'融金黑龙江大庆签约一部',u'00528_3050':u'黑龙江鼎鑫资产管理有限公司富锦分公司',u'00528_3051':u'兴宏（北京）资产管理有限公司江西省分公司',u'00528_3052':u'兴宏（北京）资产管理有限公司江西省分公司',u'00528_3053':u'安徽省兴宏资产管理有限公司',u'00528_3054':u'秦皇岛鑫鑫焱企业管理有限公司',u'00528_3055':u'北京融创投资担保有限公司',u'00528_3056':u'速融通（北京）资产管理有限公司',u'00528_3057':u'北京兴宏博亚资产管理有限公司',u'00528_3058':u'北京鑫达日盛资产管理有限公司',u'00528_3059':u'泰州君诚资产管理有限公司',u'00528_3060':u'兴宏（北京）资产管理有限公司安顺翔分公司',u'00528_3061':u'北京忠义华信贸易有限公司',u'00528_3062':u'哈尔滨市鼎成投资管理有限公司',u'00528_3063':u'兴宏嘉晟（北京）资产管理有限公司',u'00528_3064':u'鑫和（北京）资产管理有限公司',u'00528_3065':u'安庆大众资产管理有限公司',u'00528_3066':u'北京兴盛融通投资有限公司',u'00528_3067':u'尚盈资产管理有限公司',u'00528_3068':u'鹤岗汇融投资有限公司',u'00528_3069':u'三河市鼎泰企业信息咨询有限公司',u'00528_3070':u'赤城兴财融通投资咨询服务有限公司',u'00528_3071':u'内蒙古兴宏华阳聚金投资有限公司',u'00528_3072':u'九江欣宏资产管理有限公司',u'00528_3073':u'兴宏（北京）资产管理有限公司石家庄分公司',u'00528_3074':u'河北北伸源投资有限公司',u'00528_3075':u'江苏兴厦资产管理有限公司',u'00528_3076':u'张家口北银投资咨询服务有限公司',u'00528_3077':u'商丘市兴和房地产中介有限公司',u'00528_3078':u'温州亿已投资信息咨询有限公司',u'00528_3079':u'兴宏（北京）资产管理有限公司河北分公司',u'00528_3080':u'哈尔滨市龙军投资管理有限公司',u'00528_3081':u'江西鼎盛世纪资产管理有限公司',u'00528_3082':u'河南刚乾实业有限公司',u'00528_3083':u'石家庄市鹿泉区鑫宏商务服务有限公司',u'00528_3084':u'河北北伸源投资有限公司保定第一分公司',u'00528_3085':u'迁安市泰安企业管理咨询服务有限公司',u'00528_3086':u'聊城兴宏鼎盛金融信息服务有限公司',u'00528_3087':u'山东兴邦金融服务外包有限公司',u'00528_3088':u'富锦市惠洋春天投资管理有限公司',u'00528_3089':u'烟台兴宏国益投资有限公司',u'00528_3090':u'贵州羽宣资产管理有限公司',u'00528_3091':u'本溪兴宏投资管理有限公司',u'00528_3092':u'秦皇岛世强商务服务有限公司',u'00528_3093':u'六安市建宏投资管理有限公司',u'00528_3094':u'抚宁县铭泰商务服务有限公司',u'00528_3095':u'江西宏福资产管理有限公司',u'00528_3096':u'甘肃兴宏企业管理有限公司',u'00528_3097':u'集贤县合力投资咨询有限公司',u'00528_3098':u'青岛茂源鑫通商贸有限公司',u'00528_3099':u'卢龙县凤龙商务服务有限公司',u'00528_3100':u'天津市东盛资产管理有限责任公司',u'00528_3101':u'衡水卓信资产管理有限公司',u'00528_3102':u'湖北新福投资有限公司',u'00528_3103':u'秦皇岛贵昌商务服务有限公司',u'00528_3104':u'华美汇达（北京）资产管理有限责任公司',u'00528_3105':u'北京日新恒远投资管理有限公司',u'00528_3106':u'达通投资咨询服务有限责任公司',u'00528_3107':u'北京兴宏鑫融投资资产管理有限公司',u'00528_3108':u'成都坤银贷投资管理有限公司',u'00528_3109':u'沈阳鼎城恒金投资管理有限公司',u'00528_3110':u'廊坊市海州企业管理咨询有限公司',u'00528_3111':u'北京信泽通投资管理有限公司',u'00528_3112':u'南京丹宏金融信息服务有限公司',u'00528_3113':u'兴宏（北京）资产管理有限公司云南分公司',u'00528_3114':u'兴宏（北京）资产管理有限公司阳洋分公司',u'00528_3115':u'兴宏（北京）资产管理有限公司褔顺和投资咨询分公司',u'00528_3116':u'北京宏通顺昌投资管理有限公司',u'00528_3117':u'兴宏（北京）资产管理有限公司辽阳分公司',u'00528_3119':u'北京融海昌盛国际投资有限公司',u'00528_3120':u'上海贯宏资产管理有限公司',u'00528_3121':u'北京同大资产管理有限公司',u'00528_3122':u'广西贝福信用服务有限公司',u'00528_3123':u'华融普惠(北京)电子商务有限公司广州海珠营业部',u'00528_3124':u'华融普惠(北京)电子商务有限公司东莞长安营业部',u'00528_3125':u'华融普惠(北京)电子商务有限公司玉林玉州营业部',u'00528_3126':u'华融普惠(北京)电子商务有限公司苏州高新营业部',u'00528_3127':u'华融普惠(北京)电子商务有限公司呼和浩特新城营业部',u'00528_3128':u'华融普惠(北京)电子商务有限公司重庆江北营业部',u'00528_3129':u'兴宏（北京）资产管理有限公司门头沟资产管理分公司',u'00528_3130':u'北京日新恒远投资管理有限公司',u'00528_3131':u'菏泽兴宏金融服务有限公司',u'00528_3132':u'融金安徽合肥签约一部',u'00528_3133':u'融金安徽芜湖签约一部',u'00528_3134':u'融金河北衡水签约一部',u'00528_3135':u'融金河南新乡签约一部',u'00528_3136':u'融金河南许昌签约二部',u'00528_3137':u'融金河南郑州签约一部',u'00528_3138':u'融金吉林吉林签约一部',u'00528_3139':u'融金吉林长春签约一部',u'00528_3140':u'融金江苏南京签约一部',u'00528_3141':u'融金江苏南通签约一部',u'00528_3142':u'融金江苏苏州签约一部',u'00528_3143':u'融金江苏无锡签约一部',u'00528_3144':u'融金江苏徐州签约一部',u'00528_3145':u'融金江苏扬州签约一部',u'00528_3146':u'融金河北廊坊签约一部',u'00528_3147':u'融金陕西西安签约一部',u'00528_3148':u'融金广东东莞签约一部',u'00528_3149':u'融金四川成都签约一部',u'00528_3150':u'中亿普惠北京营业部',u'00528_3151':u'许昌北银商贸有限公司',u'00528_3152':u'兴宏（北京）资产管理有限公司房山分公司',u'00528_3153':u'北京兴华德盛投资咨询有限公司',u'00528_3154':u'兴宏（北京）资产管理有限公司内蒙古分公司',u'00528_3155':u'兴宏（北京）资产管理有限公司呼和浩特市分公司',u'00528_3156':u'北京嘉来粒投资担保有限公司',u'00528_3157':u'兴宏（北京）资产管理有限公司青云店分公司',u'00528_3158':u'本溪市盛泰投资管理有限公司',u'00528_3159':u'绥化鑫悦投资咨询服务有限公司',u'00528_3160':u'兴宏(北京)资产管理有限公司众搏分公司',u'00528_3161':u'菏泽兴宏金融服务有限公司',u'00528_3162':u'中亿普惠辽宁沈阳营业部',u'00528_3163':u'中亿普惠安徽合肥营业部',u'00528_3164':u'中亿普惠浙江杭州营业部',u'00528_3165':u'中亿普惠山西太原营业部',u'00528_3166':u'中亿普惠四川绵阳营业部',u'00528_3167':u'中亿普惠云南昆明营业部',u'00528_3168':u'中亿普惠河北石家庄营业部',u'00528_3169':u'心海集团有限责任公司北京西城区营业部',u'00528_3170':u'心海集团有限责任公司北京大兴区营业部',u'00528_3171':u'心海集团有限责任公司贵州南明区营业部',u'00528_3172':u'心海集团有限责任公司河北唐山路北区营业部',u'00528_3173':u'心海集团有限责任公司河北唐山路南区营业部',u'00528_3174':u'心海集团有限责任公司河北承德双桥区营业部',u'00528_3175':u'心海集团有限责任公司河南郑州二七区营业部',u'00528_3176':u'心海集团有限责任公司河南许昌东城区营业部',u'00528_3177':u'心海集团有限责任公司河南郑州郑东新区营业部',u'00528_3178':u'心海集团有限责任公司河南郑州金水区营业部',u'00528_3179':u'心海集团有限责任公司江西九江市营业部',u'00528_3180':u'心海集团有限责任公司山东青岛李沧区营业部',u'00528_3181':u'心海集团有限责任公司山东济南槐荫区营业部',u'00528_3182':u'心海集团有限责任公司山东聊城经济开发区营业部',u'00528_3183':u'心海集团有限责任公司四川绵阳涪城区营业部',u'00528_3184':u'心海集团有限责任公司四川成都高新区营业部',u'00528_3185':u'心海集团有限责任公司四川宜宾营业部',u'00528_3186':u'心海集团有限责任公司四川成都锦江区营业部',u'00528_3187':u'心海集团有限责任公司四川成都武侯区营业部',u'00528_3188':u'心海集团有限责任公司四川重庆北部新区营业部',u'00528_3189':u'心海集团有限责任公司四川重庆巴南营业部',u'00528_3190':u'心海集团有限责任公司天津自贸区营业部',u'00528_3191':u'心海集团有限责任公司山东济南市中区营业部',u'00528_3192':u'华信众筹营业部1',u'00528_3193':u'华信众筹营业部2',u'00528_3194':u'华信众筹营业部3',u'00528_3195':u'华信众筹营业部4',u'00528_3196':u'华信众筹营业部5',u'00528_3197':u'华信众筹营业部6',u'00528_3198':u'华信众筹营业部7',u'00528_3199':u'华信众筹营业部8',u'00528_3200':u'华信众筹营业部9',u'00528_3201':u'华信众筹营业部10',u'00528_3202':u'华信众筹营业部11',u'00528_3203':u'华信众筹营业部12',u'00528_3204':u'华信众筹营业部13',u'00528_3205':u'华信众筹营业部14',u'00528_3206':u'华信众筹营业部15',u'00528_3207':u'华信众筹营业部16',u'00528_3208':u'华信众筹营业部17',u'00528_3209':u'华信众筹营业部18',u'00528_3210':u'华信众筹营业部19',u'00528_3211':u'华信众筹营业部20',u'00528_3212':u'华信众筹营业部21',u'00528_3213':u'华信众筹营业部22',u'00528_3214':u'华信众筹营业部23',u'00528_3215':u'华信众筹营业部24',u'00528_3216':u'华信众筹营业部25',u'00528_3217':u'华信众筹营业部26',u'00528_3218':u'华信众筹营业部27',u'00528_3219':u'华信众筹营业部28',u'00528_3220':u'华信众筹营业部29',u'00528_3221':u'华信众筹营业部30',u'00528_3222':u'华信众筹营业部31',u'00528_3223':u'华信众筹营业部32',u'00528_3224':u'华信众筹营业部33',u'00528_3225':u'华信众筹营业部34',u'00528_3226':u'华信众筹营业部35',u'00528_3227':u'华信众筹营业部36',u'00528_3228':u'华信众筹营业部37',u'00528_3229':u'华信众筹营业部38',u'00528_3230':u'华信众筹营业部39',u'00528_3231':u'华信众筹营业部41',u'00528_3232':u'华信众筹营业部43',u'00528_3233':u'华信众筹营业部44',u'00528_3234':u'华信众筹营业部45',u'00528_3235':u'华信众筹营业部46',u'00528_3236':u'华信众筹营业部47',u'00528_3237':u'华信众筹营业部48',u'00528_3238':u'华信众筹营业部49',u'00528_3239':u'华信众筹营业部50',u'00528_3240':u'华信众筹营业部51',u'00528_3241':u'华信众筹营业部52',u'00528_3242':u'华信众筹营业部53',u'00528_3243':u'华信众筹营业部54',u'00528_3244':u'华信众筹营业部55',u'00528_3245':u'华信众筹营业部56',u'00528_3246':u'华信众筹营业部57',u'00528_3247':u'华信众筹营业部58',u'00528_3248':u'华信众筹营业部59',u'00528_3249':u'华信众筹营业部60',u'00528_3250':u'华信众筹营业部61',u'00528_3251':u'哈尔滨富阳投资有限公司',u'00528_3252':u'华信众筹营业部62',u'00528_3253':u'华信众筹营业部63',u'00528_3254':u'华信众筹营业部64',u'00528_3255':u'华信众筹营业部65',u'00528_3256':u'华信众筹营业部66',u'00528_3257':u'华信众筹营业部67',u'00528_3258':u'华信众筹营业部40',u'00528_3259':u'华信众筹营业部42',u'00528_4000':u'大庆市宏宇雪梅广告有限公司',u'00528_4001':u'大庆庆然天然气有限公司',u'00528_4002':u'大庆孟氏投资管理有限公司',u'00528_4003':u'吉林金管资产管理有限公司',u'00528_4004':u'长春市金管商务信息咨询服务有限公司',u'00528_4005':u'长春市禹晟投资管理有限公司',u'00528_4006':u'江阴昌吉投资管理有限公司',u'00528_4007':u'丹东创发实业有限公司',u'00528_4008':u'丹东富华牧业有限公司',u'00528_4009':u'丹东市振安区同兴镇金鑫水泥制品厂',u'00528_4010':u'凤城元腾实业有限公司',u'00528_4011':u'沈阳德盛商务信息咨询有限公司',u'00528_4012':u'沈阳金管资产管理有限公司',u'00528_4013':u'甘肃仰运物资有限公司',u'00528_4014':u'淄博路侠信息咨询有限公司',u'00528_4015':u'甘肃金管资产管理有限公司',u'00528_4016':u'潍坊博远投资管理有限公司',u'00528_4017':u'金昌诚信银通资产管理有限公司',u'00528_4018':u'内蒙古桔子金融服务有限责任公司',u'00528_4019':u'威海龙信投资管理有限公司',u'00528_4020':u'聊城市财信投资担保有限公司',u'00528_4021':u'济宁亿通投资管理有限公司',u'00528_4022':u'内蒙古新益贷互联网金融信息服务有限公司',u'00528_4023':u'阿拉善盟金管资产管理有限公司',u'00528_4024':u'安鑫达汽车检测有限公司',u'00528_4025':u'巴彦淖尔金投资产管理有限公司',u'00528_4026':u'济南大业投资管理有限公司',u'00528_4027':u'巴彦淖尔市明德商贸有限责任公司',u'00528_4028':u'滨州市平太投资管理有限公司',u'00528_4029':u'巴彦淖尔市新势力广告有限公司',u'00528_4030':u'通辽市金石投资管理有限公司',u'00528_4031':u'巴彦淖尔市鑫盛商贸有限公司',u'00528_4032':u'赤峰君和投资管理有限公司',u'00528_4033':u'包头仁杰投资信息咨询有限公司',u'00528_4034':u'包头市鲁商投资管理有限公司',u'00528_4035':u'包头市聚鑫源汽车贸易有限公司',u'00528_4036':u'包头市旺鼎汽贸有限公司',u'00528_4037':u'沈阳润丰投资管理有限公司',u'00528_4038':u'鄂尔多斯市路安汽贸有限公司',u'00528_4039':u'铜陵金管资产管理有限公司',u'00528_4040':u'义乌市天市投资管理有限公司',u'00528_4041':u'金华市梦达投资管理有限公司',u'00528_4042':u'呼和浩特市金管资产管理有限公司',u'00528_4043':u'呼和浩特市誉腾汽车销售有限公司',u'00528_4044':u'天津市天门投资管理有限公司',u'00528_4045':u'菏泽市三铃投资信息咨询有限公司',u'00528_4046':u'金印广告有限公司',u'00528_4047':u'长治市万威投资管理有限公司',u'00528_4048':u'青岛宝泉工贸有限公司',u'00528_4049':u'满洲里金管资产管理有限公司',u'00528_4050':u'运城市贝格投资管理服务有限公司',u'00528_4051':u'内蒙古豪正资产管理有限公司',u'00528_4052':u'忻州市谷雨信息咨询有限公司',u'00528_4053':u'湖南普兰电子商务有限公司',u'00528_4054':u'太原一开投资管理有限公司',u'00528_4055':u'内蒙古亨晔汽车服务有限公司',u'00528_4056':u'智慧芙蓉（湖南）城市营运系统服务有限公司',u'00528_4057':u'吕梁市日晟投资管理有限公司',u'00528_4058':u'内蒙古弘冠资产管理有限公司',u'00528_4059':u'智慧桃花源（湖南）城市营运系统服务有限公司',u'00528_4060':u'内蒙古久久易小额贷款咨询服务有限责任公司',u'00528_4061':u'智慧潇湘（湖南）城市营运系统服务有限公司',u'00528_4062':u'内蒙古立信资产管理咨询服务有限公司',u'00528_4063':u'内蒙古融通投资咨询有限公司',u'00528_4064':u'湖南家嘉食品有限公司',u'00528_4065':u'大同市新海信息咨询有限公司',u'00528_4066':u'内蒙古三瑞贸易有限责任公司',u'00528_4067':u'山西金管百车行信息咨询有限公司',u'00528_4068':u'湖南嘉茂房地产开发有限公司',u'00528_4069':u'内蒙古腾程广告有限公司',u'00528_4070':u'内蒙古鑫盛华亿投资有限公司',u'00528_4071':u'湖南凯龙网络科技有限公司',u'00528_4072':u'锦州金航投资管理有限公司',u'00528_4073':u'通辽金管资产管理有限公司',u'00528_4074':u'湖南省天雅农林绿化科技发展有限公司',u'00528_4075':u'通辽市兴吉汽车租赁有限公司',u'00528_4076':u'大连九天投资管理有限公司',u'00528_4077':u'湖南湘粤融资产管理有限公司',u'00528_4078':u'乌海金管资产管理有限公司',u'00528_4079':u'鞍山市双成投资管理有限公司',u'00528_4080':u'湖南伊翔置业有限公司',u'00528_4081':u'乌海市瑞翔商贸有限责任公司',u'00528_4082':u'娄底骏豪文体用品有限公司',u'00528_4083':u'镇江市国宁投资管理有限公司',u'00528_4084':u'乌兰察布市管金投资有限公司',u'00528_4085':u'沅江市有信汽车贸易有限公司',u'00528_4086':u'徐州利好投资管理有限公司',u'00528_4087':u'锡林郭勒盟鑫博瑞投资有限公司',u'00528_4088':u'沅江市宇航发展有限公司',u'00528_4089':u'连云港市金佰禾商贸有限公司',u'00528_4090':u'通辽市弘伟信息咨询服务有限公司',u'00528_4091':u'长沙慈德文化传播有限公司',u'00528_4092':u'吉林中澳投资集团有限公司',u'00528_4093':u'长沙县哲圣农业科技开发有限公司',u'00528_4094':u'绥化金信银通投资管理有限公司',u'00528_4095':u'长沙八旗信息科技有限公司',u'00528_4096':u'晋城经济开发区融易贷小额贷款有限公司',u'00528_4097':u'双鸭山市双源投资有限责任公司',u'00528_4098':u'临汾美华美尚文化传媒有限公司',u'00528_4099':u'安国市融通信息咨询有限公司',u'00528_4100':u'太原市信友邦投资咨询有限公司',u'00528_4101':u'三亚鑫京商贸有限责任公司',u'00528_4102':u'淮北市倚天投资管理有限公司',u'00528_4103':u'闻喜县锦盈昇小额贷款有限责任公司',u'00528_4104':u'合肥市华联信息咨询服务有限公司',u'00528_4105':u'孝义市金管贸易有限公司',u'00528_4106':u'长沙湘创资产管理有限公司',u'00528_4107':u'原平市聚创空间商贸有限公司',u'00528_4108':u'原平市银信小额贷款有限责任公司',u'00528_4109':u'惠州市南新橡塑制品有限有限公司',u'00528_4110':u'北京铭江科技发展有限公司',u'00528_4111':u'义乌华以农业科技有限公司',u'00528_4112':u'北京时代财富投资管理有限公司',u'00528_4113':u'长沙享居红木家具有限公司',u'00528_4114':u'北京天朗嘉盛投资咨询有限公司',u'00528_4115':u'北京熙然财富投资管理有限公司',u'00528_4116':u'北京云德伟业商贸有限公司',u'00528_4117':u'徐州市第六建筑安装工程公司',u'00528_4118':u'盛钰耀融（北京）科技有限公司',u'00528_4119':u'九朝会鑫（北京）资产管理有限公司',u'00528_4120':u'自贡市金管资产管理有限公司',u'00528_4121':u'和田金地新农商贸有限公司',u'00528_4122':u'宜宾市金管资产管理有限公司',u'00528_4123':u'遂宁市金管资产管理有限公司',u'00528_4124':u'南充金管资产管理有限公司',u'00528_4125':u'乐山市金管资产管理有限公司',u'00528_4126':u'广元市金管资产管理有限公司',u'00528_4127':u'广安市金管资产管理有限公司',u'00528_4128':u'德阳市金管资产管理有限公司',u'00528_4129':u'沧州一德投资管理有限公司',u'00528_4130':u'达州金管信息服务有限公司',u'00528_4131':u'合印投资管理有限公司',u'00528_4132':u'成都市武侯区金管资产管理有限公司',u'00528_4133':u'巴中金管资产管理有限公司',u'00528_4134':u'乾坤福商贸有限公司',u'00528_4135':u'三河市辉成投资有限公司',u'00528_4136':u'唐山柏悦投资管理有限公司',u'00528_4137':u'邢台金管坤宝商贸有限公司',u'00528_4138':u'涿州市华睿通投资有限公司',u'00528_4139':u'西安德邦林实验室设备有限公司',u'00528_4140':u'武功县恒顺房地产开发有限责任公司',u'00528_4141':u'延安灏瀚豪杰商贸有限公司',u'00528_4142':u'安康市宗远智能电子科技有限公司',u'00528_4143':u'澄城县龙腾工贸有限公司',u'00528_4144':u'富平县金鼎源小麦种植专业合作社',u'00528_4145':u'陕西风华蓉兴生态庄园有限公司',u'00528_4146':u'陕西和旭商贸有限公司',u'00528_4147':u'陕西汇金易融商务服务有限公司',u'00528_4148':u'陕西拓盛实业有限责任公司',u'00528_4149':u'陕西昭宏建筑安装工程有限公司',u'00528_4150':u'渭南昌信新型建材有限公司',u'00528_4151':u'咸阳荣豪商贸有限公司',u'00528_4152':u'陕西建康电子商务有限公司',u'00528_4153':u'陕西禾佳农佳农科贸有限',u'00528_4154':u'葫芦岛鼎鑫资产管理有限公司',u'00528_4155':u'鼎鑫（北京）资产管理有限责任公司阜蒙县分公司',u'00528_4156':u'鼎鑫（北京）资产管理有限责任公司本溪分公司',u'00528_4157':u'鼎鑫（北京）资产管理有限公司鞍山分公司',u'00528_4158':u'鼎鑫（北京）资产管理有限责任公司秦皇岛分公司',u'00528_4159':u'黑龙江鼎鑫资产管理有限公司汤原分公司',u'00528_4160':u'黑龙江鼎鑫资产管理有限公司拜泉分公司',u'00528_4161':u'黑龙江鼎鑫资产管理有限公司宝泉岭分公司',u'00528_4162':u'黑龙江鼎鑫资产管理有限公司集贤分公司',u'00528_4163':u'五常市银博士资产管理有限公司',u'00528_4164':u'嫩江县汇融资产管理有限公司',u'00528_4165':u'黑龙江鼎鑫资产管理有限公司前哨分公司',u'00528_4166':u'成都国凯东商务服务有限公司',u'00528_4167':u'四川国创国睿投资有限公司',u'00528_4168':u'巴中国创投资有限公司',u'00528_4169':u'重庆巨全投资咨询有限责任公司',u'00529':u'河南万事捷贸易有限公司',u'00530':u'盐城市鼎域众融投资咨询有限公司',u'00531':u'张海宁',u'00532':u'江苏银方投资管理有限公司',u'00541':u'北京圣维华投资管理有限公司',u'00542':u'北京万众信用管理有限公司',u'00543':u'万众信用唐山玉田直营店',u'00544':u'万众信用亦庄直营店',u'00545':u'万众信用龙湖分公司',u'00546':u'万众信用西红门直营店',u'00547':u'万众信用河南周口直营店',u'00548':u'万众信用唐山丰润直营店',u'00549':u'万众信用景德镇分公司',u'00550':u'万众信用廊坊固安分公司',u'00551':u'万众信用昌平直营店',u'00552':u'唐山路北直营店',u'00553':u'万众信用武夷山分公司',u'00554':u'国创控股集团有限公司',u'00555':u'国创控股集团有限公司中弘兴分公司',u'00556':u'国创控股集团有限公司华融担保分公司',u'00557':u'国创控股集团有限公司西南分公司',u'00558':u'国创控股集团有限公司成都金控分公司',u'00560':u'富邦信（北京）金融服务外包有限公司',u'00561':u'鼎鑫（北京）资产管理有限责任公司',u'00562':u'兴宏（北京）资产管理有限公司',u'00563':u'湖北卡联商务服务有限公司襄阳分公司',u'00564':u'金管资产管理有限公司',u'00565':u'新普开元（北京）资产管理有限公司',u'00566':u'邯郸市乾亿担保有限公司',u'00567':u'济南金澄信息咨询有限公司',u'00568':u'泗水县立军物流有限公司',u'00569':u'哈尔滨家便利电子商务有限公司',u'00570':u'四川国创金控商务服务有限公司',u'00571':u'北京中弘兴投资管理有限公司',u'00572':u'三门峡巴珊电子商务有限公司',u'00573':u'心海（北京）金融信息服务有限公司',u'00575':u'山西晋林财智企业管理有限公司',u'00576':u'河南众筹资产管理有限公司',u'00577':u'固安县东信融通投资咨询服务有限公司',u'00578':u'北京一村一家文化传播有限公司',u'00579':u'河南弗雷电子科技有限公司',u'00580':u'江西融投资产管理有限公司',u'00581':u'山东济宁凯达建筑工程有限公司',u'00582':u'聊城市东升包装设备有限公司',u'00583':u'青岛小珠山旅游发展有限公司',u'00584':u'北京欧尼克复合材料板厂',u'00585':u'北京信同宏利咨询服务有限公司',u'00586':u'北京鑫盛峰岭投资有限公司',u'00587':u'枣庄市赢信经济信息咨询有限公司',u'00590':u'重庆创富联合商务信息咨询有限公司',u'00592':u'河南畅远企业管理咨询有限公司',u'00593':u'华融担保有限公司',u'00594':u'河南信鑫金融服务有限公司',u'00595':u'郑州金亿斯顿电子科技有限公司',u'00596':u'湖北金管众诚资产管理有限责任公司',u'00597':u'聊城市日兴达商务信息咨询有限公司',u'00598':u'廊坊市金淇竣通投资咨询有限公司',u'00599':u'山东聊城众信网络科技有限公司',u'00600':u'心海（天津）资产管理有限公司',u'00601':u'辽源鑫禹投资信息服务咨询有限公司',u'00602':u'永清县恒丰小额贷款有限公司',u'00603':u'信阳新阳实业有限公司',u'00604':u'重庆照创电子商务中心',u'00605':u'河南亿名威商贸有限公司',u'00606':u'中科信发（北京）资产管理有限公司',u'00608':u'贵州鸿骏通融资担保有限公司',u'00609':u'四川金鑫汇通投资有限公司',u'00610':u'重庆普麦投资咨询有限公司',u'00611':u'四川省蓉城金源非融资性担保有限公司',u'00612':u'重庆焱坤投资咨询有限公司',u'00613':u'宜宾市顺通投资信息咨询有限公司',u'00614':u'成都天耀行投资有限责任公司',u'00615':u'创宏河北企业管理咨询有限公司',u'00616':u'丹东宏悦投资管理有限公司',u'00617':u'兴宏（北京）资产管理有限公司广西分公司',u'00618':u'镇江利丰资产管理咨询有限公司',u'00619':u'廊坊市辉宇浩月投资有限公司',u'00620':u'聊城茂宏企业管理咨询有限公司',u'00621':u'聊城市腾翔置业有限公司',u'00622':u'唐山睿诚商务咨询服务有限公司',u'00623':u'秦皇岛俊华房地产经纪有限公司',u'00624':u'青岛群益惠投资咨询有限公司',u'00627':u'重庆彬立科技有限公司',u'00628':u'绵阳国创投资有限公司',u'00629':u'哈尔滨万和投资管理有限公司',u'00630':u'北京金源华信投资管理有限公司',u'00632':u'迁西县兴宏投资咨询有限公司',u'00633':u'黄骅市兴宏信用服务有限公司',u'00634':u'兴港（北京）资产管理有限公司',u'00641':u'兴宏（北京）资产管理有限公司三合金汇分公司',u'00642':u'天门亿创资产管理有限公司',u'00643':u'兴宏（北京）资产管理有限公司通州分公司',u'00644':u'黑龙江红兴隆农垦兴皓投资助贷咨询服务有限公司',u'00645':u'涿州市京阳润通投资有限公司',u'00646':u'北京豪威众达担保有限公司',u'00647':u'张家港市欣融鑫信息咨询服务有限公司',u'00662':u'郭新豪',u'00681':u'融金（北京）电子商务有限公司',u'00701':u'北京远洋华信资产管理有限公司',u'00702':u'淮安鹏程信息技术有限公司',u'00703':u'江阴市秋逸信息咨询服务有限公司',u'00704':u'连云港市安达经济信息咨询有限公司',u'00705':u'泰州共创广告传媒有限公司',u'00706':u'江苏二五八金融信息服务有限公司',u'00707':u'盐城祥吉抵押贷款咨询服务有限公司',u'00721':u'胡杰',u'00722':u'安徽本高商务管理有限公司淮南分公司',u'00723':u'江西玖壹金融服务有限公司',u'00724':u'安润金融信息服务（北京）有限公司',u'00724_2000':u'信息技术部',u'00724_2001':u'业务部',u'00724_2002':u'风控部',u'00724_2003':u'运营部',u'00724_2004':u'财务部',u'00724_2005':u'四子王旗营业部',u'00724_2006':u'天津分公司',u'00724_2007':u'烟台分公司',u'00724_2008':u'佛山分公司',u'00724_2009':u'苏尼特右旗营业部',u'00724_2010':u'安润金控',u'00724_2011':u'杭州久昌',u'00724_2012':u'沈阳泓轩',u'00724_2013':u'家电协会',u'00724_2014':u'首担担保',u'00724_2015':u'九江东汇薪融',u'00724_2016':u'千诚微金融',u'00724_2017':u'阜阳分公司',u'00724_2018':u'广州营业部',u'00724_2019':u'武川营业部',u'00725':u'荆州市华强商贸投资有限公司',u'00726':u'中亿普惠（北京）金融服务外包有限公司',u'00727':u'平顶山市瑞旗网络科技有限公司',u'00728':u'安徽金圆金融信息咨询有限公司',u'00729':u'武汉融广资产管理有限公司',u'00743':u'安徽富道金融信息咨询有限公司',u'00744':u'怀化恒兴商务咨询有限公司',u'00745':u'济南小米易贷投资管理有限公司',u'00746':u'宋伟',u'00748':u'无锡雷鼎投资管理有限公司',u'00749':u'余姚市恒宸信息咨询有限公司',u'00750':u'商丘市梁园区玮亚通讯器材维修部',u'00751':u'申光明',u'00752':u'武汉鑫鸿利源贸易有限公司',u'00754':u'湖南省赢和装修经纪人服务有限公司',u'00755':u'尹仲',u'00761':u'平顶山市豪弘商贸有限公司',u'00781':u'翁星星',u'00782':u'周口市开发区恩翔日化百货商行',u'00784':u'张豪磊',u'00786':u'驻马店市伟翔商贸有限公司',u'00789':u'南阳市巨匠汇装饰设计有限公司',u'00791':u'许昌欧威电子产品有限公司平顶山分公司',u'00801':u'河南九思普惠实业发展有限公司',u'00821':u'河南鑫昊企业管理咨询有限公司',u'00822':u'尚树俊',u'00823':u'刘攀',u'00824':u'南阳市宇辰信息技术有限公司',u'00825':u'平顶山市英联网络科技服务有限公司',u'00826':u'薛长富',u'00827':u'南阳海晟网络科技有限公司',u'00828':u'顾庆',u'00829':u'四川银信普惠金融服务外包有限公司',u'00830':u'上饶市优甫汽车服务有限公司',u'00841':u'心海集团有限责任公司',u'00843':u'湖北卡联商务服务有限公司荆州分公司',u'00844':u'桂林融通汽车销售有限公司',u'00845':u'广西锦玖贸易有限公司',u'00846':u'河南省竞合商贸有限公司',u'00847':u'大理市寰远经济信息咨询有限公司',u'00848':u'李娜',u'00861':u'新乡市伯爵汽车销售有限公司',u'00862':u'张超',u'00881':u'华信众筹（北京）信息咨询服务有限公司',u'00882':u'嘉兴市奇点贸易有限公司',u'00883':u'傅建飞',u'00884':u'安徽汇中鑫通投资管理有限责任公司',u'00885':u'海城市兴海区鑫明电子商务咨询中心',u'00886':u'柳州市赛斯贸易有限公司',u'00901':u'驻马店市驿城区羽凡网络科技有限公司',u'00902':u'广西玉林兴盾投资有限公司',u'00904':u'程红煜',u'00905':u'荆州宝德电子商务有限公司',u'00921':u'张婷婷',u'00922':u'鞍山华玺安阳投资咨询有限公司',u'00942':u'四川盛汇信通商务咨询有限公司',u'00943':u'抚州市临川区官华电器经营部',u'00944':u'惠金所',u'00944_2000':u'BJFD',u'00944_2001':u'BJFD02渠道经理',u'00944_2002':u'BJFD03渠道经理',u'00944_2003':u'BJFD04渠道经理',u'00944_2004':u'SZFD',u'00944_2005':u'SZFD02渠道经理',u'00944_2006':u'HZFD',u'00944_2007':u'HZFD02渠道经理',u'00944_2008':u'BJFD06渠道经理',u'00944_2009':u'BJYQCD01渠道经理',u'00944_2010':u'TJBLCD01渠道经理',u'00944_2011':u'SZCZHPZ01渠道经理',u'00944_2012':u'CCWSCD01渠道经理',u'00944_2013':u'CDFD',u'00944_2014':u'SZYWCD01渠道经理',u'00944_3000':u'BJFD01渠道经理',u'00944_3001':u'BJFD02渠道',u'00944_3002':u'BJFD03渠道',u'00944_3003':u'BJFD04渠道',u'00944_3004':u'SZFD01渠道经理',u'00944_3005':u'SZFD02渠道',u'00944_3006':u'HZFD01渠道经理',u'00944_3007':u'HZFD02渠道',u'00944_3008':u'BJFD06渠道',u'00944_3009':u'BJYQCD01渠道',u'00944_3010':u'TJBLCD01渠道',u'00944_3011':u'SZCZHPZ01渠道',u'00944_3012':u'CCWSCD01渠道',u'00944_3013':u'CDFD01渠道经理',u'00944_3014':u'SZYWCD01渠道',u'00945':u'河南沃邦网络科技有限公司',u'00961':u'东莞市金苍子实业投资有限公司',u'00982':u'于都县阳光五金经营店',u'01001':u'大连易快付网络科技有限公司',u'01003':u'宿迁日升汽车服务有限公司',u'01005':u'晋商消费金融股份有限公司',u'01005_2000':u'北京市海淀区名人视线造型艺术培训学校',u'01005_2001':u'温州裕鼎宏网络信息咨询服务有限公司',u'01005_2002':u'摩托邦总部',u'01005_2003':u'山西博海易联通信科技有限公司',u'01005_2004':u'山西九艺装饰工程设计有限公司',u'01005_2005':u'上海厚本金融信息服务有限公司',u'01005_2006':u'山西易联支付数据处理有限公司',u'01005_2007':u'山西威特安能能源科技有限公司',u'01005_2008':u'太原兴鹏伟业贸易有限公司',u'01005_2009':u'银河金服',u'01005_2010':u'美丽分期',u'01005_2011':u'黑龙江红兴隆农垦管理局(总部）',u'01005_2012':u'惠人贷商务顾问（北京）有限公司',u'01005_2013':u'北京淏泽源国际文化发展有限公司',u'01005_2014':u'山西君和源投资咨询有限公司',u'01005_2015':u'深圳市沃特尔科技有限公司',u'01005_2016':u'妙笔菡塘（北京）文化传播有限公司',u'01005_2017':u'引行金融信息服务（上海）有限公司',u'01005_2018':u'北京华世中瑞科技有限公司',u'01005_2019':u'上海万国',u'01005_2020':u'广州万国',u'01005_2021':u'北京电销',u'01005_2022':u'北京万国',u'01005_2023':u'沈阳万国',u'01005_2024':u'太原市万柏林区非池文化艺术培训中心',u'01005_2025':u'深圳博纳互联网金融服务有限公司',u'01005_2028':u'智富金融信息服务（上海）有限公司',u'01005_2029':u'北京华世中瑞科技有限公司',u'01005_2030':u'上海通善互联网金融信息服务有限公司',u'01005_2031':u'山西易凯国际旅游有限公司',u'01005_2032':u'北京融联世纪信息技术有限公司',u'01005_2033':u'山西巨绩二手车经纪有限公司',u'01005_2034':u'北京你我他互学数据科技股份有限公司',u'01005_2035':u'成都吉瑞纳杰商务服务有限公司',u'01005_2036':u'可可家里（北京）信息技术有限公司',u'01005_2037':u'北京万众信用管理有限公司',u'01005_2038':u'南京颂恩凯商务咨询有限公司',u'01005_2039':u'元正融资租赁（上海）有限公司',u'01005_2040':u'中望金服信息科技（北京）有限公司',u'01005_2041':u'四川亿信通资产管理有限公司',u'01005_3000':u'温州营业部',u'01005_3001':u'山西博海易联通信科技有限公司',u'01005_3002':u'VIVO店',u'01005_3003':u'OPPO店',u'01005_3004':u'华为二店',u'01005_3005':u'华为一店',u'01005_3006':u'4G店',u'01005_3007':u'厚本金融（邢台门店）',u'01005_3008':u'厚本金融（南充门店）',u'01005_3009':u'厚本金融（晋中门店）',u'01005_3010':u'厚本金融（上海门店）',u'01005_3011':u'厚本金融（太原门店）',u'01005_3012':u'厚本金融（天津门店）',u'01005_3013':u'厚本金融（乐山门店）',u'01005_3014':u'厚本金融（福州门店）',u'01005_3015':u'厚本金融（承德门店）',u'01005_3016':u'厚本金融（武汉门店）',u'01005_3017':u'易联支付（晋中办事处）',u'01005_3018':u'易联支付（大同办事处）',u'01005_3019':u'易联支付（吕梁办事处）',u'01005_3020':u'易联支付（运城办事处）',u'01005_3021':u'易联支付（忻州办事处）',u'01005_3022':u'易联支付（长治办事处）',u'01005_3023':u'易联支付（晋城办事处）',u'01005_3024':u'易联支付（朔州办事处）',u'01005_3025':u'易联支付（阳泉办事处）',u'01005_3026':u'易联支付（临汾办事处）',u'01005_3027':u'易联支付（太原营业部）',u'01005_3028':u'山西威特安能能源科技有限公司',u'01005_3029':u'厚本金融（运营总部）',u'01005_3030':u'太原市万柏林区新森园家俱经销部',u'01005_3031':u'襄阳正大',u'01005_3032':u'兰州正大',u'01005_3033':u'美分期-幸福医疗',u'01005_3034':u'美分期-美玉颜',u'01005_3035':u'瑞安营业部（快易贷房产类）',u'01005_3036':u'北京淏泽源国际文化发展有限公司沈阳办事处',u'01005_3037':u'北京淏泽源国际文化发展有限公司河南分公司',u'01005_3038':u'北京新生代人力资源有限责任公司',u'01005_3039':u'北京淏泽源国际文化发展有限公司无锡分公司',u'01005_3040':u'北京淏泽源国际文化发展有限公司上海办事处',u'01005_3041':u'山西君和源投资咨询有限公司',u'01005_3042':u'台州营业部',u'01005_3043':u'深圳市沃特尔科技有限公司山西分公司',u'01005_3044':u'美分期-当代医疗',u'01005_3045':u'山西分校',u'01005_3046':u'北京分校',u'01005_3047':u'引行金融-北京微贷中心',u'01005_3048':u'引行金融-北京丰台分行',u'01005_3049':u'引行金融-内蒙古通辽分行',u'01005_3050':u'引行金融-内蒙古鹿城分行',u'01005_3051':u'引行金融-辽宁葫芦岛分行',u'01005_3052':u'引行金融-河北保定分行',u'01005_3053':u'引行金融-北京朝阳分行',u'01005_3054':u'引行金融-内蒙古青城分行',u'01005_3055':u'引行金融-内蒙古赤峰分行',u'01005_3056':u'引行金融-内蒙古呼市分行',u'01005_3057':u'引行金融-内蒙古包头分行',u'01005_3058':u'引行金融-北京总部',u'01005_3059':u'厚本金融（常州门店）',u'01005_3060':u'厚本金融（吴忠门店）',u'01005_3061':u'厚本金融（贵阳门店）',u'01005_3062':u'厚本金融（长沙门店）',u'01005_3063':u'厚本金融（包头门店）',u'01005_3064':u'厚本金融（连云港门店）',u'01005_3065':u'厚本金融（衡水门店）',u'01005_3066':u'厚本金融（南阳门店）',u'01005_3067':u'厚本金融（黄石门店）',u'01005_3068':u'厚本金融（岳阳门店）',u'01005_3069':u'厚本金融（深圳门店）',u'01005_3070':u'厚本金融（湛江门店）',u'01005_3071':u'厚本金融（南宁门店）',u'01005_3072':u'厚本金融（日照门店）',u'01005_3073':u'厚本金融（廊坊门店）',u'01005_3074':u'厚本金融（沧州门店）',u'01005_3075':u'厚本金融（银川门店）',u'01005_3076':u'厚本金融（徐州门店）',u'01005_3077':u'厚本金融（梧州门店）',u'01005_3078':u'厚本金融（安康门店）',u'01005_3079':u'可可乐行山西总部',u'01005_3080':u'可可乐行（车居尚汽车服务会所）',u'01005_3081':u'可可乐行（车邦士汽车服务）',u'01005_3082':u'可可乐行（河津相逢汽车服务部）',u'01005_3083':u'可可乐行（运城尊尚汽车会所）',u'01005_3084':u'可可乐行（运城天诚汽修）',u'01005_3085':u'可可乐行（太原市幽幽幽汽车服务有限公司）',u'01005_3086':u'美分期-薇琳医疗',u'01005_3087':u'非池文化艺术培训中心',u'01005_3088':u'深圳博纳总部',u'01005_3089':u'山西正大',u'01005_3091':u'智富徐州分公司',u'01005_3092':u'智富常州分公司',u'01005_3093':u'智富长沙分公司',u'01005_3094':u'智富厦门分公司',u'01005_3095':u'智富昆明分公司',u'01005_3096':u'智富马鞍山分公司',u'01005_3097':u'智富泰州分公司',u'01005_3098':u'智富宁波分公司',u'01005_3099':u'智富金融总部',u'01005_3100':u'上海通善互联网金融信息服务有限公司上海营业部',u'01005_3101':u'山西易凯国际旅游有限公司',u'01005_3102':u'北京融联世纪信息技术有限公司',u'01005_3103':u'杭州营业部',u'01005_3104':u'山西巨绩二手车经纪有限公司',u'01005_3105':u'武汉万国',u'01005_3106':u'天津万国',u'01005_3107':u'太原万国',u'01005_3108':u'南宁万国',u'01005_3109':u'海口万国',u'01005_3110':u'昆明万国',u'01005_3111':u'济南万国',u'01005_3112':u'杭州万国',u'01005_3113':u'成都营业部',u'01005_3114':u'厚本金融（太原二门店）',u'01005_3115':u'厚本金融（临汾门店）',u'01005_3116':u'厚本金融（达州门店）',u'01005_3117':u'厚本金融（宜宾门店）',u'01005_3118':u'孟州市顺超汽修部',u'01005_3119':u'濮阳市濮上路中信汽车服务店',u'01005_3120':u'郑州市郑东新区恒驰轮胎汽车用品服务中心',u'01005_3121':u'无锡美车坊名车会所',u'01005_3122':u'运城市空港开发区乾得龙汽车美容中心',u'01005_3123':u'晋城市利轩工贸有限公司第一公司',u'01005_3124':u'山西新乐行信息技术有限公司',u'01005_3125':u'南阳顺航汽车用品',u'01005_3126':u'河南长葛市马军汽修',u'01005_3127':u'威威汽车维修一站式服务',u'01005_3128':u'林州市众汽维修中心',u'01005_3129':u'焦作市新东方汽车修理有限公司',u'01005_3130':u'淮安东南汽车销售服务有限公司',u'01005_3131':u'可可家里总部',u'01005_3132':u'久速汽车销售有限公司',u'01005_3133':u'苏州市苏州1989贸易有限公司',u'01005_3134':u'南京坤泰汽车服务有限公司',u'01005_3135':u'北京万众信用管理有限公司总部',u'01005_3136':u'小古汽服',u'01005_3137':u'上海捷通汽车服务中心',u'01005_3138':u'永信汽车用品',u'01005_3139':u'上海宝驿汽车修有限公司',u'01005_3140':u'鑫鑫汽车维修换油中心',u'01005_3141':u'龙亭区车爵士汽车美容装饰',u'01005_3142':u'亚之星汽车修理有限公司',u'01005_3143':u'宏宾伟业',u'01005_3144':u'北京现代东仁环宇店',u'01005_3145':u'韩城市禹道修理厂',u'01005_3146':u'车仆恒耀汽车美容养护连锁',u'01005_3147':u'铜川新区大山养护中心',u'01005_3148':u'上海捷通汽车服务中心',u'01005_3149':u'畅行汽车修理厂',u'01005_3150':u'集宁信达汽车修理厂',u'01005_3151':u'天和汽车维修会所',u'01005_3152':u'众利汽修',u'01005_3153':u'雅博汽车修理厂',u'01005_3154':u'鄂尔多斯市盛通汽车美容中心',u'01005_3155':u'众鑫汽车服务有限公司',u'01005_3156':u'钢铁西街汽车修理厂',u'01005_3157':u'内蒙古百得利名车专修',u'01005_3158':u'鑫富达汽车修理厂',u'01005_3159':u'内蒙古云岭物联信息技术有限公司',u'01005_3160':u'东禹车饰',u'01005_3161':u'保时洁',u'01005_3162':u'爱卡联盟汽车服务连锁',u'01005_3163':u'蚌埠经济开发区五一五机油快修连锁店',u'01005_3164':u'淮南方信科维信息技术有限公司',u'01005_3165':u'全椒县鸿顺汽修美容中心',u'01005_3166':u'安徽凯撒名车',u'01005_3167':u'宏宇汽车美容装饰中心',u'01005_3168':u'森林雨汽车服务',u'01005_3169':u'榆林市榆阳区行车无忧汽车服务有限公司',u'01005_3170':u'西安市可可家里',u'01005_3171':u'鸿宇汽车美容装饰',u'01005_3172':u'六盘水可可乐行',u'01005_3173':u'贵阳可可乐行科技有限公司',u'01005_3174':u'温州市可可乐行科技有限公司',u'01005_3175':u'车臣汽车用品店',u'01005_3176':u'信合汽车租赁',u'01005_3177':u'沧州可可乐行',u'01005_3178':u'永一汽车美容装饰店',u'01005_3179':u'振兴汽车装具',u'01005_3180':u'百事达汽车养护中心',u'01005_3181':u'易县浩辉汽车用品经销处',u'01005_3182':u'可可乐行河北总代理驻秦皇岛办事处',u'01005_3183':u'可可乐行邯郸经销商',u'01005_3184':u'河北安驰汽车租赁公司',u'01005_3185':u'武汉爱乐行信息技术有限公司',u'01005_3186':u'十堰市可可顺通电子科技有限公司',u'01005_3187':u'好多亿信息科技有限公司',u'01005_3188':u'天津市人民政府机关汽车修理厂',u'01005_3189':u'湖南阳升信息技术有限公司',u'01005_3190':u'临沂市兰山区轩轮汽车饰品经营部',u'01005_3191':u'环翠区艺玮汽车美容中心',u'01005_3192':u'菏泽RGB高端汽车养护中心',u'01005_3193':u'聊城市利源车饰用品',u'01005_3194':u'青岛丰慧汽车用品有限公司',u'01005_3195':u'汽车公馆',u'01005_3196':u'庆云宏发汽车装具门饰',u'01005_3197':u'烟台众悦信息技术服务有限公司',u'01005_3198':u'日照市东港区东盛汽车装饰美容中心',u'01005_3199':u'酷车饰界',u'01005_3200':u'智富海口分公司',u'01005_3201':u'智富郑州分公司',u'01005_3202':u'智富安庆分公司',u'01005_3203':u'智富合肥第二分公司',u'01005_3204':u'智富南通分公司',u'01005_3205':u'智富蚌埠分公司',u'01005_3206':u'智富南宁分公司',u'01005_3207':u'智富昆山分公司',u'01005_3208':u'智富嘉兴分公司',u'01005_3209':u'智富西安分公司',u'01005_3210':u'智富苏州分公司',u'01005_3211':u'智富镇江分公司',u'01005_3212':u'智富石家庄分公司',u'01005_3213':u'智富唐山分公司',u'01005_3214':u'智富济南分公司',u'01005_3215':u'智富芜湖分公司',u'01005_3216':u'智富合肥第一分公司',u'01005_3217':u'智富江阴分公司',u'01005_3218':u'智富张家港分公司',u'01005_3219':u'智富南昌分公司',u'01005_3220':u'智富太原分公司',u'01005_3221':u'智富赣州分公司',u'01005_3222':u'智富宜兴分公司',u'01005_3223':u'智富无锡分公司',u'01005_3224':u'智富宜宾分公司',u'01005_3225':u'智富玉溪分公司',u'01005_3226':u'南京奥体中心店',u'01005_3227':u'长沙万国',u'01005_3228':u'南京万国',u'01005_3229':u'合肥万国',u'01005_3230':u'重庆万国',u'01005_3231':u'长春万国',u'01005_3232':u'西安万国',u'01005_3233':u'南昌万国',u'01005_3234':u'兰州万国',u'01005_3235':u'哈尔滨万国',u'01005_3236':u'成都万国学校',u'01005_3237':u'环县中昌汽车租赁有限公司',u'01005_3238':u'内蒙古极速名车信息服务有限公司',u'01005_3239':u'上海路宜汽车租赁有限公司',u'01005_3240':u'邯郸市联茂汽车贸易有限公司',u'01005_3241':u'河南新乡车邦贷汽车销售服务有限公司',u'01005_3242':u'郑州嘉业汽车销售有限公司',u'01005_3243':u'甘肃中汇商务有限公司武威分公司',u'01005_3244':u'甘肃中汇商务有限公司酒泉分公司',u'01005_3245':u'甘肃中汇商务有限公司',u'01005_3246':u'西安融掮企业信息咨询服务有限公司',u'01005_3247':u'西安融本新能源有限公司',u'01005_3248':u'陕西巨捷汽车信息咨询服务有限公司',u'01005_3249':u'中望金服无锡服务中心',u'01005_3250':u'中望金服镇江服务中心',u'01005_3251':u'中望金服淮安服务中心',u'01005_3252':u'中望金服宣城服务中心',u'01005_3253':u'中望金服合肥服务中心',u'01005_3254':u'中望金服佛山服务中心',u'01005_3255':u'中望金服清远服务中心',u'01005_3256':u'中望金服海口服务中心',u'01005_3257':u'中望金服广州服务中心',u'01005_3258':u'亿信通陇南分公司',u'01005_3259':u'亿信通泸州分公司',u'01005_3260':u'亿信通内江分公司',u'01005_3261':u'亿信通邛崃分公司',u'01005_3262':u'亿信通汉源分公司',u'01005_3263':u'亿信通广元分公司',u'01005_3264':u'亿信通雅安分公司',u'01005_3265':u'亿信通蒲江分公司',u'01005_3266':u'四川亿信通资产管理有限公司',u'01021':u'红河州凌本信息技术服务有限公司',u'01022':u'江西帕廷顿投资发展有限公司',u'01023':u'西湖区鹏仔电器批发部',u'01041':u'蒋金祥',u'01042':u'抚州市信大金信息服务有限公司',u'01043':u'何燕',u'01061':u'钱包金服（北京）科技有限公司',u'01061_2000':u'客如云',u'01061_2001':u'钱包生活',u'01082':u'平台演示公司',u'01101':u'数据服务专用演示',u'01101_2000':u'江南金行',u'01101_2001':u'上海星湖',u'01141':u'西安鼎盛典当有限责任公司',u'01141_2000':u'民生财务',u'01141_2001':u'典当资金财务',u'01141_3000':u'民生百货大楼',u'01141_3001':u'民生百货西大街店',u'01141_3002':u'民生百货庆阳店',u'01141_3003':u'民生电子城店',u'01141_3004':u'民生百货骡马市店',u'01141_3005':u'民生百货钟楼店',u'01141_3006':u'民生百货曲江店',u'01141_3007':u'民生百货延安店',u'01141_3008':u'民生百货五路口店',u'01141_3009':u'民生百货文景店',u'01141_3010':u'民生百货龙首店',u'01141_3011':u'民生百货长安店',u'01141_3012':u'O2O网上商城',u'900000000':u"宇信科技"}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(XindaiyunSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def start_requests(self):

        # csvfile = file('yuxin_%s.csv'%time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), 'wb')
        #
        # writer = csv.writer(csvfile)

        yield Request(self.logins_url)


    def parse(self, response):

        self.sess = {}

        cookie = [i.split(";")[0] for i in response.headers.getlist('Set-Cookie')]

        for cook in cookie:
            self.sess.update({cook[:cook.index("=")]: cook[cook.index("=") + 1:]})

        username = "xxxx"

        passwd = "xxxx"

        login_url = "http://ep.duohaojr.com/userSignOn.do"

        post_data = {
            "currentUserId": "%s"%username,
            "password":"%s"%passwd,
            "text1":"验证码",
            "realIp":"111.200.62.30",
            "browserInfo":"名称：Netscape**版本：5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36**信息:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
                    }

        yield FormRequest(login_url,cookies=self.sess,formdata=post_data,callback=self.save_session)

    def save_session(self, response):

        hxs = HtmlXPathSelector(response)

        name = "".join(hxs.xpath("//span[@class='admin_02']/text()").extract())

        if name == "":

            response.request.dont_filter = True

            yield response.request

        else:

            logging.warning(msg="%s"%name)

            self.emp_id = "".join(hxs.xpath("//script[@type='text/javascript'][1]/text()").re(r"empId\s=\s+?'([\S]+?)';")[0])

            save_session_url = "http://ep.duohaojr.com/saveCurrentRoleLogo.do?EMP_SID=%s&curRoleLogo=03" % self.emp_id

            yield FormRequest(url=save_session_url,callback=self.parse_detail)

    def parse_detail(self,response):

        if "系统出现异常" in response.body:

            response.request.dont_filter = True

            yield response.request

        else:

            post_data = {
                "page": "1",
                "rows": "10",

            }

            if int(self.settings["USELOCALIP"])==1:

                loan_url = "http://ep.duohaojr.com/queryLmLoanListForLmPmShdAction.do?EMP_SID=%s"

                yield FormRequest(url=loan_url% self.emp_id, callback=self.parse_pagenos, formdata=post_data,meta={"ur":loan_url})

                surp_url = "http://ep.duohaojr.com/lcappl/queryHkbbList4Anrun.do?EMP_SID=%s"

                yield FormRequest(url=surp_url % self.emp_id, callback=self.parse_pagenos, formdata=post_data,
                                  meta={"ur": surp_url})
            else:

                contact_url = "http://ep.duohaojr.com/queryContList4AnRun.do?EMP_SID=%s"

                yield FormRequest(url=contact_url% self.emp_id,callback=self.parse_pagenos,formdata=post_data,meta={"ur":contact_url})

    def parse_pagenos(self,response):

        if "系统出现异常" in response.body:

            response.request.dont_filter = True

            yield response.request

        else:

            url = response.meta[u"ur"]

            try:

                j_read = json.loads(response.body.decode("utf8").replace(" ",""))

            except Exception,e:

                print e

                print response.body

                yield response.request

            total_count = int(j_read[u"total"])

            page_nos = total_count/50 if total_count%50==0 else total_count/50+1

            url = url % self.emp_id

            if "queryLmLoanListForLmPmShdAction.do" in url:

                cb = self.parse_loan

            elif "http://ep.duohaojr.com/queryContList4AnRun.do" in url:

                cb = self.parse_contact
            else:

                cb = self.parse_surp

            for page_no in range(1,page_nos):

                #post_data = "page=%s&rows=10&sort=loan_tnr&order=desc" % page_no

                post_data = {
                    "page":str(page_no),
                    "rows":"50",
                }

                yield FormRequest(url, callback=cb, formdata=post_data,dont_filter=True,meta={"pagenos":page_no})

    def parse_contact(self, response):

        pagenos = response.meta["pagenos"]

        if "系统出现异常" in response.body:

            response.request.dont_filter = True

            yield response.request

        else:

            j_read = json.loads(response.body.decode("utf8").replace(" ", ""))

            for row in j_read[u"rows"]:

                items = {}

                items[u"合同号"] = row[u"cont_no"]

                items[u"进件编号"] = row[u"doc_num"]

                items[u"客户名称"] = row[u"cust_name"]

                items[u"证件号码"] = row[u"id_no"]

                items[u"合同金额"] = row[u"apprv_amt"]

                items[u"贷款期限"] = row[u"apprv_tnr"]

                items[u"申请日期"] = row[u"apply_dt"]

                items[u"签约登记日期"] = row[u"sign_dt"]

                url= "http://ep.duohaojr.com/viewApplContPage.do?EMP_SID=%s&applSeq=%s&returnURL=queryLoanListPage4AnRun&pageFlag=forAnRun"%(self.emp_id,row[u"appl_seq"])

                yield Request(url=url,callback=self.parse_contact_info,meta={"items":items,u"cont_no":row[u"cont_no"],"pagenos":pagenos})

    def parse_contact_info(self,response):

        if "系统出现异常" in response.body:

            response.request.dont_filter = True

            yield response.request

        else:

            itemss_list = []

            items = response.meta[u"items"]

            itemss_list.append(items)

            cont_no = response.meta[u"cont_no"]

            hxs = HtmlXPathSelector(response)

            item = {}

            item[u'申请人名称'] = "".join(hxs.xpath(u"//td[text()='申请人名称：']/following-sibling::td[1]/input/@value").extract())

            item[u'证件类型'] = self.id_type[unicode("".join(hxs.xpath(u"//td[text()='证件类型：']/following-sibling::td[1]/input/@defaultVal").extract()))]

            item[u'证件号码'] = "".join(hxs.xpath(u"//td[text()='证件号码：']/following-sibling::td[1]/input/@value").extract())

            item[u'经营实体性质'] = self.business_type[unicode("".join(hxs.xpath(u"//td[text()='经营实体性质：']/following-sibling::td[1]/input/@defaultVal").extract()))]

            item[u'经营实体名称'] = "".join(hxs.xpath(u"//td[text()='经营实体名称：']/following-sibling::td[1]/input/@value").extract())

            item[u'经营实体类型'] = "".join(hxs.xpath(u"//td[text()='经营实体类型：']/following-sibling::td[1]/input/@defaultVal").extract())

            item[u'成立日期'] = "".join(hxs.xpath(u"//td[text()='成立日期：']/following-sibling::td[1]/input/@value").extract())

            item[u'经营实体注册号'] = "".join(hxs.xpath(u"//td[text()='经营实体注册号：']/following-sibling::td[1]/input/@value").extract())

            item[u'营业执照号码'] = "".join(hxs.xpath(u"//td[text()='营业执照号码：']/following-sibling::td[1]/input/@value").extract())

            item[u'营业执照注册日期'] = "".join(hxs.xpath(u"//td[text()='营业执照注册日期：']/following-sibling::td[1]/input/@value").extract())

            item[u'营业执照到期日'] = "".join(hxs.xpath(u"//td[text()='营业执照到期日：']/following-sibling::td[1]/input/@value").extract())

            item[u'经营场所所有权'] = self.house_type[unicode("".join(hxs.xpath(u"//td[text()='经营场所所有权：']/following-sibling::td[1]/input/@defaultVal").extract()))]

            item[u'租赁到期日'] = "".join(hxs.xpath(u"//td[text()='租赁到期日：']/following-sibling::td[1]/input/@value").extract())

            item[u'职工人数'] = "".join(hxs.xpath(u"//td[text()='职工人数：']/following-sibling::td[1]/input/@value").extract())

            item[u'月均营业额(元)'] = "".join(hxs.xpath(u"//td[text()='月均营业额(元)：']/following-sibling::td[1]/input/@value").extract())

            item[u'联系电话'] = "".join(hxs.xpath(u"//td[text()='联系电话：']/following-sibling::td[1]/input/@value").extract())

            item[u'申请人身份'] = self.company_member_type[unicode("".join(hxs.xpath(u"//td[text()='申请人身份：']/following-sibling::td[1]/input/@defaultVal").extract()))]

            item[u'持股比例(%)'] = "".join(hxs.xpath(u"//td[text()='持股比例(%)：']/following-sibling::td[1]/input/@value").extract())

            item[u'总工龄(年)'] = "".join(hxs.xpath(u"//td[text()='总工龄(年)：']/following-sibling::td[1]/input/@value").extract())

            item[u'现单位工龄(年)'] = "".join(hxs.xpath(u"//td[text()='现单位工龄(年)：']/following-sibling::td[1]/input/@value").extract())

            item[u'注册地址'] = "".join(hxs.xpath(u"//td[text()='注册地址：']/following-sibling::td[1]/input/@value").extract())

            item[u'经营地址'] = "".join(hxs.xpath(u"//td[text()='经营地址：']/following-sibling::td[1]/input/@value").extract())

            item[u'注册地址邮编'] = "".join(hxs.xpath(u"//td[text()='注册地址邮编：']/following-sibling::td[1]/input/@value").extract())

            item[u'经营地址邮编'] = "".join(hxs.xpath(u"//td[text()='经营地址邮编：']/following-sibling::td[1]/input/@value").extract())

            item[u'主营业务'] = "".join(hxs.xpath(u"//td/div[text()='主营业务：']/following-sibling::td[1]/text()").extract())

            item[u'其他情况描述'] = "".join(hxs.xpath(u"//td/div[text()='其他情况描述：']/following-sibling::td[1]/text()").extract())

            item[u'贷款品种'] = self.loan_type_name[unicode("".join(hxs.xpath(u"//td[text()='贷款品种：']/following-sibling::td[1]/input/@defaultVal").extract()))]

            item[u'申请日期'] = "".join(hxs.xpath(u"//td[text()='申请日期：']/following-sibling::td[1]/input/@value").extract())

            item[u'审批期限'] = "".join(hxs.xpath(u"//td[text()='审批期限：']/following-sibling::td[1]/input/@value").extract())

            item[u'审批金额(元)'] = "".join(hxs.xpath(u"//td[text()='审批金额(元)：']/following-sibling::td[1]/input/@value").extract())

            item[u'还款方式'] = self.interest_type[unicode("".join(hxs.xpath(u"//td[text()='还款方式：']/following-sibling::td[1]/input/@defaultVal").extract()))]

            item[u'借款年利率(%)'] = "".join(hxs.xpath(u"//td[text()='借款年利率(%)：']/following-sibling::td[1]/input/@value").extract())

            item[u'逾期罚息利率(%)'] = "".join(hxs.xpath(u"//td[text()='逾期罚息利率(%)：']/following-sibling::td[1]/input/@value").extract())

            item[u'合同金额(元)'] = "".join(hxs.xpath(u"//td[text()='合同金额(元)：']/following-sibling::td[1]/input/@value").extract())

            item[u'放款金额(元)'] = "".join(hxs.xpath(u"//td[text()='放款金额(元)：']/following-sibling::td[1]/input/@value").extract())

            item[u'合同起始日期'] = "".join(hxs.xpath(u"//td[text()='合同起始日期：']/following-sibling::td[1]/input/@value").extract())

            item[u'合同结束日期'] = "".join(hxs.xpath(u"//td[text()='合同结束日期：']/following-sibling::td[1]/input/@value").extract())

            account_name = hxs.xpath(u"//td[text()='账号户名：']/following-sibling::td[1]/input/@value").extract()

            item[u'放款_账号户名'] = "".join(account_name[0] if len(account_name)==1 else account_name)

            account_no = hxs.xpath(u"//td[text()='账号/卡号：']/following-sibling::td[1]/input/@value").extract()

            item[u'放款_账号/卡号'] = "".join(account_no[0] if len(account_no)==1 else account_no)

            item[u'放款_开户银行'] = self.bank_type[unicode("".join(hxs.xpath(u"//td[text()='开户银行：']/following-sibling::td[1]/div/input/@defaultVal").extract()))]

            account_department = hxs.xpath(u"//td[text()='开户机构：']/following-sibling::td[1]/input/@value").extract()

            item[u'放款_开户机构'] = "".join(account_department[0] if len(account_department)==1 else account_department)

            item[u'还款_账号户名'] = "".join(account_name[1] if len(account_name)==2 else "")

            item[u'还款_账号/卡号'] = "".join(account_no[1] if len(account_no)==2 else "")

            item[u'还款_开户银行'] = self.bank_type[unicode(
                "".join(hxs.xpath(u"//td[text()='开户银行：']/following-sibling::td[1]/input/@defaultVal").extract()))]

            item[u'还款_开户机构'] = "".join(account_department[1] if len(account_department)==2 else "")

            item[u'客户经理'] = self._members[unicode(
                "".join(hxs.xpath(u"//td[text()='客户经理：']/following-sibling::td[1]/input/@defaultVal").extract()))]

            item[u'登记日期'] = "".join(
                hxs.xpath(u"//td[text()='登记日期：']/following-sibling::td[1]/input/@value").extract())

            item[u'登记人员'] = self._members[unicode(
                "".join(hxs.xpath(u"//td[text()='登记人员：']/following-sibling::td[1]/input/@defaultVal").extract()))]

            item[u'进件编号'] = "".join(
                hxs.xpath(u"//td[text()='进件编号：']/following-sibling::td[1]/input/@value").extract())

            itemss_list.append(item)

            self.cont_items.update({cont_no:itemss_list})

    def parse_surp(self, response):

        if "系统出现异常" in response.body:

            response.request.dont_filter = True

            yield response.request

        else:

            try:

                j_read = json.loads(response.body.decode("utf8").replace(" ", ""))

            except Exception,e:

                print e

                print response.body

                return

            for row in j_read[u"rows"]:

                item = {}

                item[u"合同号"] = row[u"loan_cont_no"]

                item[u"客户名称"] = row[u"cust_name"]

                item[u"放款日期"] = row[u"loan_actv_dt"]

                item[u"首次还款日"] = row[u"first_pay_dt"]

                item[u"最近还款日"] = row[u"last_pay_dt"]

                item[u"贷款品种"] = row[u"loan_typ"]

                item[u"放款金额"] = row[u"loan_amt"]

                item[u"贷款期限"] = row[u"tnr"]

                item[u"还款方式"] = row[u"loan_paym_mtd"]

                item[u"应还总额"] = row[u"all_need_pay_amt"]

                item[u"已还本金"] = row[u"pay_base_amt"]

                item[u"贷款余额"] = row[u"surp_amt"]

                item[u"收费项目"] = row[u"col_fee"]

                item[u"收费金额"] = row[u"real_fee"]

                item[u"违约金"] = row[u"weiyue_fee"]

                item[u"逾期费用"] = row[u"due_fee"]

                item[u"逾期金额"] = row[u"due_amt"]

                item[u"贷款状态"] = row[u"due_sts"]

                item[u"登记人员"] = self._members[row[u"operator_cde"]]

                item[u"客户经理"] = self._members[row[u"crt_usr"]]

                item[u"所属机构"] = self.department[row[u"bch_cde"]]

                item[u"进件编号"] = row[u"doc_num"]

                self.surp_items.update({row[u"loan_cont_no"]:[item]})




    def parse_loan(self, response):

        if "系统出现异常" in response.body:

            response.request.dont_filter = True

            yield response.request

        else:

            try:

                j_read = json.loads(response.body.decode("utf8").replace(" ", ""))

            except Exception,e:

                print e

                print response.body

                return

            for row in j_read[u"rows"]:

                items = {}

                items.update({u'贷款合同号':row[u"cmis_loan_cont_no"]})

                items.update({u'借据号':row[u"loan_no"]})

                items.update({u'客户名称':row[u"cust_name"]})

                items.update({u'证件号码': row[u"id_no"]})

                items.update({u'贷款品种': self.loan_type_name[row[u"loan_typ"]]})

                items.update({u'期限': row[u"loan_tnr"]})

                items.update({u'还款间隔':self.pay_type[row[u"paym_freq_unit"]]})

                items.update({u'发放金额(元)':row[u"orig_prcp"]})

                items.update({u'剩余本金(元)':row[u"loan_os_prcp"]})

                items.update({u'放款日期':row[u"loan_actv_dt"]})

                post_data = {
                    "loan_no":row[u"loan_no"],
                    "sort":"ps_perd_no",
                    "order":"asc",
                }

                url = "http://ep.duohaojr.com/queryLmPmShdForLmPmShdAction.do?EMP_SID=%s"%self.emp_id

                yield FormRequest(url=url,formdata=post_data,callback=self.parse_loan_detail,meta={"items":items,u"loan_no":row[u"loan_no"]})


    def parse_loan_detail(self, response):

        if "系统出现异常" in response.body:

            response.request.dont_filter = True

            yield response.request

        else:

            itemss_list = []

            items = response.meta[u"items"]

            itemss_list.append(items)

            loan_no = response.meta[u"loan_no"]

            try:

                j_read = json.loads(response.body.decode("utf8").replace(" ", ""))

            except Exception,e:

                print e

                print response.body

                return

            for row in j_read[u"rows"]:

                item = {}

                item[u"期号"] = row[u"ps_perd_no"]

                item[u"到期日"] = row[u"ps_due_dt"]

                item[u"期供金额"] = row[u"ps_instm_amt"]

                item[u"本金"] = row[u"ps_prcp_amt"]

                item[u"利息"] = row[u"ps_norm_int_amt"]

                item[u"罚息"] = row[u"ps_od_int_amt"]

                item[u"复利"] = row[u"ps_comm_od_int"]

                item[u"剩余本金"] = row[u"ps_rem_prcp"]

                item[u"已还本金 "] = row[u"setl_prcp"]

                item[u"已还利息"] = row[u"setl_norm_int"]

                item[u"已还罚息"] = row[u"setl_od_int_amt"]

                item[u"已还复利"] = row[u"setl_comm_od_int"]

                item[u"应还滞纳金"] = row[u"ps_fee"]

                item[u"已还滞纳金"] = row[u"setl_fee"]

                item[u"应还账户管理费"] = row[u"ps_fee_amt"]

                item[u"已还账户管理费"] = row[u"setl_fee_amt"]

                item[u"减免利息"] = row[u"ps_wv_nm_int"]

                item[u"减免罚息"] = row[u"ps_wv_od_int"]

                item[u"减免复利"] = row[u"ps_wv_comm_int"]

                item[u"逾期标志"] = self.tag[row[u"ps_od_ind"]]

                item[u"结清标志"] = self.tag[row[u"setl_ind"]]

                itemss_list.append(item)

            for row in [j_read[u"footer"][0]]:

                item = {}

                item[u"期号"] = row[u"ps_perd_no"]

                item[u"本金"] = row[u"ps_prcp_amt"]

                item[u"利息"] = row[u"ps_norm_int_amt"]

                item[u"罚息"] = row[u"ps_od_int_amt"]

                item[u"复利"] = row[u"ps_comm_od_int"]

                item[u"已还本金 "] = row[u"setl_prcp"]

                item[u"已还利息"] = row[u"setl_norm_int"]

                item[u"已还罚息"] = row[u"setl_od_int_amt"]

                item[u"已还复利"] = row[u"setl_comm_od_int"]

                item[u"应还滞纳金"] = row[u"ps_fee"]

                item[u"已还滞纳金"] = row[u"setl_fee"]

                item[u"应还账户管理费"] = row[u"ps_fee_amt"]

                item[u"已还账户管理费"] = row[u"setl_fee_amt"]

                item[u"减免罚息"] = row[u"ps_wv_od_int"]

                item[u"减免复利"] = row[u"ps_wv_comm_int"]

                itemss_list.append(item)

            for row in [j_read[u"footer"][1]]:

                itemss_list.append({row[u"ps_wv_od_int"]:row[u"ps_wv_comm_int"]})

            self.loan_items.update({loan_no:itemss_list})

    def spider_closed(self, spider):

        # self.all_item.append(spider.loan_items)
        #
        # self.all_item.append(spider.cont_items)
        #
        # self.all_item.append(spider.surp_items)

        if int(self.settings["USELOCALIP"]) == 1:

            con.hmset("yuxin_items", {"loan_status": 1})

            con.hmset("yuxin_items", {"loan_items": self.loan_items})

            con.hmset("yuxin_items", {"surp_items": self.surp_items})

        else:

            con.hmset("yuxin_items", {"cont_status": 1})

            con.hmset("yuxin_items", {"cont_items": self.cont_items})





        

