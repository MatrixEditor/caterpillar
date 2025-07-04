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
from ._base import Sequence
from ._struct import (
    Struct,
    struct,
    UnionHook,
    union,
    unpack,
    unpack_file,
    pack,
    pack_into,
    pack_file,
    sizeof,
)
from ._bitfield import (
    Bitfield,
    bitfield,
    BitfieldEntry,
    BitfieldGroup,
    BitfieldValueFactory,
    issigned,
    getbits,
    NewGroup,
    EndGroup,
    SetAlignment,
    EnumFactory,
    CharFactory,
    DEFAULT_ALIGNMENT,
)
from ._template import istemplate, template, TemplateTypeVar, derive

__all__ = [
    "Sequence",
    "Struct",
    "struct",
    "UnionHook",
    "union",
    "unpack",
    "unpack_file",
    "pack",
    "pack_into",
    "pack_file",
    "sizeof",
    "Bitfield",
    "bitfield",
    "BitfieldGroup",
    "issigned",
    "getbits",
    "istemplate",
    "template",
    "TemplateTypeVar",
    "derive",
    "NewGroup",
    "EndGroup",
    "SetAlignment",
    "BitfieldEntry",
    "BitfieldValueFactory",
    "EnumFactory",
    "CharFactory",
    "DEFAULT_ALIGNMENT",
]
