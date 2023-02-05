# -*- coding: utf-8 -*-


from google.protobuf import json_format


class ProtobufHelper:

    @staticmethod
    def to_obj(data, cls):
        if data is None:
            return None
        return json_format.ParseDict(data, cls(), ignore_unknown_fields=True)

    @staticmethod
    def batch_to_obj(data, cls):
        if not data:
            return []
        return [ProtobufHelper.to_obj(d, cls) for d in data]

    @staticmethod
    def to_json(data):
        if data is None:
            return None
        return json_format.MessageToDict(
            data, including_default_value_fields=True,
            preserving_proto_field_name=True
        )

    @staticmethod
    def batch_to_json(data):
        if not data:
            return []
        return [ProtobufHelper.to_json(d) for d in data]
