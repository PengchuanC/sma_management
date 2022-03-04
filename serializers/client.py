"""
@author: chuanchao.peng
@date: 2022/2/26 14:33
@file client.py
@desc:
"""
import grpc


from serializers import server_pb2 as pb, server_pb2_grpc as pbc


class SMABackendServices(object):
    def __init__(self, ip: str, port: int):
        self.channel = grpc.insecure_channel(f'{ip}:{port}')
        self.stub = pbc.SMABackendServiceStub(self.channel)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.channel.close()

    def portfolio(self):
        req = pb.ReqNull()
        yield from self.stub.Portfolio(request=req)

    def portfolio_ex(self):
        req = pb.ReqNull()
        yield from self.stub.PortfolioEx(request=req)

    def balance(self, port_code: str, date: str):
        req = pb.ReqNormal(port_code=port_code, date=date)
        yield from self.stub.Balance(request=req)

    def balance_ex(self, port_code: str, date: str):
        req = pb.ReqNormal(port_code=port_code, date=date)
        yield from self.stub.BalanceEx(request=req)

    def balance_benchmark(self, port_code: str, date: str):
        req = pb.ReqNormal(port_code=port_code, date=date)
        yield from self.stub.BalanceBenchmark(request=req)

    def voucher(self, port_code: str, date: str):
        req = pb.ReqNormal(port_code=port_code, date=date)
        yield from self.stub.Voucher(request=req)

    def trans(self, port_code: str, date: str):
        req = pb.ReqNormal(port_code=port_code, date=date)
        yield from self.stub.Trans(request=req)

    def holding(self, port_code: str, date: str):
        req = pb.ReqNormal(port_code=port_code, date=date)
        yield from self.stub.Holding(request=req)

    def security(self):
        req = pb.ReqNull()
        yield from self.stub.Security(request=req)

    def security_quote(self, port_code: str, date: str):
        req = pb.ReqNormal(port_code=port_code, date=date)
        yield from self.stub.SecurityQuote(request=req)

    def security_category(self):
        req = pb.ReqNull()
        yield from self.stub.SecurityCategory(request=req)

    def income(self, port_code: str, date: str):
        req = pb.ReqNormal(port_code=port_code, date=date)
        yield from self.stub.Income(request=req)

    def income_ex(self, port_code: str, date: str):
        req = pb.ReqNormal(port_code=port_code, date=date)
        yield from self.stub.IncomeEx(request=req)

    def customer(self):
        req = pb.ReqNull()
        yield from self.stub.Customer(request=req)

    def sales(self):
        req = pb.ReqNull()
        yield from self.stub.Sales(request=req)

    def customer_mapping(self):
        req = pb.ReqNull()
        yield from self.stub.CustomerMapping(request=req)

    def sales_mapping(self):
        req = pb.ReqNull()
        yield from self.stub.SalesMapping(request=req)

    def pr(self, port_code: str, date: str):
        req = pb.ReqNormal(port_code=port_code, date=date)
        yield from self.stub.PR(request=req)


if __name__ == '__main__':
    with SMABackendServices('10.170.129.129', 50060) as services:
        for ret in services.customer():
            print(ret)
