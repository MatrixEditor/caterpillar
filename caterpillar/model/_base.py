# Copyright (C) MatrixEditor 2023
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
import re

from typing import Optional
from typing import List, Dict, Any
from typing import Set, Iterable
from dataclasses import dataclass

from caterpillar.abc import (
    _StructLike,
    _ContextLike,
    _StreamType,
)
from caterpillar.context import Context
from caterpillar.byteorder import (
    ByteOrder,
    Arch,
)
from caterpillar.exception import StructException
from caterpillar.options import (
    S_DISCARD_CONST,
    S_DISCARD_UNNAMED,
    S_UNION,
    Flag,
)
from caterpillar.fields import Field, INVALID_DEFAULT


@dataclass(init=False)
class Sequence(_StructLike):
    fields: List[Field]
    """A list of all fields defined in this struct.

    This attribute stores the fields in an *ordered* collection, whereby ordered
    means, relative to their initial class declaration position. These fields can
    be modified using ``add_field``, ``del_field`` or the operators ``+`` and
    ``-``.
    """

    order: Optional[ByteOrder]
    """
    Optional configuration value for the byte order of a field.__annotations__
    """

    arch: Optional[Arch]
    """
    Global architecture definition (will be inferred on all fields)
    """

    options: Set[Flag]
    """
    Additional options specifying what to include in the final class.
    """

    field_options: Set[Flag]
    """
    Global field flags that will be applied on all fields.
    """

    def __init__(
        self,
        fields: Optional[Dict[str, Field]] = None,
        order: Optional[ByteOrder] = None,
        arch: Optional[Arch] = None,
        options: Iterable[Flag] = None,
        field_options: Iterable[Flag] = None,
    ) -> None:
        self.arch = arch
        self.order = order
        self.options = set(options or [])
        self.field_options = set(field_options or [])

        # these fields will be set or used while processing the model type
        self._member_map_ = fields or {}
        self.fields: List[Field] = list((fields or {}).values())
        # Process all fields in the model
        self._process_fields()

    def has_option(self, option: Flag) -> bool:
        """
        Check if the struct has a specific option.

        :param option: The option to check.
        :return: True if the struct has the specified option, else False.
        """
        return option in self.options

    def _included(self, name: str, default: Optional[Any]) -> bool:
        """
        Check if a field with the given name should be included.

        :param name: The name of the field.
        :param default: The default value of the field.
        :return: True if the field should be included, else False.
        """
        if self.has_option(S_DISCARD_UNNAMED):
            if re.match(r"^_[0-9]*$", name):
                return False

        if self.has_option(S_DISCARD_CONST):
            if default != INVALID_DEFAULT:
                return False

        return True

    def _process_fields(self) -> None:
        pass

    def add_field(self, name: str, field: Field, included: bool = False) -> None:
        """
        Add a field to the struct.

        :param name: The name of the field.
        :param field: The field to add.
        :param included: True if the field should be included, else False.
        """
        self.fields.append(field)
        setattr(field, "__name__", name)
        if included:
            self._member_map_[name] = field

    def is_union(self) -> bool:
        """
        Check if the struct is a union.

        :return: True if the struct is a union, else False.
        """
        return self.has_option(S_UNION)

    def __size__(self, context: _ContextLike) -> int:
        """
        Get the size of the struct.

        :param context: The context of the struct.
        :return: The size of the struct.
        """
        sizes = []
        base_path = context._path
        for field in self.fields:
            context._path = ".".join([base_path, field.get_name()])
            sizes.append(field.__size__(context))

        return max(sizes) if self.is_union() else sum(sizes)

    def unpack_one(self, stream: _StreamType, context: _ContextLike) -> Optional[Any]:
        # At first, we define the object context where the parsed values
        # will be stored
        init_data: Dict[str, Any] = {}
        context._obj = Context(_parent=context)

        base_path = context._path
        start = stream.tell()
        max_size = 0

        for field in self.fields:
            pos = stream.tell()
            name = field.get_name()
            # The context path has to be changed accordingly
            context._path = ".".join([base_path, name])
            result = field.__unpack__(stream, context)
            # the object's data shouldn't include removed fields
            context._obj[name] = result
            if name in self._member_map_:
                init_data[name] = result

            if self.is_union():
                # This union implementation will cover the max size
                max_size = max(max_size, stream.tell() - pos)
                stream.seek(start)

        obj = init_data
        if self.is_union():
            # Reset the stream position
            stream.seek(start + max_size)
        return obj

    def __unpack__(self, stream: _StreamType, context: _ContextLike) -> Optional[Any]:
        """
        Unpack the struct from the stream.

        :param stream: The stream to unpack from.
        :param context: The context of the struct.
        :return: The unpacked object.
        """
        base_path = context._path
        this_context = Context(_parent=context, _io=stream, _path=base_path)
        # See __pack__ for more information
        field: Optional[Field] = context.get("_field")
        if field and field.is_seq():
            length: int = field.length(context)  # use parent context here
            values = []  # always list (maybe add factory)

            this_context._length = length
            this_context._lst = values
            this_context._field = field
            # REVISIT: add _pos to context
            for i in range(length):
                this_context._index = i
                value = self.unpack_one(stream, this_context)
                values.append(value)
            return values

        return self.unpack_one(stream, this_context)

    def get_value(self, obj: Any, name: str, field: Field) -> Optional[Any]:
        return obj.get(name, None)

    def pack_one(
        self, obj: Dict[str, Any], stream: _StreamType, context: _ContextLike
    ) -> None:
        is_union = self.is_union()
        max_size = 0
        union_field: Optional[_StructLike] = None
        base_path: str = context._path

        for field in self.fields:
            # The name has to be set (important for current context)
            name = field.get_name()
            if name is None:
                raise StructException(f"Could not measure a field's name: {field!r}")

            if is_union:
                # Union is only applicable for non-dynamic structs
                size: int = field.__size__(context)
                if size > max_size:
                    max_size = size
                    union_field = field
            else:
                # Default behaviour: let the field write its content to the stream.
                context._path = ".".join([base_path, name])
                if name in self._member_map_:
                    value = self.get_value(obj, name, field)
                else:
                    # REVISIT: this line might not be necessary if const fields alredy
                    # use their internal value.
                    value = field.default if field.default != INVALID_DEFAULT else None
                field.__pack__(value, stream, context)

        if is_union:
            if union_field is None:
                raise StructException(
                    f"Invalid union config: no fields declared! path={context._path!r}"
                )

            name = union_field.get_name()
            context._path = ".".join([base_path, "<value>"])
            # REVISIT: are constant values allowed here? + name validation?
            value = self.get_value(obj, name, union_field)
            union_field.__pack__(value, stream, context)

    def __pack__(self, obj: Any, stream: _StreamType, context: _ContextLike) -> None:
        # REVISIT: code cleanup
        base_path = context._path
        this_context = Context(_parent=context, _io=stream, _path=base_path, _obj=obj)
        max_size = 0

        is_union = self.is_union()
        # As structs can be used in field definitions a field will call this struct
        # and could potentially be a sequence. Therefore, we have to check whether we
        # should unpack multiple objects.
        field: Optional[Field] = context.get("_field")
        if field and field.is_seq():
            # Treat the 'obj' as a sequence/iterable
            if not isinstance(obj, Iterable):
                raise TypeError(f"Expected iterable sequence, got {type(obj)}")

            data = list(obj)
            this_context._length = len(data)
            this_context._field = field
            for i, elem in enumerate(data):
                # The path will contain an additional hint on what element is processed
                # at the moment.
                this_context._index = i
                this_context._path = ".".join([base_path, str(i)])
                this_context._obj = elem
                self.pack_one(elem, stream, this_context)
        else:
            self.pack_one(obj, stream, this_context)
