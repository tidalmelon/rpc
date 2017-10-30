import grpc
from grpc.framework.common import cardinality
from grpc.framework.interfaces.face import utilities as face_utilities

import user_login_pb2 as user__login__pb2
import user_login_pb2 as user__login__pb2
import user_login_pb2 as user__login__pb2
import user_login_pb2 as user__login__pb2
import user_login_pb2 as user__login__pb2
import user_login_pb2 as user__login__pb2
import user_login_pb2 as user__login__pb2
import user_login_pb2 as user__login__pb2
import user_login_pb2 as user__login__pb2
import user_login_pb2 as user__login__pb2


class UserLoginStub(object):

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.loadSites = channel.unary_unary(
        '/userlogin.UserLogin/loadSites',
        request_serializer=user__login__pb2.SitesRequest.SerializeToString,
        response_deserializer=user__login__pb2.SitesResponse.FromString,
        )
    self.loginYys = channel.unary_unary(
        '/userlogin.UserLogin/loginYys',
        request_serializer=user__login__pb2.RequestYYS.SerializeToString,
        response_deserializer=user__login__pb2.ResponseYYS.FromString,
        )
    self.loginGjj = channel.unary_unary(
        '/userlogin.UserLogin/loginGjj',
        request_serializer=user__login__pb2.RequestGJJ.SerializeToString,
        response_deserializer=user__login__pb2.ResponseGJJ.FromString,
        )
    self.searchXmdDzdp = channel.unary_unary(
        '/userlogin.UserLogin/searchXmdDzdp',
        request_serializer=user__login__pb2.RequestXmdDzdpSearch.SerializeToString,
        response_deserializer=user__login__pb2.ResponseXmdDzdpSearch.FromString,
        )
    self.getCommentsXmdDzdp = channel.unary_unary(
        '/userlogin.UserLogin/getCommentsXmdDzdp',
        request_serializer=user__login__pb2.RequestXmdDzdpComment.SerializeToString,
        response_deserializer=user__login__pb2.ResponseXmdDzdpComment.FromString,
        )


class UserLoginServicer(object):

  def loadSites(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def loginYys(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def loginGjj(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def searchXmdDzdp(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def getCommentsXmdDzdp(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_UserLoginServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'loadSites': grpc.unary_unary_rpc_method_handler(
          servicer.loadSites,
          request_deserializer=user__login__pb2.SitesRequest.FromString,
          response_serializer=user__login__pb2.SitesResponse.SerializeToString,
      ),
      'loginYys': grpc.unary_unary_rpc_method_handler(
          servicer.loginYys,
          request_deserializer=user__login__pb2.RequestYYS.FromString,
          response_serializer=user__login__pb2.ResponseYYS.SerializeToString,
      ),
      'loginGjj': grpc.unary_unary_rpc_method_handler(
          servicer.loginGjj,
          request_deserializer=user__login__pb2.RequestGJJ.FromString,
          response_serializer=user__login__pb2.ResponseGJJ.SerializeToString,
      ),
      'searchXmdDzdp': grpc.unary_unary_rpc_method_handler(
          servicer.searchXmdDzdp,
          request_deserializer=user__login__pb2.RequestXmdDzdpSearch.FromString,
          response_serializer=user__login__pb2.ResponseXmdDzdpSearch.SerializeToString,
      ),
      'getCommentsXmdDzdp': grpc.unary_unary_rpc_method_handler(
          servicer.getCommentsXmdDzdp,
          request_deserializer=user__login__pb2.RequestXmdDzdpComment.FromString,
          response_serializer=user__login__pb2.ResponseXmdDzdpComment.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'userlogin.UserLogin', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
