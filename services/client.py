from typing import Generator

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
        self.stub.SyncAll(request=request)

    def commit_primary(self):
        request = services_pb2.sync__pb2.Request()
        resp = self.stub.SyncPrimary(request=request)
        print(resp.status_code)

    def sma_portfolio(self) -> Generator:
        request = services_pb2.transfer__pb2.NULL()
        resp = self.stub.SMAPortfolio(request=request)
        return resp

    def sma_portfolio_expanded(self):
        request = services_pb2.transfer__pb2.NULL()
        resp = self.stub.SMAPortfolioExpanded(request=request)
        return resp

    def sma_balance(self, port_code: str, date: str):
        request = services_pb2.transfer__pb2.TRequest(port_code=port_code, date=date)
        resp = self.stub.SMABalance(request=request)
        return resp

    def sma_balance_expanded(self, port_code: str, date: str):
        request = services_pb2.transfer__pb2.TRequest(port_code=port_code, date=date)
        resp = self.stub.SMABalanceExpanded(request=request)
        return resp

    def sma_income_portfolio(self, port_code: str, date: str):
        request = services_pb2.transfer__pb2.TRequest(port_code=port_code, date=date)
        resp = self.stub.SMAIncome(request=request)
        return resp

    def sma_income_asset(self, port_code: str, date: str):
        request = services_pb2.transfer__pb2.TRequest(port_code=port_code, date=date)
        resp = self.stub.SMAIncomeAsset(request=request)
        return resp

    def sma_holding(self, port_code: str, date: str):
        request = services_pb2.transfer__pb2.TRequest(port_code=port_code, date=date)
        resp = self.stub.SMAHolding(request=request)
        return resp

    def sma_transaction(self, port_code: str, date: str):
        request = services_pb2.transfer__pb2.TRequest(port_code=port_code, date=date)
        resp = self.stub.SMATransaction(request=request)
        return resp

    def sma_detail_fee(self, port_code: str, date: str):
        request = services_pb2.transfer__pb2.TRequest(port_code=port_code, date=date)
        resp = self.stub.SMADetailFee(request=request)
        return resp

    def sma_benchmark(self, port_code: str, date: str):
        request = services_pb2.transfer__pb2.TRequest(port_code=port_code, date=date)
        resp = self.stub.SMABenchmark(request=request)
        return resp

    def sma_interest_tax(self, port_code: str, date: str):
        request = services_pb2.transfer__pb2.TRequest(port_code=port_code, date=date)
        resp = self.stub.SMAInterestTax(request=request)
        return resp

    def sma_security(self):
        request = services_pb2.transfer__pb2.NULL()
        resp = self.stub.SMASecurity(request=request)
        return resp

    def sma_security_quote(self, date: str):
        request = services_pb2.transfer__pb2.TRequest(port_code="", date=date)
        resp = self.stub.SMASecurityQuote(request=request)
        return resp


if __name__ == '__main__':
    # host = '10.170.139.12:443'
    host = 'localhost:50053'
    with Client(host) as client:
        client.security_quote('2021-12-10')
