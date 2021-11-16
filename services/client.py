import grpc

from services import services_pb2, services_pb2_grpc


class Client(object):

    def __init__(self, host):
        self.channel = grpc.insecure_channel(host)
        self.stub = services_pb2_grpc.ServerStub(self.channel)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.channel.close()

    def ping(self):
        request = services_pb2.sync__pb2.PingRequest(msg='msg from sma_management')
        resp = self.stub.Ping(request=request)
        print(resp.code)
        print(resp.msg)

    def commit_all(self):
        request = services_pb2.sync__pb2.Request()
        resp = self.stub.SyncAll(request=request)
        return resp.status_code

    def commit_primary(self):
        request = services_pb2.sync__pb2.Request()
        resp = self.stub.SyncPrimary(request=request)
        return resp.status_code


if __name__ == '__main__':
    with Client('10.170.139.12:443') as c:
        c.ping()
