# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from services import sync_pb2 as sync__pb2


class ServerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Ping = channel.unary_unary(
                '/services.Server/Ping',
                request_serializer=sync__pb2.PingRequest.SerializeToString,
                response_deserializer=sync__pb2.PingResponse.FromString,
                )
        self.SyncAll = channel.unary_unary(
                '/services.Server/SyncAll',
                request_serializer=sync__pb2.Request.SerializeToString,
                response_deserializer=sync__pb2.Response.FromString,
                )
        self.SyncPrimary = channel.unary_unary(
                '/services.Server/SyncPrimary',
                request_serializer=sync__pb2.Request.SerializeToString,
                response_deserializer=sync__pb2.Response.FromString,
                )


class ServerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Ping(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SyncAll(self, request, context):
        """同步全部数据
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SyncPrimary(self, request, context):
        """同步关键数据
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Ping': grpc.unary_unary_rpc_method_handler(
                    servicer.Ping,
                    request_deserializer=sync__pb2.PingRequest.FromString,
                    response_serializer=sync__pb2.PingResponse.SerializeToString,
            ),
            'SyncAll': grpc.unary_unary_rpc_method_handler(
                    servicer.SyncAll,
                    request_deserializer=sync__pb2.Request.FromString,
                    response_serializer=sync__pb2.Response.SerializeToString,
            ),
            'SyncPrimary': grpc.unary_unary_rpc_method_handler(
                    servicer.SyncPrimary,
                    request_deserializer=sync__pb2.Request.FromString,
                    response_serializer=sync__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'services.Server', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Server(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/services.Server/Ping',
            sync__pb2.PingRequest.SerializeToString,
            sync__pb2.PingResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SyncAll(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/services.Server/SyncAll',
            sync__pb2.Request.SerializeToString,
            sync__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SyncPrimary(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/services.Server/SyncPrimary',
            sync__pb2.Request.SerializeToString,
            sync__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)