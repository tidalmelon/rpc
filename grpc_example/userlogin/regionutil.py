# -*- coding: utf-8 -*-

import json
from operator import itemgetter
from itertools import groupby


class RegionUtil(object):

    def __init__(self):
        self.citys = {}
        #maginc num
        with open('./resource/citys-dzdp.json') as f:
            js = f.read()
            dic = json.loads(js)
            if dic:
                for line in dic['city']:
                    city, _, _, num, _ = line.split('|')
                    if city not in self.citys:
                        self.citys[city] = num

    def getNumByCity(self, city_std):
        if city_std in self.citys:
            #print 'mingzhong'
            return city_std, self.citys[city_std]
        #arr = []
        #stand = set(city_std)
        #for city in self.citys:
        #    st = set(city)
        #    num = len(stand & st)
        #    arr.append((city, num, self.citys[city]))
        #arr.sort(key=itemgetter(1), reverse=True)
        #print '-----'
        #for k, g in groupby(arr, key=itemgetter(1)):
            #for item in g:
                #print city_std.encode('utf-8'), item[0].encode('utf-8'), item[1], item[2].encode('utf-8')
            #break
        #print '-----'
        return None, None

if __name__ == '__main__':

    util = RegionUtil()
    aset = set()
    with open('./resource/sys_citys_stand.json') as f:
        js = f.read()
        js = js[3:]
        dic = json.loads(js)
        if dic:
            for line in dic['city']:
                _, _, _, city, _, _ = line.split('|')
                if city not in aset:
                    aset.add(city)
                    city1, num = util.getNumByCity(city)
                    if city1:
                        print city.encode('utf-8'), city1.encode('utf-8'), num

    print len(aset)



    #key = u'北京市'
    #key = u'大名县'
