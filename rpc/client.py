import asyncio
import grpc

import rpc.services.server_pb2 as pb
import rpc.services.server_pb2_grpc as pbg

from typing import List

from rpc.config import HOST, PORT


loop = asyncio.get_event_loop()


class Client(object):
    stub: pbg.RpcServiceStub = None

    def __init__(self):
        self.channel = grpc.aio.insecure_channel(f'{HOST}:{PORT}')

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

    async def fund_category(self, funds: List[str]):
        r = pb.funds__pb2.FundCategoryRequest(fund=funds)
        response: pb.funds__pb2.FundCategoryResponse = await self.stub.FundCategoryHandler(r)
        status_code = response.status_code
        if status_code != 0:
            return {}
        data = response.data
        data = [{'secucode': x.secucode, 'category': x.category} for x in data]
        return data

    @staticmethod
    async def async_simple(attr, *args):
        async with Client() as client:
            ret = await getattr(client, attr)(*args)
        return ret

    @classmethod
    def simple(cls, attr, *args):
        ret = loop.run_until_complete(cls.async_simple(attr, *args))
        return ret


def example():
    r = Client.simple('fund_category', ['000001', '110011'])
    print(r)


if __name__ == '__main__':
    example()
