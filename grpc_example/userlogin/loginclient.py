# -*- coding: utf-8 -*-

import grpc
import user_login_pb2
import user_login_pb2_grpc


def run():
    channel = grpc.insecure_channel('172.28.40.23:50051')
    stub = user_login_pb2_grpc.UserLoginStub(channel)
    response = stub.loadSites(user_login_pb2.SitesRequest(unamed=1))
    print response.sites

if __name__ == '__main__':
    run()
