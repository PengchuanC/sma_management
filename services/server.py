import time
from concurrent import futures

import grpc
from django.db import close_old_connections

from services import services_pb2, services_pb2_grpc
from proc.schedule import commit_all, priority_task


class Server(services_pb2_grpc.ServerServicer):

    def Ping(self, request, context):
        msg = request.msg
        ret_msg = f'received msg "{msg}"'
        return services_pb2.sync__pb2.PingResponse(msg=ret_msg, code=0)

    def SyncAll(self, request, context):
        close_old_connections()
        commit_all()
        return services_pb2.sync__pb2.Response(status_code=0)

    def SyncPrimary(self, request, context):
        close_old_connections()
        priority_task()
        return services_pb2.sync__pb2.Response(status_code=0)

    @staticmethod
    def serve():
        host = '[::]:50053'
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        services_pb2_grpc.add_ServerServicer_to_server(Server(), server)
        server.add_insecure_port(host)
        server.start()
        try:
            while True:
                time.sleep(60 * 60)  # one day in seconds
        except KeyboardInterrupt:
            server.stop(0)
        except Exception as e:
            print(e)
            server.stop(-1)


if __name__ == '__main__':
    Server.serve()
