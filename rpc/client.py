
import grpc

from rpc.compiled import command_pb2, command_pb2_grpc


class RpcInstance(object):
    stub: command_pb2_grpc.CommandToolStub = None

    def __init__(self, port=50051):
        self.channel = grpc.insecure_channel(f'127.0.0.1:{port}')

    def connect(self):
        self.stub = command_pb2_grpc.CommandToolStub(self.channel)

    def close(self):
        self.channel.close()

    def commit_index_gil(self, name: str):
        r = command_pb2.Request(name=name)
        response = self.stub.CommitIndexGil(r)
        return response

    def commit_fund(self, name: str):
        r = command_pb2.Request(name=name)
        response = self.stub.CommitFund(r)
        return response

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == '__main__':
    with RpcInstance() as ri:
        resp = ri.commit_fund('test')
    print(resp)
