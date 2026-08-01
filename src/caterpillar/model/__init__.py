# Copyright (C) MatrixEditor 2023-2026
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
from ._base import RemoveField, Sequence
from ._bitfield import (DEFAULT_ALIGNMENT, Bitfield, BitfieldDefMixin,
                        BitfieldEntry, BitfieldGroup, BitfieldValueFactory,
                        CharFactory, EndGroup, EnumFactory, NewGroup,
                        SetAlignment, bitfield, bitfield_factory, getbits,
                        issigned)
from ._struct import (Invisible, Struct, StructDefMixin, UnionHook, struct,
                      struct_factory, union)
from ._template import (TemplateFieldRef, TemplateTypeVar, derive, field_of,
                        istemplate, template)
from .provider import pack, pack_file, pack_into, sizeof, unpack, unpack_file

__all__ = [
    "bitfield_factory",
    "bitfield",
    "Bitfield",
    "BitfieldDefMixin",
    "BitfieldEntry",
    "BitfieldGroup",
    "BitfieldValueFactory",
    "CharFactory",
    "DEFAULT_ALIGNMENT",
    "derive",
    "EndGroup",
    "EnumFactory",
    "field_of",
    "getbits",
    "Invisible",
    "issigned",
    "istemplate",
    "NewGroup",
    "pack_file",
    "pack_into",
    "pack",
    "RemoveField",
    "Sequence",
    "SetAlignment",
    "sizeof",
    "struct_factory",
    "struct",
    "Struct",
    "StructDefMixin",
    "template",
    "TemplateFieldRef",
    "TemplateTypeVar",
    "union",
    "UnionHook",
    "unpack_file",
    "unpack",
]
