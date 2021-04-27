import asyncio
import grpc

import rpc.services.server_pb2 as pb
import rpc.services.server_pb2_grpc as pbg

from typing import List

from rpc.register import consul_app


loop = asyncio.get_event_loop()


class Client(object):
    stub: pbg.RpcServiceStub = None

    def __init__(self, service_name):
        host, port = self.get_server(service_name)
        self.channel = grpc.aio.insecure_channel(f'{host}:{port}')

    @staticmethod
    def get_server(service_name):
        """获取微服务地址"""
        server, err = consul_app.find(service_name)
        if err:
            raise RuntimeError(f'cannot find service [{service_name}]!')
        host = server['Address']
        port = server['Port']
        return host, port

    async def connect(self):
        self.stub = pbg.RpcServiceStub(self.channel)

    async def close(self):
        await self.channel.close()

    async def __aenter__(self):
        await self.connect()
        return self

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def fund_category(self, funds: List[str], kind: int):
        r = pb.funds__pb2.FundCategoryRequest(fund=funds, kind=kind)
        response: pb.funds__pb2.FundCategoryResponse = await self.stub.FundCategoryHandler(r)
        status_code = response.status_code
        if status_code != 0:
            return {}
        data = response.data
        data = [{'secucode': x.secucode, 'category': x.category} for x in data]
        return data

    async def fund_basic_info(self):
        r = pb.funds__pb2.FundBasicInfoRequest()
        response = await self.stub.FundBasicInfoHandler(r)
        resp = {x.secucode: x.launch_date for x in response.data}
        return resp

    async def portfolio_core(self):
        """核心池中基金列表"""
        r = pb.funds__pb2.NullRequest()
        response = await self.stub.PortfolioCoreHandler(r)
        resp = response.funds
        return resp

    @staticmethod
    async def async_simple(attr, *args):
        name = 'fund_filter_django'
        async with Client(name) as client:
            ret = await getattr(client, attr)(*args)
        return ret

    @classmethod
    def simple(cls, attr, *args):
        ret = loop.run_until_complete(cls.async_simple(attr, *args))
        return ret


def example():
    r = Client.simple('fund_category', ['000001', '110011'], '1')
    print(r)
    r = Client.simple('portfolio_core')
    print(r)


if __name__ == '__main__':
    example()
