# 服务注册

import consul

from rpc.config import CONSUL_CONFIG


class Consul(object):
    """
    微服务注册与发现中心
    Attributes:
        host: 服务ip
        port: 服务端口，默认为8500
    """

    def __init__(self, host, port=8500):
        self._consul = consul.Consul(host, port)

    def register(self, name, host, port):
        """注册服务"""
        self._consul.agent.service.register(
            name=name, service_id=name, address=host, port=port,
            check=consul.Check().tcp(host=host, port=port, interval='5s',
                                     timeout='30s', deregister='30s')
        )

    def deregister(self, service_id):
        """注销服务"""
        self._consul.agent.service.deregister(service_id=service_id)

    def find(self, name):
        """通过服务名称发现服务"""
        services = self._consul.agent.services()
        server = services.get(name)
        if not server:
            return None, True
        return server, False

    def get_by_key(self, key):
        """查询key/value"""
        value = self._consul.kv.get(key)
        info = value[1]
        return info['Value']


consul_app = Consul(**CONSUL_CONFIG)
