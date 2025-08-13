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
from .byteorder import (
    AARCH64,
    AMD,
    AMD64,
    ARM,
    ARM64,
    BigEndian,
    LittleEndian,
    PowerPC,
    PowerPC64,
    RISC_V,
    RISC_V64,
    x86,
    x86_64,
)
from .context import ContextPath, ctx, parent, this, ContextLength as lenof
from .context import ctx as C, parent as P, root as G
from .model import (
    bitfield,
    pack,
    pack_file,
    pack_into,
    struct,
    union,
    unpack,
    unpack_file,
    sizeof,
    Sequence as Seq,
)
from .shared import typeof, getstruct, hasstruct
from .registry import to_struct
from . import options as opt
from .fields import Field as F

__all__ = [
    "AARCH64",
    "AMD",
    "AMD64",
    "ARM",
    "ARM64",
    "BigEndian",
    "LittleEndian",
    "PowerPC",
    "PowerPC64",
    "RISC_V",
    "RISC_V64",
    "x86",
    "x86_64",
    "bitfield",
    "pack",
    "pack_file",
    "pack_into",
    "struct",
    "union",
    "unpack",
    "unpack_file",
    "sizeof",
    "Seq",
    "typeof",
    "getstruct",
    "hasstruct",
    "ContextPath",
    "ctx",
    "parent",
    "this",
    "lenof",
    "to_struct",
    "F",
    "opt",
    "C",
    "P",
    "G",
]
