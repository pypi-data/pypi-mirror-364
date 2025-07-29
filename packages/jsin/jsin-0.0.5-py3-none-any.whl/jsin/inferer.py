'''
define the json inferer to construct
a schematic tree from a loaded json object
'''

from enum import StrEnum
from dataclasses import dataclass
from collections.abc import Mapping
from collections.abc import Collection
from typing import Self

from . import schematic_tree_nodes as stn

from .exceptions import UnidentifiableTypeError


class JsonPrimitiveType(StrEnum):
    '''
    enum class describing JSON primitive types
    '''
    NULL = 'NULL'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    ARRAY = 'ARRAY'
    OBJECT = 'OBJECT'

    @classmethod
    def tell(cls, obj) -> Self:
        '''
        identify the JSON primitive type of an object
        '''

        if obj is None:
            return cls.NULL

        if isinstance(obj, bool):
            if obj:
                return cls.TRUE
            return cls.FALSE

        if isinstance(obj, (int, float)):
            return cls.NUMBER

        if isinstance(obj, str):
            return cls.STRING

        # dict() is a Collection
        # so we must check for Mapping first
        if isinstance(obj, Mapping):
            return cls.OBJECT

        if isinstance(obj, Collection):
            return cls.ARRAY

        raise UnidentifiableTypeError(obj)


@dataclass
class InfererOptions():
    infer_str_enum: bool = True
    infer_key_indexed_array: bool = True
    merge_subtrees: bool = True


class Inferer():
    options: InfererOptions
    nodes: set[stn.BaseNode]

    def __init__(self, options: InfererOptions):
        self.options = options
        self.nodes = set()

    def infer(self, obj):
        node: stn.BaseNode | None = None
        t = JsonPrimitiveType.tell(obj)

        match t:
            case JsonPrimitiveType.NULL:
                node = stn.NullNode()

            case JsonPrimitiveType.TRUE | JsonPrimitiveType.FALSE:
                node = stn.BooleanNode()

            case JsonPrimitiveType.NUMBER:
                node = stn.NumberNode(contains_float=isinstance(obj, float))

            case JsonPrimitiveType.STRING:
                node = stn.StringNode(initial_string=obj)
