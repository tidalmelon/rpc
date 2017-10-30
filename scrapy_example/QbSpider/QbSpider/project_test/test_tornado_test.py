# coding=utf-8
#!/usr/bin/env python
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import json
import time


class JsonHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.json_arg = None
        t = self.request.headers.get('Content-Type', '')
        if 'application/json' in t.lower():
            self.json_arg = json.loads(self.request.body)


class MainHandler(JsonHandler):

    def get(self, *args, **kwargs):

        time.sleep(20)

        self.write("ha"*66)

class App(object):

    def make_app(self):
        return tornado.web.Application([
            (r"/schedule", MainHandler),
        ])


class StartServices(object):
    app = App().make_app()
    sockets = tornado.netutil.bind_sockets(9999)
    tornado.process.fork_processes(100)
    server = HTTPServer(app)
    server.add_sockets(sockets)
    IOLoop.current().start()


if __name__ == "__main__":

    StartServices()
