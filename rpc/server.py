import grpc
from concurrent import futures
from asyncio import sleep

from django.db import connections
from django.db.utils import OperationalError

import rpc.services.server_pb2 as pb
import rpc.services.server_pb2_grpc as pbg

from rpc.funds import category
from rpc.config import PORT


class Server(pbg.RpcServiceServicer):

    async def FundCategoryHandler(self, request, context):
        """获取基金分类"""
        resp = await category.fund_category_new(request, context)
        return resp

    async def FundBasicInfoHandler(self, request, context):
        """获取基金基础信息"""
        resp = await category.fund_basic_info(request, context)
        return resp

    @staticmethod
    async def serve():
        server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=2))
        pbg.add_RpcServiceServicer_to_server(Server(), server)
        server.add_insecure_port(f'[::]:{PORT}')
        await server.start()
        print('grpc server started')
        try:
            while True:
                await sleep(60 * 60 * 4)
        except KeyboardInterrupt:
            await server.stop()
