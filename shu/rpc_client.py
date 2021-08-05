import asyncio
import grpc
from typing import AsyncIterator

from src.services_pb2_grpc import MicroServiceStub
from src import am_sma_pb2 as pb

from rpc.register import consul_app


service_name = 'microservices'


class Client(object):

    def __init__(self):
        service, _ = consul_app.find(service_name)
        host = service['Address']
        port = service['Port']
        self.channel = grpc.aio.insecure_channel(f'{host}:{port}')
        self.stub = MicroServiceStub(self.channel)

    async def sma_portfolio(self) -> AsyncIterator[pb.Portfolio]:
        request = pb.NULL()
        data = self.stub.SMAPortfolio(request)
        async for x in data:
            yield x

    async def sma_balance(self, port_code, date) -> AsyncIterator[pb.Portfolio]:
        request = pb.Request(port_code=port_code, date=date)
        data = self.stub.SMABalance(request)
        async for x in data:
            yield x

    async def sma_balance_expanded(self, port_code, date) -> AsyncIterator[pb.Portfolio]:
        request = pb.Request(port_code=port_code, date=date)
        data = self.stub.SMABalanceExpanded(request)
        async for x in data:
            yield x

    async def sma_income(self, port_code, date) -> AsyncIterator[pb.Portfolio]:
        request = pb.Request(port_code=port_code, date=date)
        data = self.stub.SMAIncome(request)
        async for x in data:
            yield x

    async def sma_income_asset(self, port_code, date) -> AsyncIterator[pb.Portfolio]:
        request = pb.Request(port_code=port_code, date=date)
        data = self.stub.SMAIncomeAsset(request)
        async for x in data:
            yield x

    async def sma_holding(self, port_code, date) -> AsyncIterator[pb.Portfolio]:
        request = pb.Request(port_code=port_code, date=date)
        data = self.stub.SMAHolding(request)
        async for x in data:
            yield x

    async def sma_transaction(self, port_code, date) -> AsyncIterator[pb.Portfolio]:
        request = pb.Request(port_code=port_code, date=date)
        data = self.stub.SMATransaction(request)
        async for x in data:
            yield x

    async def sma_detail_fee(self, port_code, date) -> AsyncIterator[pb.Portfolio]:
        request = pb.Request(port_code=port_code, date=date)
        data = self.stub.SMADetailFee(request)
        async for x in data:
            yield x

    async def sma_benchmark(self, port_code, date) -> AsyncIterator[pb.Portfolio]:
        request = pb.Request(port_code=port_code, date=date)
        data = self.stub.SMABenchmark(request)
        async for x in data:
            yield x

    async def sma_interest_tax(self, port_code, date) -> AsyncIterator[pb.Portfolio]:
        request = pb.Request(port_code=port_code, date=date)
        data = self.stub.SMAInterestTax(request)
        async for x in data:
            yield x

    async def sma_security(self) -> AsyncIterator[pb.Security]:
        request = pb.Request(port_code=None, date=None)
        data = self.stub.SMASecurity(request)
        async for x in data:
            yield x

    async def sma_security_quote(self, date) -> AsyncIterator[pb.SecurityQuote]:
        """date实际为id，为了保持接口一致所以写为date"""
        request = pb.Request(port_code=None, date=date)
        data = self.stub.SMASecurityQuote(request)
        async for x in data:
            yield x


async def test():
    client = Client()
    async for x in client.sma_security_quote('8511'):
        print(x)
    print('exit')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
