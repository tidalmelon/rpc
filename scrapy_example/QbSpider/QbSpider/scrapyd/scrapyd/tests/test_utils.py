import sys, os
from pkgutil import get_data
from cStringIO import StringIO

from twisted.trial import unittest

from scrapy.utils.test import get_pythonpath
from scrapyd.interfaces import IEggStorage
from scrapyd.utils import get_crawl_args, get_spider_list
from scrapyd import get_application

def get_pythonpath_scrapyd():
    scrapyd_path = __import__('scrapyd').__path__[0]
    return os.path.dirname(scrapyd_path) + os.pathsep + get_pythonpath() + os.pathsep + os.environ.get('PYTHONPATH', '')


class UtilsTest(unittest.TestCase):

    def test_get_crawl_args(self):
        msg = {'_project': 'lolo', '_spider': 'lala'}
        self.assertEqual(get_crawl_args(msg), ['lala'])
        msg = {'_project': 'lolo', '_spider': 'lala', 'arg1': u'val1'}
        cargs = get_crawl_args(msg)
        self.assertEqual(cargs, ['lala', '-a', 'arg1=val1'])
        assert all(isinstance(x, str) for x in cargs), cargs

    def test_get_crawl_args_with_settings(self):
        msg = {'_project': 'lolo', '_spider': 'lala', 'arg1': u'val1', 'settings': {'ONE': 'two'}}
        cargs = get_crawl_args(msg)
        self.assertEqual(cargs, ['lala', '-a', 'arg1=val1', '-s', 'ONE=two'])
        assert all(isinstance(x, str) for x in cargs), cargs

class GetSpiderListTest(unittest.TestCase):

    def test_get_spider_list(self):
        path = os.path.abspath(self.mktemp())
        j = os.path.join
        eggs_dir = j(path, 'eggs')
        os.makedirs(eggs_dir)
        dbs_dir = j(path, 'dbs')
        os.makedirs(dbs_dir)
        logs_dir = j(path, 'logs')
        os.makedirs(logs_dir)
        os.chdir(path)
        with open('scrapyd.conf', 'w') as f:
            f.write("[scrapyd]\n")
            f.write("eggs_dir = %s\n" % eggs_dir)
            f.write("dbs_dir = %s\n" % dbs_dir)
            f.write("logs_dir = %s\n" % logs_dir)
        app = get_application()
        eggstorage = app.getComponent(IEggStorage)
        eggfile = StringIO(get_data("scrapyd.tests", 'mybot.egg'))
        eggstorage.put(eggfile, 'mybot', 'r1')
        spiders = get_spider_list('mybot', pythonpath=get_pythonpath_scrapyd())
        self.assertEqual(sorted(spiders), ['spider1', 'spider2'])

