# coding=utf-8
import pycurl
import cStringIO
import re
import MySQLdb
import time


def getip(url):

    try:

        c = pycurl.Curl()

        buf = cStringIO.StringIO()

        c.setopt(pycurl.TIMEOUT_MS,1000)

        c.setopt(pycurl.MAXREDIRS,0)

        c.setopt(pycurl.URL,url)

        c.setopt(pycurl.WRITEFUNCTION,buf.write)

        c.perform()

        body = buf.getvalue()

        ip = re.findall(re.compile(r'\d+\.\d+\.\d+\.\d+',re.I),body)[0]

        c.close()

        buf.close()

    except Exception,e:

        pass

        return None

    return ip

def get_connection():

    con = MySQLdb.connect(db='proxys', host='111.200.62.9', user='root', passwd='Qbbigdata', port=3306)

    return con


if __name__ == "__main__":

    ip_list = []

    port = "20431"

    while 1:

        ip1 = getip("http://www.ip138.com/")

        if ip1 is None:

            ip2 = getip("http://www.ip.cn/")

            if ip2 is None:

                ip3 = getip("http://tool.chinaz.com/")

                ip = ip3

            else:

                ip = ip2

        else:

            ip = ip1

        if ip:

            if ip not in ip_list:

                ip_1 = None if len(ip_list)==0 else ip_list[0]

                ip_list = []

                ip_list.append(ip+":%s"%port)

                try:

                    if ip_1:

                        if ip_1 != (ip+":%s"%port):

                            con = get_connection()

                            cur = con.cursor()

                            cur.execute("delete from new_ip where ip=%s", (ip_1,))

                            con.commit()

                            cur.execute("insert into new_ip(ip,status) VALUES (%s,%s)", (ip + ":%s" % port, 1))

                            con.commit()

                            cur.close()

                            con.close()

                        else:

                            pass

                    else:

                        con = get_connection()

                        cur = con.cursor()

                        cur.execute("insert into new_ip(ip,status) VALUES (%s,%s)",(ip+":%s"%port,1))

                        con.commit()

                        cur.close()

                        con.close()

                except Exception,e:

                    print e

                    pass

            time.sleep(3)
        else:
            pass











