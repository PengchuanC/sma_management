# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import serializers.balance_pb2 as balance__pb2
import serializers.income_pb2 as income__pb2
import serializers.pr_pb2 as pr__pb2
import serializers.security_pb2 as security__pb2
import serializers.server_pb2 as server__pb2
import serializers.transaction_pb2 as transaction__pb2
import serializers.users_pb2 as users__pb2


class SMABackendServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Portfolio = channel.unary_stream(
                '/serializers.SMABackendService/Portfolio',
                request_serializer=server__pb2.ReqNull.SerializeToString,
                response_deserializer=server__pb2.RspPortfolio.FromString,
                )
        self.PortfolioEx = channel.unary_stream(
                '/serializers.SMABackendService/PortfolioEx',
                request_serializer=server__pb2.ReqNull.SerializeToString,
                response_deserializer=server__pb2.RspPortfolioEx.FromString,
                )
        self.Balance = channel.unary_stream(
                '/serializers.SMABackendService/Balance',
                request_serializer=server__pb2.ReqNormal.SerializeToString,
                response_deserializer=balance__pb2.RspBalance.FromString,
                )
        self.BalanceEx = channel.unary_stream(
                '/serializers.SMABackendService/BalanceEx',
                request_serializer=server__pb2.ReqNormal.SerializeToString,
                response_deserializer=balance__pb2.RspBalanceEx.FromString,
                )
        self.BalanceBenchmark = channel.unary_stream(
                '/serializers.SMABackendService/BalanceBenchmark',
                request_serializer=server__pb2.ReqNormal.SerializeToString,
                response_deserializer=balance__pb2.RspBalanceBenchmark.FromString,
                )
        self.Voucher = channel.unary_stream(
                '/serializers.SMABackendService/Voucher',
                request_serializer=server__pb2.ReqNormal.SerializeToString,
                response_deserializer=transaction__pb2.RspVoucher.FromString,
                )
        self.Trans = channel.unary_stream(
                '/serializers.SMABackendService/Trans',
                request_serializer=server__pb2.ReqNormal.SerializeToString,
                response_deserializer=transaction__pb2.RspTrans.FromString,
                )
        self.Holding = channel.unary_stream(
                '/serializers.SMABackendService/Holding',
                request_serializer=server__pb2.ReqNormal.SerializeToString,
                response_deserializer=transaction__pb2.RspHolding.FromString,
                )
        self.Security = channel.unary_stream(
                '/serializers.SMABackendService/Security',
                request_serializer=server__pb2.ReqNull.SerializeToString,
                response_deserializer=security__pb2.RspSecurity.FromString,
                )
        self.SecurityQuote = channel.unary_stream(
                '/serializers.SMABackendService/SecurityQuote',
                request_serializer=server__pb2.ReqNormal.SerializeToString,
                response_deserializer=security__pb2.RspSecurityQuote.FromString,
                )
        self.SecurityCategory = channel.unary_stream(
                '/serializers.SMABackendService/SecurityCategory',
                request_serializer=server__pb2.ReqNull.SerializeToString,
                response_deserializer=security__pb2.RspSecurityCategory.FromString,
                )
        self.Income = channel.unary_stream(
                '/serializers.SMABackendService/Income',
                request_serializer=server__pb2.ReqNormal.SerializeToString,
                response_deserializer=income__pb2.RspIncome.FromString,
                )
        self.IncomeEx = channel.unary_stream(
                '/serializers.SMABackendService/IncomeEx',
                request_serializer=server__pb2.ReqNormal.SerializeToString,
                response_deserializer=income__pb2.RspIncomeEx.FromString,
                )
        self.Customer = channel.unary_stream(
                '/serializers.SMABackendService/Customer',
                request_serializer=server__pb2.ReqNull.SerializeToString,
                response_deserializer=users__pb2.RspCustomer.FromString,
                )
        self.Sales = channel.unary_stream(
                '/serializers.SMABackendService/Sales',
                request_serializer=server__pb2.ReqNull.SerializeToString,
                response_deserializer=users__pb2.RspSales.FromString,
                )
        self.CustomerMapping = channel.unary_stream(
                '/serializers.SMABackendService/CustomerMapping',
                request_serializer=server__pb2.ReqNull.SerializeToString,
                response_deserializer=users__pb2.RspCustomerMapping.FromString,
                )
        self.SalesMapping = channel.unary_stream(
                '/serializers.SMABackendService/SalesMapping',
                request_serializer=server__pb2.ReqNull.SerializeToString,
                response_deserializer=users__pb2.RspSalesMapping.FromString,
                )
        self.PR = channel.unary_stream(
                '/serializers.SMABackendService/PR',
                request_serializer=server__pb2.ReqNormal.SerializeToString,
                response_deserializer=pr__pb2.RspPR.FromString,
                )


class SMABackendServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Portfolio(self, request, context):
        """获取SMA组合基础信息
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PortfolioEx(self, request, context):
        """获取SMA组合扩充信息
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Balance(self, request, context):
        """获取SMA估值表
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def BalanceEx(self, request, context):
        """获取SMA估值表扩充信息
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def BalanceBenchmark(self, request, context):
        """获取SMA产品基准净值
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Voucher(self, request, context):
        """凭证
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Trans(self, request, context):
        """流水
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Holding(self, request, context):
        """持仓
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Security(self, request, context):
        """证券基础信息
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SecurityQuote(self, request, context):
        """证券行情
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SecurityCategory(self, request, context):
        """证券分类
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Income(self, request, context):
        """基金收益
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def IncomeEx(self, request, context):
        """基金收益扩充信息
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Customer(self, request, context):
        """SMA客户
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Sales(self, request, context):
        """销售
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CustomerMapping(self, request, context):
        """客户产品关联信息
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SalesMapping(self, request, context):
        """销售产品关联信息
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PR(self, request, context):
        """申购赎回记录
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SMABackendServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Portfolio': grpc.unary_stream_rpc_method_handler(
                    servicer.Portfolio,
                    request_deserializer=server__pb2.ReqNull.FromString,
                    response_serializer=server__pb2.RspPortfolio.SerializeToString,
            ),
            'PortfolioEx': grpc.unary_stream_rpc_method_handler(
                    servicer.PortfolioEx,
                    request_deserializer=server__pb2.ReqNull.FromString,
                    response_serializer=server__pb2.RspPortfolioEx.SerializeToString,
            ),
            'Balance': grpc.unary_stream_rpc_method_handler(
                    servicer.Balance,
                    request_deserializer=server__pb2.ReqNormal.FromString,
                    response_serializer=balance__pb2.RspBalance.SerializeToString,
            ),
            'BalanceEx': grpc.unary_stream_rpc_method_handler(
                    servicer.BalanceEx,
                    request_deserializer=server__pb2.ReqNormal.FromString,
                    response_serializer=balance__pb2.RspBalanceEx.SerializeToString,
            ),
            'BalanceBenchmark': grpc.unary_stream_rpc_method_handler(
                    servicer.BalanceBenchmark,
                    request_deserializer=server__pb2.ReqNormal.FromString,
                    response_serializer=balance__pb2.RspBalanceBenchmark.SerializeToString,
            ),
            'Voucher': grpc.unary_stream_rpc_method_handler(
                    servicer.Voucher,
                    request_deserializer=server__pb2.ReqNormal.FromString,
                    response_serializer=transaction__pb2.RspVoucher.SerializeToString,
            ),
            'Trans': grpc.unary_stream_rpc_method_handler(
                    servicer.Trans,
                    request_deserializer=server__pb2.ReqNormal.FromString,
                    response_serializer=transaction__pb2.RspTrans.SerializeToString,
            ),
            'Holding': grpc.unary_stream_rpc_method_handler(
                    servicer.Holding,
                    request_deserializer=server__pb2.ReqNormal.FromString,
                    response_serializer=transaction__pb2.RspHolding.SerializeToString,
            ),
            'Security': grpc.unary_stream_rpc_method_handler(
                    servicer.Security,
                    request_deserializer=server__pb2.ReqNull.FromString,
                    response_serializer=security__pb2.RspSecurity.SerializeToString,
            ),
            'SecurityQuote': grpc.unary_stream_rpc_method_handler(
                    servicer.SecurityQuote,
                    request_deserializer=server__pb2.ReqNormal.FromString,
                    response_serializer=security__pb2.RspSecurityQuote.SerializeToString,
            ),
            'SecurityCategory': grpc.unary_stream_rpc_method_handler(
                    servicer.SecurityCategory,
                    request_deserializer=server__pb2.ReqNull.FromString,
                    response_serializer=security__pb2.RspSecurityCategory.SerializeToString,
            ),
            'Income': grpc.unary_stream_rpc_method_handler(
                    servicer.Income,
                    request_deserializer=server__pb2.ReqNormal.FromString,
                    response_serializer=income__pb2.RspIncome.SerializeToString,
            ),
            'IncomeEx': grpc.unary_stream_rpc_method_handler(
                    servicer.IncomeEx,
                    request_deserializer=server__pb2.ReqNormal.FromString,
                    response_serializer=income__pb2.RspIncomeEx.SerializeToString,
            ),
            'Customer': grpc.unary_stream_rpc_method_handler(
                    servicer.Customer,
                    request_deserializer=server__pb2.ReqNull.FromString,
                    response_serializer=users__pb2.RspCustomer.SerializeToString,
            ),
            'Sales': grpc.unary_stream_rpc_method_handler(
                    servicer.Sales,
                    request_deserializer=server__pb2.ReqNull.FromString,
                    response_serializer=users__pb2.RspSales.SerializeToString,
            ),
            'CustomerMapping': grpc.unary_stream_rpc_method_handler(
                    servicer.CustomerMapping,
                    request_deserializer=server__pb2.ReqNull.FromString,
                    response_serializer=users__pb2.RspCustomerMapping.SerializeToString,
            ),
            'SalesMapping': grpc.unary_stream_rpc_method_handler(
                    servicer.SalesMapping,
                    request_deserializer=server__pb2.ReqNull.FromString,
                    response_serializer=users__pb2.RspSalesMapping.SerializeToString,
            ),
            'PR': grpc.unary_stream_rpc_method_handler(
                    servicer.PR,
                    request_deserializer=server__pb2.ReqNormal.FromString,
                    response_serializer=pr__pb2.RspPR.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'serializers.SMABackendService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SMABackendService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Portfolio(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/Portfolio',
            server__pb2.ReqNull.SerializeToString,
            server__pb2.RspPortfolio.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PortfolioEx(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/PortfolioEx',
            server__pb2.ReqNull.SerializeToString,
            server__pb2.RspPortfolioEx.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Balance(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/Balance',
            server__pb2.ReqNormal.SerializeToString,
            balance__pb2.RspBalance.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def BalanceEx(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/BalanceEx',
            server__pb2.ReqNormal.SerializeToString,
            balance__pb2.RspBalanceEx.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def BalanceBenchmark(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/BalanceBenchmark',
            server__pb2.ReqNormal.SerializeToString,
            balance__pb2.RspBalanceBenchmark.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Voucher(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/Voucher',
            server__pb2.ReqNormal.SerializeToString,
            transaction__pb2.RspVoucher.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Trans(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/Trans',
            server__pb2.ReqNormal.SerializeToString,
            transaction__pb2.RspTrans.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Holding(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/Holding',
            server__pb2.ReqNormal.SerializeToString,
            transaction__pb2.RspHolding.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Security(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/Security',
            server__pb2.ReqNull.SerializeToString,
            security__pb2.RspSecurity.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SecurityQuote(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/SecurityQuote',
            server__pb2.ReqNormal.SerializeToString,
            security__pb2.RspSecurityQuote.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SecurityCategory(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/SecurityCategory',
            server__pb2.ReqNull.SerializeToString,
            security__pb2.RspSecurityCategory.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Income(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/Income',
            server__pb2.ReqNormal.SerializeToString,
            income__pb2.RspIncome.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def IncomeEx(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/IncomeEx',
            server__pb2.ReqNormal.SerializeToString,
            income__pb2.RspIncomeEx.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Customer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/Customer',
            server__pb2.ReqNull.SerializeToString,
            users__pb2.RspCustomer.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Sales(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/Sales',
            server__pb2.ReqNull.SerializeToString,
            users__pb2.RspSales.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CustomerMapping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/CustomerMapping',
            server__pb2.ReqNull.SerializeToString,
            users__pb2.RspCustomerMapping.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SalesMapping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/SalesMapping',
            server__pb2.ReqNull.SerializeToString,
            users__pb2.RspSalesMapping.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PR(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/serializers.SMABackendService/PR',
            server__pb2.ReqNormal.SerializeToString,
            pr__pb2.RspPR.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)