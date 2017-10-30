# -*- coding: utf-8 -*-

import json


class RegionUtil(object):

    def __init__(self):
        self.citys = []
        #maginc num
        with open('./citys-dzdp.json') as f:
            js = f.read()
            dic = json.loads(js)
            if dic:
                for line in dic['city']:
                    city, _, _, num, _ = line.split('|')
                    self.citys.append((int(num), city))
        self.citys.sort(key=lambda x:x[0])
        for e in self.citys:
            print e


if __name__ == '__main__':

    util = RegionUtil()
    

