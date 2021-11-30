# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: backtest.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='backtest.proto',
  package='services',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0e\x62\x61\x63ktest.proto\x12\x08services\"5\n\x07Request\x1a\r\n\x0bNullRequest\x1a\x1b\n\x0b\x44\x61teRequest\x12\x0c\n\x04\x64\x61te\x18\x01 \x01(\t\"\x8f\x01\n\x08Response\x1a*\n\x0bNavResponse\x12\x1b\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\r.services.Nav\x1a\x30\n\x0eWeightResponse\x12\x1e\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x10.services.Weight\x1a%\n\x0eStatusResponse\x12\x13\n\x0bstatus_code\x18\x01 \x01(\x04\"6\n\x03Nav\x12\x11\n\tport_code\x18\x01 \x01(\x04\x12\x0c\n\x04\x64\x61te\x18\x02 \x01(\t\x12\x0e\n\x06unitnv\x18\x03 \x01(\x02\"\xe0\x01\n\x06Weight\x12\x0c\n\x04\x64\x61te\x18\x01 \x01(\t\x12\x13\n\x0btarget_risk\x18\x02 \x01(\x02\x12\x0e\n\x06\x65quity\x18\x03 \x01(\x02\x12\x14\n\x0c\x66ixed_income\x18\x04 \x01(\x02\x12\x13\n\x0b\x61lternative\x18\x05 \x01(\x02\x12\x10\n\x08monetary\x18\x06 \x01(\x02\x12\r\n\x05hs300\x18\x07 \x01(\x02\x12\r\n\x05zz500\x18\x08 \x01(\x02\x12\n\n\x02zz\x18\t \x01(\x02\x12\n\n\x02hs\x18\n \x01(\x02\x12\x0b\n\x03llz\x18\x0b \x01(\x02\x12\x0b\n\x03xyz\x18\x0c \x01(\x02\x12\n\n\x02hb\x18\r \x01(\x02\x12\n\n\x02hj\x18\x0e \x01(\x02\x32\xad\x03\n\x0e\x42\x61\x63ktestServer\x12U\n\x14StandardPortfolioNav\x12\x1d.services.Request.NullRequest\x1a\x1e.services.Response.NavResponse\x12J\n\x06Weight\x12\x1d.services.Request.NullRequest\x1a!.services.Response.WeightResponse\x12R\n\x11IndexPortfolioNav\x12\x1d.services.Request.NullRequest\x1a\x1e.services.Response.NavResponse\x12V\n\x15\x46undIndexPortfolioNav\x12\x1d.services.Request.NullRequest\x1a\x1e.services.Response.NavResponse\x12L\n\x08SyncData\x12\x1d.services.Request.NullRequest\x1a!.services.Response.StatusResponseb\x06proto3'
)




_REQUEST_NULLREQUEST = _descriptor.Descriptor(
  name='NullRequest',
  full_name='services.Request.NullRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=39,
  serialized_end=52,
)

_REQUEST_DATEREQUEST = _descriptor.Descriptor(
  name='DateRequest',
  full_name='services.Request.DateRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='date', full_name='services.Request.DateRequest.date', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=54,
  serialized_end=81,
)

