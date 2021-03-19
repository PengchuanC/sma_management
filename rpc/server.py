import time
import grpc
from concurrent import futures

import rpc.services.server_pb2 as pb
import rpc.services.server_pb2_grpc as pbg

from rpc.funds.category import fund_category


class Server(pbg.RpcServiceServicer):

    def FundCategoryHandler(self, request, context):
        """获取基金分类"""
        return fund_category(request, context)

    @staticmethod
    def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        pbg.add_RpcServiceServicer_to_server(Server(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        print('grpc server started')
        try:
            while True:
                time.sleep(60*60*24)
        except KeyboardInterrupt:
            server.stop()

