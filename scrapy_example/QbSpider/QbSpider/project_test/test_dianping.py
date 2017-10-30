import requests


if __name__ == "__main__":

    headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, sdch",
        "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
        "Host":"www.dianping.com",
        "Proxy-Connection":"keep-alive",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
    }

    proxies = {"http":"http://106.46.136.37:808",}

    text = requests.get(url="http://www.dianping.com/shop/68601600/review_more?pageno=1",headers=headers)

    print text.text