_REQUEST = _descriptor.Descriptor(
  name='Request',
  full_name='services.Request',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[_REQUEST_NULLREQUEST, _REQUEST_DATEREQUEST, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=28,
  serialized_end=81,
)


_RESPONSE_NAVRESPONSE = _descriptor.Descriptor(
  name='NavResponse',
  full_name='services.Response.NavResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='data', full_name='services.Response.NavResponse.data', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=96,
  serialized_end=138,
)

_RESPONSE_WEIGHTRESPONSE = _descriptor.Descriptor(
  name='WeightResponse',
  full_name='services.Response.WeightResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='data', full_name='services.Response.WeightResponse.data', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=140,
  serialized_end=188,
)

_RESPONSE_STATUSRESPONSE = _descriptor.Descriptor(
  name='StatusResponse',
  full_name='services.Response.StatusResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='status_code', full_name='services.Response.StatusResponse.status_code', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=190,
  serialized_end=227,
)

_RESPONSE = _descriptor.Descriptor(
  name='Response',
  full_name='services.Response',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[_RESPONSE_NAVRESPONSE, _RESPONSE_WEIGHTRESPONSE, _RESPONSE_STATUSRESPONSE, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=84,
  serialized_end=227,
)


_NAV = _descriptor.Descriptor(
  name='Nav',
  full_name='services.Nav',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='port_code', full_name='services.Nav.port_code', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='date', full_name='services.Nav.date', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='unitnv', full_name='services.Nav.unitnv', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=229,
  serialized_end=283,
)


_WEIGHT = _descriptor.Descriptor(
  name='Weight',
  full_name='services.Weight',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='date', full_name='services.Weight.date', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='target_risk', full_name='services.Weight.target_risk', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='equity', full_name='services.Weight.equity', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='fixed_income', full_name='services.Weight.fixed_income', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='alternative', full_name='services.Weight.alternative', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='monetary', full_name='services.Weight.monetary', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='hs300', full_name='services.Weight.hs300', index=6,
      number=7, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='zz500', full_name='services.Weight.zz500', index=7,
      number=8, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='zz', full_name='services.Weight.zz', index=8,
      number=9, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='hs', full_name='services.Weight.hs', index=9,
      number=10, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='llz', full_name='services.Weight.llz', index=10,
      number=11, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='xyz', full_name='services.Weight.xyz', index=11,
      number=12, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='hb', full_name='services.Weight.hb', index=12,
      number=13, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='hj', full_name='services.Weight.hj', index=13,
      number=14, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=286,
  serialized_end=510,
)

_REQUEST_NULLREQUEST.containing_type = _REQUEST
_REQUEST_DATEREQUEST.containing_type = _REQUEST
_RESPONSE_NAVRESPONSE.fields_by_name['data'].message_type = _NAV
_RESPONSE_NAVRESPONSE.containing_type = _RESPONSE
_RESPONSE_WEIGHTRESPONSE.fields_by_name['data'].message_type = _WEIGHT
_RESPONSE_WEIGHTRESPONSE.containing_type = _RESPONSE
_RESPONSE_STATUSRESPONSE.containing_type = _RESPONSE
DESCRIPTOR.message_types_by_name['Request'] = _REQUEST
DESCRIPTOR.message_types_by_name['Response'] = _RESPONSE
DESCRIPTOR.message_types_by_name['Nav'] = _NAV
DESCRIPTOR.message_types_by_name['Weight'] = _WEIGHT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Request = _reflection.GeneratedProtocolMessageType('Request', (_message.Message,), {

  'NullRequest' : _reflection.GeneratedProtocolMessageType('NullRequest', (_message.Message,), {
    'DESCRIPTOR' : _REQUEST_NULLREQUEST,
    '__module__' : 'backtest_pb2'
    # @@protoc_insertion_point(class_scope:services.Request.NullRequest)
    })
  ,

  'DateRequest' : _reflection.GeneratedProtocolMessageType('DateRequest', (_message.Message,), {
    'DESCRIPTOR' : _REQUEST_DATEREQUEST,
    '__module__' : 'backtest_pb2'
    # @@protoc_insertion_point(class_scope:services.Request.DateRequest)
    })
  ,
  'DESCRIPTOR' : _REQUEST,
  '__module__' : 'backtest_pb2'
  # @@protoc_insertion_point(class_scope:services.Request)
  })
_sym_db.RegisterMessage(Request)
_sym_db.RegisterMessage(Request.NullRequest)
_sym_db.RegisterMessage(Request.DateRequest)

Response = _reflection.GeneratedProtocolMessageType('Response', (_message.Message,), {

  'NavResponse' : _reflection.GeneratedProtocolMessageType('NavResponse', (_message.Message,), {
    'DESCRIPTOR' : _RESPONSE_NAVRESPONSE,
    '__module__' : 'backtest_pb2'
    # @@protoc_insertion_point(class_scope:services.Response.NavResponse)
    })
  ,

  'WeightResponse' : _reflection.GeneratedProtocolMessageType('WeightResponse', (_message.Message,), {
    'DESCRIPTOR' : _RESPONSE_WEIGHTRESPONSE,
    '__module__' : 'backtest_pb2'
    # @@protoc_insertion_point(class_scope:services.Response.WeightResponse)
    })
  ,

  'StatusResponse' : _reflection.GeneratedProtocolMessageType('StatusResponse', (_message.Message,), {
    'DESCRIPTOR' : _RESPONSE_STATUSRESPONSE,
    '__module__' : 'backtest_pb2'
    # @@protoc_insertion_point(class_scope:services.Response.StatusResponse)
    })
  ,
  'DESCRIPTOR' : _RESPONSE,
  '__module__' : 'backtest_pb2'
  # @@protoc_insertion_point(class_scope:services.Response)
  })
_sym_db.RegisterMessage(Response)
_sym_db.RegisterMessage(Response.NavResponse)
_sym_db.RegisterMessage(Response.WeightResponse)
_sym_db.RegisterMessage(Response.StatusResponse)

Nav = _reflection.GeneratedProtocolMessageType('Nav', (_message.Message,), {
  'DESCRIPTOR' : _NAV,
  '__module__' : 'backtest_pb2'
  # @@protoc_insertion_point(class_scope:services.Nav)
  })
_sym_db.RegisterMessage(Nav)

Weight = _reflection.GeneratedProtocolMessageType('Weight', (_message.Message,), {
  'DESCRIPTOR' : _WEIGHT,
  '__module__' : 'backtest_pb2'
  # @@protoc_insertion_point(class_scope:services.Weight)
  })
_sym_db.RegisterMessage(Weight)



_BACKTESTSERVER = _descriptor.ServiceDescriptor(
  name='BacktestServer',
  full_name='services.BacktestServer',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=513,
  serialized_end=942,
  methods=[
  _descriptor.MethodDescriptor(
    name='StandardPortfolioNav',
    full_name='services.BacktestServer.StandardPortfolioNav',
    index=0,
    containing_service=None,
    input_type=_REQUEST_NULLREQUEST,
    output_type=_RESPONSE_NAVRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='Weight',
    full_name='services.BacktestServer.Weight',
    index=1,
    containing_service=None,
    input_type=_REQUEST_NULLREQUEST,
    output_type=_RESPONSE_WEIGHTRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='IndexPortfolioNav',
    full_name='services.BacktestServer.IndexPortfolioNav',
    index=2,
    containing_service=None,
    input_type=_REQUEST_NULLREQUEST,
    output_type=_RESPONSE_NAVRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='FundIndexPortfolioNav',
    full_name='services.BacktestServer.FundIndexPortfolioNav',
    index=3,
    containing_service=None,
    input_type=_REQUEST_NULLREQUEST,
    output_type=_RESPONSE_NAVRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='SyncData',
    full_name='services.BacktestServer.SyncData',
    index=4,
    containing_service=None,
    input_type=_REQUEST_NULLREQUEST,
    output_type=_RESPONSE_STATUSRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_BACKTESTSERVER)

DESCRIPTOR.services_by_name['BacktestServer'] = _BACKTESTSERVER

# @@protoc_insertion_point(module_scope)
