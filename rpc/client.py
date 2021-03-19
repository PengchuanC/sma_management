import grpc

import rpc.services.server_pb2 as pb
import rpc.services.server_pb2_grpc as pbg

from typing import List

from rpc.config import HOST, PORT


class Client(object):
    stub: pbg.RpcServiceStub = None

    def __init__(self):
        self.channel = grpc.insecure_channel(f'{HOST}:{PORT}')

    def connect(self):
        self.stub = pbg.RpcServiceStub(self.channel)

    def close(self):
        self.channel.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def fund_category(self, funds: List[str]):
        r = pb.funds__pb2.FundCategoryRequest(fund=funds)
        response: pb.funds__pb2.FundCategoryResponse = self.stub.FundCategoryHandler(r)
        status_code = response.status_code
        if status_code != 0:
            return {}
        data = response.data
        data = [{'secucode': x.secucode, 'category': x.category} for x in data]
        return data

    @staticmethod
    def simple(attr, *args):
        with Client() as client:
            ret = getattr(client, attr)(*args)
        return ret


def example():
    r = Client.simple('fund_category', ['000001', '110011'])
    print(r)


if __name__ == '__main__':
    example()
