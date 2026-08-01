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
from typing import Annotated as f

from . import options as opt
from .byteorder import (
    AARCH64,
    AMD,
    AMD64,
    ARM,
    ARM64,
    RISC_V,
    RISC_V64,
    BigEndian,
    Dynamic,
    Inherit,
    LittleEndian,
    PowerPC,
    PowerPC64,
    x86,
    x86_64,
)
from .context import ContextLength as lenof
from .context import ContextPath, ctx, parent, this
from .context import ctx as C
from .context import parent as P
from .context import root as G
from .fields import Field as F
from .model import Sequence as Seq
from .model import (
    bitfield,
    pack,
    pack_file,
    pack_into,
    sizeof,
    struct,
    union,
    unpack,
    unpack_file,
)
from .registry import to_struct
from .shared import getstruct, hasstruct, typeof

__all__ = [
    "AARCH64",
    "AMD",
    "AMD64",
    "ARM",
    "ARM64",
    "RISC_V",
    "RISC_V64",
    "BigEndian",
    "C",
    "ContextPath",
    "Dynamic",
    "F",
    "G",
    "Inherit",
    "LittleEndian",
    "P",
    "PowerPC",
    "PowerPC64",
    "Seq",
    "bitfield",
    "ctx",
    "f",
    "getstruct",
    "hasstruct",
    "lenof",
    "opt",
    "pack",
    "pack_file",
    "pack_into",
    "parent",
    "sizeof",
    "struct",
    "this",
    "to_struct",
    "typeof",
    "union",
    "unpack",
    "unpack_file",
    "x86",
    "x86_64",
]
