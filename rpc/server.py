import grpc
from concurrent import futures
from asyncio import sleep

from django.db import connections
from django.db.utils import OperationalError

import rpc.services.server_pb2 as pb
import rpc.services.server_pb2_grpc as pbg

from rpc.funds import category
from rpc.config import HOST, PORT

from rpc.register import consul_app


class Server(pbg.RpcServiceServicer):

    async def FundCategoryHandler(self, request, context):
        """获取基金分类"""
        resp = await category.fund_category_new(request, context)
        return resp

    async def FundCategoryFullHandler(self, request, context):
        """获取基金完整分类"""
        resp = await category.fund_classify_full(request, context)
        return resp

    async def FundBasicInfoHandler(self, request, context):
        """获取基金基础信息"""
        resp = await category.fund_basic_info(request, context)
        return resp

    async def PortfolioCoreHandler(self, request, context):
        """获取基金分类"""
        resp = await category.portfolio_core(request, context)
        return resp

    @staticmethod
    async def register(name, host, port):
        service, err = consul_app.find(name)
        if not err:
            consul_app.deregister(service['ID'])
        consul_app.register(name, host, port)

    @staticmethod
    async def serve():
        server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=2))
        pbg.add_RpcServiceServicer_to_server(Server(), server)
        server.add_insecure_port(f'[::]:{PORT}')
        await server.start()
        print('grpc server started')
        name = 'fund_filter_django'
        await Server.register(name, HOST, PORT)
        try:
            while True:
                await sleep(60 * 60 * 4)
        except KeyboardInterrupt:
            await server.stop()
