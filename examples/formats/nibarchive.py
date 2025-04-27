# Copyright (C) MatrixEditor 2023-2025
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# NOTE: If you decide to use the annotation feature, you have to manually
# apply the S_EVAL_ANNOTATIONS option to all structs
# from __future__ import annotations
import enum
import sys

from caterpillar.fields import *
from caterpillar.shortcuts import (
    struct,
    this,
    unpack_file,
    opt,
    LittleEndian,
    ctx,
    pack_file,
)

try:
    # colorized + structured output
    from rich import print
except ImportError:
    pass

# These flags will be applied to all structs and fields
opt.set_struct_flags(opt.S_REPLACE_TYPES, opt.S_SLOTS)
opt.set_field_flags(VARINT_LSB)

try:
    from numpy import array

    opt.O_ARRAY_FACTORY.value = array
except ImportError:
    pass


@struct(order=LittleEndian)
class NIBHeader:
    """Example class doc comment"""

    # Here we define a constant value, which will raise an exception
    # upon a different parsed value.
    magic: b"NIBArchive"
    """example field doc comment"""

    # Primitive types can be used just like this
    unknown_1: int32
    """second field doc comment"""

    unknown_2: int32
    object_count: int32
    offset_objects: int32
    key_count: int32
    offset_keys: int32
    value_count: int32
    offset_values: int32
    class_name_count: int32
    offset_class_names: int32


@struct(order=LittleEndian)
class NIBClassName:
    # NOTE: the custom class 'vint' is marked as a singleton class. Therefore,
    # we can use it directly. Otherwise, we have to create an instance first,
    # before we can use the struct class.
    length: vint
    extras_count: vint
    # This struct will remove all extra null-bytes padding
    name: CString(this.length)
    # Arrays can be created just like this:
    extras: int32[this.extras_count]


# Note that the returned string instance here may contain extra null-bytes
# at the end.
NIBKey = Prefixed(vint, encoding="utf-8")


class ValueType(enum.Enum):
    UNKNOWN = -1
    INT8 = 0
    INT16 = 1
    INT32 = 2
    INT64 = 3
    BOOL_TRUE = 4
    BOOL_FALSE = 5
    FLOAT = 6
    DOUBLE = 7
    DATA = 8
    NIL = 9
    OBJECT_REF = 10


# The raw data is just copied from the stream. If we don't specify an
# encoding, the raw bytes or copied.
NIBData = Prefixed(vint)


@struct(order=LittleEndian)
class NIBValue:
    key: vint
    # NOTE the use of a default value; otherwise None would be set.
    type: Enum(ValueType, uint8, ValueType.UNKNOWN)
    # The field below describes a simple switch-case structure.
    value: Field(this.type) >> {
        ValueType.INT8: int8,
        ValueType.INT16: int16,
        ValueType.INT32: int32,
        ValueType.INT64: int64,
        ValueType.BOOL_TRUE: Computed(True),
        ValueType.BOOL_FALSE: Computed(False),
        ValueType.FLOAT: float32,
        ValueType.DOUBLE: double,
        ValueType.DATA: NIBData,
        ValueType.NIL: Computed(None),
        ValueType.OBJECT_REF: int32,
        # The following line shows how to manually return the parsed value (in
        # this case it would be the result of this.type). NOTE that the value
        # is only stored temporarily in the current context (not this-context).
        #
        # If this option is not specified and none of the above matched the input,
        # an exception will be thrown.
        DEFAULT_OPTION: Computed(ctx._value),
    }


@struct(order=LittleEndian)
class NIBObject:
    # same usage as above
    name: vint
    values: vint
    value_count: vint


@struct(order=LittleEndian)
class NIBArchive:
    # Nested structs can be defined as simle as this:
    header: NIBHeader

    # All following fields are marked with '@': The parser will jump temporarily
    # to the position specified after the operator. Use | F_KEEP_POSITION to
    # continue parsing at the resulting position
    objects: NIBObject[this.header.object_count] @ this.header.offset_objects
    keys: NIBKey[this.header.key_count] @ this.header.offset_keys
    values: NIBValue[this.header.value_count] @ this.header.offset_values

    # NOTE: we can reference parsed values using 'this.foo' but methods or properties
    # can't be used.
    class_names: NIBClassName[
        this.header.class_name_count
    ] @ this.header.offset_class_names


# print(NIBArchive.__struct__.fields)
if __name__ == "__main__":
    obj = unpack_file(NIBArchive, sys.argv[1])
    print(obj)
    pack_file(obj, sys.argv[2], use_tempfile=True)
