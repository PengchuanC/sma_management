import asyncio
import grpc
import json

import rpc.services.api_pb2 as pb
import rpc.services.api_pb2_grpc as pbg

from typing import List

from rpc.register import consul_app


def get_rpc_server():
    info = consul_app.get_by_key('RpcProxyServer')
    info = json.loads(info)
    return f'{info["host"]}:{info["port"]}'


class Client(object):
    stub: pbg.ScreenRpcServerStub = None

    def __init__(self, proxy_host='10.170.139.12:443'):
        self.channel = grpc.insecure_channel(f'{proxy_host}')

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

    def fund_basic(self):
        r = pb.basic__pb2.FundBasicInfoRequest()
        response = self.stub.FundBasicInfoHandler(r)
        data = response.data
        data = {x.secucode: x.launch_date for x in data}
        return data

    @staticmethod
    def simple(attr, *args):
        name = get_rpc_server()
        with Client(name) as client:
            ret = getattr(client, attr)(*args)
        return ret


def example():
    r = Client.simple('fund_category', ['000001', '110011'])
    print(r)
    r = Client.simple('fund_basic')
    print(r)


if __name__ == '__main__':
    # example()
    get_rpc_server()

