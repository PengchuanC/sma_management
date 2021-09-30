import asyncio
import grpc

import rpc.services.api_pb2 as pb
import rpc.services.api_pb2_grpc as pbg

from typing import List

from rpc.register import consul_app


loop = asyncio.get_event_loop()


class Client(object):
    stub: pbg.ScreenRpcServerStub = None

    def __init__(self, service_name):
        host, port = self.get_server(service_name)
        self.channel = grpc.insecure_channel(f'{host}:{port}')

    @staticmethod
    def get_server(service_name):
        """获取微服务地址"""
        server, err = consul_app.find(service_name)
        if err:
            raise RuntimeError(f'cannot find service [{service_name}]!')
        host = server['Address']
        port = server['Port']
        return host, port

    def connect(self):
        self.stub = pbg.ScreenRpcServerStub(self.channel)

    def close(self):
        self.channel.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def fund_category(self, funds: List[str]):
        r = pb.classify__pb2.ClassifyReq(secucode=funds)
        response: pb.classify__pb2.ClassifyResp = self.stub.FundCategory(r)
        data: List[pb.classify__pb2.Classify] = response.data
        data = [{'secucode': x.secucode, 'first': x.first, 'second': x.second} for x in data]
        return data

    @staticmethod
    def simple(attr, *args):
        name = 'fund_screen'
        with Client(name) as client:
            ret = getattr(client, attr)(*args)
        return ret


def example():
    r = Client.simple('fund_category', ['000001', '110011'])
    print(r)


if __name__ == '__main__':
    example()
