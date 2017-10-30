#encoding=utf8
import sys, os
sys.path.append(os.path.abspath("../../"))
import redis
from scrapy.utils.project import get_project_settings
import logging
logger = logging.getLogger(__name__)
'''
获取配置的工具类
'''
class RedisConfUtil():

    def get_redis(self):

        settings = get_project_settings().getdict("REDIS_PARAMSS")

        con = redis.Redis(host=settings["REDIS_HOST"],port=settings["REDIS_PORT"],password=settings["REDIS_PASSWORD"])

        #con = redis.Redis(host=settings["REDIS_HOST"], port=settings["REDIS_PORT"])

        logging.info(msg="Connect redis server success")

        return con

# if __name__ == "__main__":
#
#     con = RedisConfUtil().get_redis()
#
#     import json
#
#     con.lpush("QUEUE_YYS_LT",json.dumps({"token": "14f0b8c8-b4ee-4530-b2c6-62c3f79dbdce", "site": "YYS_LT", "phone": "15665690475", "pwd": "127128","key":"YYS_LT_15665690475_14f0b8c8-b4ee-4530-b2c6-62c3f79dbdce","sms":""}))
#
#









