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
        """deprecated, use to_dict instead"""
        if data is None:
            return None
        if isinstance(data, str):
            return data
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data
        if isinstance(data, bool):
            return data
        return json_format.MessageToDict(
            data, including_default_value_fields=True,
            preserving_proto_field_name=True
        )

    @staticmethod
    def to_dict(data):
        if data is None:
            return None
        if isinstance(data, str):
            return data
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data
        if isinstance(data, bool):
            return data
        return json_format.MessageToDict(
            data, including_default_value_fields=True,
            preserving_proto_field_name=True
        )

    @staticmethod
    def batch_to_json(data):
        if not data:
            return []
        return [ProtobufHelper.to_json(d) for d in data]

    @staticmethod
    def to_json_v2(msg):
        return json_format.MessageToJson(
            msg,
            including_default_value_fields=True,
            preserving_proto_field_name=True)

    @staticmethod
    def to_obj_v2(data, cls):
        if data is None:
            return None
        return json_format.Parse(data, cls(), ignore_unknown_fields=True)
