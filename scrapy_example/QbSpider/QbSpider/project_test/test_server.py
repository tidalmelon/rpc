# coding=utf-8
import requests
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
import sys,os
sys.path.append(os.path.abspath("../../"))

if __name__ == "__main__":

    for spider_name in ["jingdong"]:

        for x in xrange(12):
            username = ""
            password = ""
            vercode = ""
            pay_load = {"spider" :spider_name,"username" : username, "password" : password, "vercode" : vercode,"spidertype":"delay"}
            url = "http://172.28.40.23:9999/schedule"
            requests.post(url,data=pay_load)