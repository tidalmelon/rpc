from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
import json
import redis

def _decode_list(data):
	rv = []
	for item in data:
		if isinstance(item, unicode):
			item = item.encode('utf-8')
		elif isinstance(item, list):
			item = _decode_list(item)
		elif isinstance(item, dict):
			item = _decode_dict(item)
		rv.append(item)
	return rv

def _decode_dict(data):
	rv = {}
	for key, value in data.iteritems():
		if isinstance(key, unicode):
			key = key.encode('utf-8')
		if isinstance(value, unicode):
			value = value.encode('utf-8')
		elif isinstance(value, list):
			value = _decode_list(value)
		elif isinstance(value, dict):
			value = _decode_dict(value)
		rv[key] = value
	return rv

if __name__ == "__main__":

    con = redis.Redis(host="172.28.40.23", port=6379, password="Qbbigdata")

    print eval(con.hmget("033e6d1ccb4011e6a3465a29abf1bafd","items")[0].replace("True","'True'").replace("False","'False'").replace("'",'"'))


