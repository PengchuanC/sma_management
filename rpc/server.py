import grpc
import time

from concurrent import futures

from rpc.compiled import command_pb2
from rpc.compiled import command_pb2_grpc
from sql.tools import commit_index_gil, commit_fund


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Server(command_pb2_grpc.CommandToolServicer):
    """服务端server

    Attributes:

    """

    def CommitIndexGil(self, request, context):
        """同步指数数据

        Args:
            request:
            context:

        Returns:
            Response: 返回任务执行结果状态
        """
        ok = False
        try:
            commit_index_gil()
            ok = True
        except Exception as e:
            print(e)
        resp = command_pb2.Response(ok=ok)
        return resp

    def CommitFund(self, request, context):
        """同步基金数据

        Args:
            request:
            context:

        Returns:
            Response: 返回任务执行结果状态
        """
        ok = False
        try:
            commit_fund()
            ok = True
        except Exception as e:
            print(e)
        resp = command_pb2.Response(ok=ok)
        return resp

    @staticmethod
    def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        command_pb2_grpc.add_CommandToolServicer_to_server(Server(), server)
        server.add_insecure_port("[::]:50051")
        server.start()
        try:
            while True:
                print("start server")
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == '__main__':
    Server.serve()
