import requests
import shadowsocks

if __name__ == "__main__":

    url = "http://www.ip.cn/"

    r = requests.get(url=url,proxies={"http":"116.28.119.109:20461"},timeout=2)

    print r.text