# coding=utf-8
import requests
from lxml import etree
import logging
import re


class XindaiyunSpider(object):


    logins_url = "http://ep.duohaojr.com/signOnAuto.do"

    loginout_url = "http://ep.duohaojr.com/signOut.do"

    def login(self):

        login_cookie = requests.get(self.logins_url)

        cookie = dict(login_cookie.cookies)

        username = "xxxx"

        passwd = "callme"

        login_url = "http://ep.duohaojr.com/userSignOn.do"

        post_data = {
            "currentUserId": "%s" % username,
            "password": "%s" % passwd,
            "text1": "验证码",
            "realIp": "",
            "browserInfo": "",
        }

        login_content = requests.post(login_url,data=post_data,json=cookie)

        hxs = etree.HTML(login_content.text)

        name = "".join(hxs.xpath("//span[@class='admin_02']/text()"))

        logging.warning(msg="%s" % name)

        emp_id = re.findall(re.compile(r"empId\s=\s+?'([\S]+?)';",re.I),hxs.xpath("//script[@type='text/javascript'][1]/text()")[0])[0]

        url = "http://ep.duohaojr.com/welcomeShenpi.do?EMP_SID=%s&usr_sex=10"%emp_id

        shen_content = requests.get(url,cookies=dict(login_content.cookies))

        hxs = etree.HTML(shen_content.text)

        emp_id = re.findall(re.compile(r"empId\s=\s+?'([\S]+?)';", re.I),
                            hxs.xpath("//script[@type='text/javascript'][1]/text()")[0])[0]

        url = "http://ep.duohaojr.com/queryLmLoanListForLmPmShdAction.do?EMP_SID=%s" % emp_id

        post_data = {'page':'1',
                     'rows':'10'}

        back_plan = requests.post(url,data=post_data)

        print back_plan.text







if __name__ == "__main__":
    # post_data = {
    #     "page": '20',
    #     "rows": '20'
    # }
    #
    # url = "http://ep.duohaojr.com/queryLmLoanListForLmPmShdAction.do?EMP_SID=CIDCANJCAFFPHJFXCFDLARHNDNGEANBXCHHGITGD"
    #
    # headers = {
    #     # "Accept": "application/json, text/javascript, */*; q=0.01",
    #     # "Accept-Encoding": "gzip, deflate",
    #     # "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    #     # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    #     # "Host": "ep.duohaojr.com",
    #     # "Origin": "http://ep.duohaojr.com",
    #     # "Referer": "http://ep.duohaojr.com/queryLmPmShd.do?EMP_SID=CIDCANJCAFFPHJFXCFDLARHNDNGEANBXCHHGITGD&menuId=queryLmPmShd",
    #     # "X-Requested-With": "XMLHttpRequest",
    #     "Cookie": "JSESSIONID=FEFE95FE41DC8483D72B66384E62C50A;"
    # }
    #
    # #r = requests.post(url, data=post_data,json=headers)
    #
    # #jobid = r.text
    #
    # url2 = "http://ep.duohaojr.com/queryLmLoanListForLmPmShdAction.do?EMP_SID=CIDCANJCAFFPHJFXCFDLARHNDNGEANBXCHHGITGD"
    #
    # r = requests.post(url2, data=post_data)
    #
    # jobid = r.text
    #
    # print jobid

    print XindaiyunSpider().login()
