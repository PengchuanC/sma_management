# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: services.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import services.sync_pb2 as sync__pb2
import services.transfer_pb2 as transfer__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='services.proto',
  package='services',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0eservices.proto\x12\x08services\x1a\nsync.proto\x1a\x0etransfer.proto2\xc7\x07\n\x06Server\x12\x35\n\x04Ping\x12\x15.services.PingRequest\x1a\x16.services.PingResponse\x12\x30\n\x07SyncAll\x12\x11.services.Request\x1a\x12.services.Response\x12\x34\n\x0bSyncPrimary\x12\x11.services.Request\x1a\x12.services.Response\x12\x35\n\x0cSMAPortfolio\x12\x0e.services.NULL\x1a\x13.services.Portfolio0\x01\x12\x45\n\x14SMAPortfolioExpanded\x12\x0e.services.NULL\x1a\x1b.services.PortfolioExpanded0\x01\x12\x35\n\nSMABalance\x12\x12.services.TRequest\x1a\x11.services.Balance0\x01\x12\x45\n\x12SMABalanceExpanded\x12\x12.services.TRequest\x1a\x19.services.BalanceExpanded0\x01\x12\x33\n\tSMAIncome\x12\x12.services.TRequest\x1a\x10.services.Income0\x01\x12=\n\x0eSMAIncomeAsset\x12\x12.services.TRequest\x1a\x15.services.IncomeAsset0\x01\x12\x35\n\nSMAHolding\x12\x12.services.TRequest\x1a\x11.services.Holding0\x01\x12=\n\x0eSMATransaction\x12\x12.services.TRequest\x1a\x15.services.Transaction0\x01\x12\x39\n\x0cSMADetailFee\x12\x12.services.TRequest\x1a\x13.services.DetailFee0\x01\x12\x37\n\x0bSMASecurity\x12\x12.services.TRequest\x1a\x12.services.Security0\x01\x12\x41\n\x10SMASecurityQuote\x12\x12.services.TRequest\x1a\x17.services.SecurityQuote0\x01\x12\x42\n\x0cSMABenchmark\x12\x12.services.TRequest\x1a\x1c.services.ValuationBenchmark0\x01\x12=\n\x0eSMAInterestTax\x12\x12.services.TRequest\x1a\x15.services.InterestTax0\x01\x62\x06proto3'
  ,
  dependencies=[sync__pb2.DESCRIPTOR,transfer__pb2.DESCRIPTOR,])



_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_SERVER = _descriptor.ServiceDescriptor(
  name='Server',
  full_name='services.Server',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=57,
  serialized_end=1024,
  methods=[
  _descriptor.MethodDescriptor(
    name='Ping',
    full_name='services.Server.Ping',
    index=0,
    containing_service=None,
    input_type=sync__pb2._PINGREQUEST,
    output_type=sync__pb2._PINGRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SyncAll',
    full_name='services.Server.SyncAll',
    index=1,
    containing_service=None,
    input_type=sync__pb2._REQUEST,
    output_type=sync__pb2._RESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SyncPrimary',
    full_name='services.Server.SyncPrimary',
    index=2,
    containing_service=None,
    input_type=sync__pb2._REQUEST,
    output_type=sync__pb2._RESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMAPortfolio',
    full_name='services.Server.SMAPortfolio',
    index=3,
    containing_service=None,
    input_type=transfer__pb2._NULL,
    output_type=transfer__pb2._PORTFOLIO,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMAPortfolioExpanded',
    full_name='services.Server.SMAPortfolioExpanded',
    index=4,
    containing_service=None,
    input_type=transfer__pb2._NULL,
    output_type=transfer__pb2._PORTFOLIOEXPANDED,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMABalance',
    full_name='services.Server.SMABalance',
    index=5,
    containing_service=None,
    input_type=transfer__pb2._TREQUEST,
    output_type=transfer__pb2._BALANCE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMABalanceExpanded',
    full_name='services.Server.SMABalanceExpanded',
    index=6,
    containing_service=None,
    input_type=transfer__pb2._TREQUEST,
    output_type=transfer__pb2._BALANCEEXPANDED,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMAIncome',
    full_name='services.Server.SMAIncome',
    index=7,
    containing_service=None,
    input_type=transfer__pb2._TREQUEST,
    output_type=transfer__pb2._INCOME,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMAIncomeAsset',
    full_name='services.Server.SMAIncomeAsset',
    index=8,
    containing_service=None,
    input_type=transfer__pb2._TREQUEST,
    output_type=transfer__pb2._INCOMEASSET,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMAHolding',
    full_name='services.Server.SMAHolding',
    index=9,
    containing_service=None,
    input_type=transfer__pb2._TREQUEST,
    output_type=transfer__pb2._HOLDING,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMATransaction',
    full_name='services.Server.SMATransaction',
    index=10,
    containing_service=None,
    input_type=transfer__pb2._TREQUEST,
    output_type=transfer__pb2._TRANSACTION,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMADetailFee',
    full_name='services.Server.SMADetailFee',
    index=11,
    containing_service=None,
    input_type=transfer__pb2._TREQUEST,
    output_type=transfer__pb2._DETAILFEE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMASecurity',
    full_name='services.Server.SMASecurity',
    index=12,
    containing_service=None,
    input_type=transfer__pb2._TREQUEST,
    output_type=transfer__pb2._SECURITY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMASecurityQuote',
    full_name='services.Server.SMASecurityQuote',
    index=13,
    containing_service=None,
    input_type=transfer__pb2._TREQUEST,
    output_type=transfer__pb2._SECURITYQUOTE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMABenchmark',
    full_name='services.Server.SMABenchmark',
    index=14,
    containing_service=None,
    input_type=transfer__pb2._TREQUEST,
    output_type=transfer__pb2._VALUATIONBENCHMARK,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SMAInterestTax',
    full_name='services.Server.SMAInterestTax',
    index=15,
    containing_service=None,
    input_type=transfer__pb2._TREQUEST,
    output_type=transfer__pb2._INTERESTTAX,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_SERVER)

DESCRIPTOR.services_by_name['Server'] = _SERVER

# @@protoc_insertion_point(module_scope)
