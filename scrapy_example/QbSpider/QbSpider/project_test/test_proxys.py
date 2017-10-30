#!/usr/bin/env python
#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from argparse import ArgumentParser
from Queue import Queue
from threading import Thread
import requests
import time
import re
mysql_ip = '172.28.40.21'
port = 3306
username = "crawler"
passwd = "crawler"
db='crawl'


class ProxyChecker:
    def __init__(self, inlist, threads = 200, verbose = False, timeout = 10):
        self.inlist = inlist
        # there shouldn't be more threads than there are proxies
        if threads > len(self.inlist):
            self.threads = len(self.inlist)

        else:
            self.threads = threads

        self.verbose = verbose
        self.timeout = timeout

        self.outlist = []
        self.total_scanned = 0
        self.total_working = 0
        self.original_ip = None
        self.threads_done = 0

        # constants
        self.IP_CHECK = "http://www.1356789.com/"

    def save_valid_proxy(self, proxy):
        if proxy:
            self.outlist.append(proxy)

    def get_external_ip(self, proxies = None):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Host": "www.1356789.com",
            "Referer": "http://m.ip138.com/",
        }

        try:
            if proxies:
                order_time = int(time.time() * 1000)
                r = requests.get(self.IP_CHECK, proxies = proxies, headers = headers, timeout = self.timeout)
                new_time = int(time.time() * 1000)
                time_speed = new_time - order_time

            else:
                resp = requests.get(self.IP_CHECK, headers = headers)
            if resp.status_code == 200:
                page = resp.text
                ip_url = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', page).group()
                ip_now = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ip_proxy).group()
                if ip_url == ip_now:  # 判断是否是匿名代理
                    self.ip_valid.append(ip_proxy)
                    print ip_proxy + u" 匿名代理"
                    sql = "INSERT into new_ip (ip,status,type,speed,update_time) VALUES ('%s','1','匿名代理','%.3f',NOW())" % (
                    ip_proxy, time_speed)
                    cur.execute(sql)
                else:
                    self.ip_valid.append(ip_proxy)
                    print ip_proxy + u" 透明代理"
                    sql = "INSERT into new_ip (ip,status,type,speed,update_time) VALUES ('%s','1','透明代理','%.3f',NOW())" % (
                    ip_proxy, time_speed)
                    cur.execute(sql)
                print u'保存'
                conn.commit()

        except IOError:
            return False

        return str(r.text)

    def check_proxy(self, proxy):
        proxies = {
                "http": "http://" + proxy,
                "https": "https://" + proxy
        }

        # see if the proxy actually works
        ip = self.get_external_ip(proxies = proxies)
        if not ip:
            return False

        if ip != self.original_ip:
            if self.verbose:
                print(ip)

            self.total_working += 1

        return proxy

    def process_proxy(self):
        try:
            while True:
                proxy = self.queue.get()
                self.save_valid_proxy(self.check_proxy(proxy))
                self.queue.task_done()
                self.total_scanned += 1

        except:
            pass

    def start(self):
        if self.verbose:
            print("Running: {} threads...".format(self.threads))

        self.original_ip = self.get_external_ip()

        if self.verbose:
            print("Your original external IP address is: {}".format(self.original_ip))
            print("Checking proxies...")

        self.queue = Queue(self.threads)

        # get all our threads ready for work
        for i in range(0, self.threads):
            thread = Thread(target = self.process_proxy)
            thread.daemon = True
            thread.start()

        self.start = time.time()

        # keep sending threads their jobs
        try:
            for proxy in self.inlist:
                self.queue.put(proxy.strip())

            self.queue.join()

        except KeyboardInterrupt:
            if self.verbose:
                print("Closing down, please let the threads finish.")

        if self.verbose:
            print("Running: {:.2f} seconds".format(time.time() - self.start))

        if self.verbose:
            print("Scanned: {} proxies".format(self.total_scanned))
            print("Working: {} proxies".format(self.total_working))

        return self.outlist


def CLI():
    threads_default = 200
    timeout_default = 25

    # handle all the command-line argument stuff
    parser = ArgumentParser(description = "Check a proxy list for working proxies.")
    parser.add_argument("infile", type = str, help = "input proxy list file")
    parser.add_argument("outfile", type = str, help = "output proxy list file")
    parser.add_argument("-t", "--threads", type = int, default = threads_default, help = "set the number of threads running concurrently (default {})".format(threads_default))
    parser.add_argument("-v", "--verbose", action = "store_true", help = "say lots of useless stuff (sometimes)")
    parser.add_argument("-to", "--timeout", type = int, help = "the timeout for testing proxies (default {})".format(timeout_default))
    args = parser.parse_args()

    # check to see if the input file actually exists
    try:
        infile = open(args.infile, "r")
        inlist = infile.read().split("\n")
        infile.close()

    except IOError:
        print("Invalid proxy list filename.")
        sys.exit()

    proxy_checker = ProxyChecker(inlist, threads = args.threads, verbose = args.verbose, timeout = timeout_default)
    outlist = proxy_checker.start()
    outfile = open(args.outfile, "w")
    outfile.write("\n".join(outlist))
    outfile.close()


if __name__ == "__main__":
    CLI()