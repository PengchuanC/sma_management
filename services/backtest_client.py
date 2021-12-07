import grpc

from services import backtest_pb2 as pb, backtest_pb2_grpc as pbc


class Client(object):

    def __init__(self, host, port):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = pbc.BacktestServerStub(channel=self.channel)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.channel.close()

    def standard_portfolio(self):
        request = pb.BRequest.NullRequest()
        resp = self.stub.StandardPortfolioNav(request=request)
        return resp.data

    def weight(self):
        request = pb.BRequest.NullRequest()
        resp = self.stub.Weight(request=request)
        return resp.data

    def index_portfolio(self):
        request = pb.BRequest.NullRequest()
        resp = self.stub.IndexPortfolioNav(request=request)
        return resp.data

    def fund_index_portfolio(self):
        request = pb.BRequest.NullRequest()
        resp = self.stub.FundIndexPortfolioNav(request=request)
        return resp.data

    def sync_data(self):
        request = pb.BRequest.NullRequest()
        self.stub.SyncData(request=request)


if __name__ == '__main__':
    with Client('10.170.129.129', 50055) as client:
        weight = client.weight()
        print(weight)
