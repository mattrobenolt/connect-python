# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: elizav1/eliza.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13\x65lizav1/eliza.proto\x12\x19\x62uf.connect.demo.eliza.v1\"(\n\nSayRequest\x12\x1a\n\x08sentence\x18\x01 \x01(\tR\x08sentence\")\n\x0bSayResponse\x12\x1a\n\x08sentence\x18\x01 \x01(\tR\x08sentence\"-\n\x0f\x43onverseRequest\x12\x1a\n\x08sentence\x18\x01 \x01(\tR\x08sentence\".\n\x10\x43onverseResponse\x12\x1a\n\x08sentence\x18\x01 \x01(\tR\x08sentence\"&\n\x10IntroduceRequest\x12\x12\n\x04name\x18\x01 \x01(\tR\x04name\"/\n\x11IntroduceResponse\x12\x1a\n\x08sentence\x18\x01 \x01(\tR\x08sentence2\xbd\x02\n\x0c\x45lizaService\x12V\n\x03Say\x12%.buf.connect.demo.eliza.v1.SayRequest\x1a&.buf.connect.demo.eliza.v1.SayResponse\"\x00\x12i\n\x08\x43onverse\x12*.buf.connect.demo.eliza.v1.ConverseRequest\x1a+.buf.connect.demo.eliza.v1.ConverseResponse\"\x00(\x01\x30\x01\x12j\n\tIntroduce\x12+.buf.connect.demo.eliza.v1.IntroduceRequest\x1a,.buf.connect.demo.eliza.v1.IntroduceResponse\"\x00\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'elizav1.eliza_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_SAYREQUEST']._serialized_start=50
  _globals['_SAYREQUEST']._serialized_end=90
  _globals['_SAYRESPONSE']._serialized_start=92
  _globals['_SAYRESPONSE']._serialized_end=133
  _globals['_CONVERSEREQUEST']._serialized_start=135
  _globals['_CONVERSEREQUEST']._serialized_end=180
  _globals['_CONVERSERESPONSE']._serialized_start=182
  _globals['_CONVERSERESPONSE']._serialized_end=228
  _globals['_INTRODUCEREQUEST']._serialized_start=230
  _globals['_INTRODUCEREQUEST']._serialized_end=268
  _globals['_INTRODUCERESPONSE']._serialized_start=270
  _globals['_INTRODUCERESPONSE']._serialized_end=317
  _globals['_ELIZASERVICE']._serialized_start=320
  _globals['_ELIZASERVICE']._serialized_end=637
# @@protoc_insertion_point(module_scope)
