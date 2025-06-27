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
try:
    from rich import print
except ImportError:
    pass

# --------------------------- Basic Information ---------------------------
# "Apple’s Core Audio Format (CAF) is a file format for storing and
# transporting digital audio data. It simplifies the management and
# manipulation of many types of audio data without the file-size
# limitations of other audio file formats."
# > https://developer.apple.com/library/archive/documentation/MusicAudio/Reference/CAFSpec/CAF_intro/CAF_intro.html
# -------------------------------------------------------------------------
import enum

from caterpillar.shortcuts import BigEndian, this, parent, opt
from caterpillar.model import struct, unpack_file, pack_file
from caterpillar.fields import *


opt.set_struct_flags(opt.S_SLOTS)
try:
    from numpy import array

    opt.O_ARRAY_FACTORY.value = array
except ImportError:
    pass


@struct(order=BigEndian)
class CAFHeader:
    # These fields follow standard the definition without a direct
    # default value
    file_type: b"caff"
    file_version: uint16
    # according to Apple, this field must be 0 for CAF c1 files and is reserved
    # for future usage
    file_flags: uint16


@struct(order=BigEndian)
class CAFChunkHeader:
    # As we don't know all possible chunk types, it is recommended to
    # use the Bytes struct here instead of an enum class.
    chunk_type: Bytes(4)
    chunk_size: uint64


# Enum classes are defined as simple as this. Note that the specified enum value
# should be returned by the parsing struct.
class AudioFormatFlags(enum.IntEnum):
    CAFLinearPCMFormatFlagIsFloat = 1
    CAFLinearPCMFormatFlagIsLittleEndian = 0


@struct(order=BigEndian)
class CAFAudioFormat:
    sample_rate: float64
    # The explicit encoding here is for illustration purposes. The default
    # one is actually utf-8.
    format_id: String(4, encoding="utf-8")
    format_flags: Enum(AudioFormatFlags, uint32)
    # The next fields are all simple integer fields
    bytes_per_packet: uint32
    frames_per_packet: uint32
    channels_per_frame: uint32
    bits_per_channel: uint32


@struct(order=BigEndian)
class CAFData:
    edit_count: uint32
    # The parent object can be referenced with a simple shortcut that accesses
    # the direct parent object context.
    data: Memory(parent.chunk_header.chunk_size - 4)


@struct(order=BigEndian)
class CAFInformation:
    # Here we use the _GreedyType to indicate that we don't known the size of
    # the string to parse. The struct will parse until it reads the termination
    # character '\x00'
    key: CString(...)
    value: CString(...)


@struct(order=BigEndian)
class CAFStringsChunk:
    # A simple prefixed field where we use a reference to an already parsed value
    # as the length.
    # num_entries: uint32
    strings: CAFInformation[uint32::]


@struct(order=BigEndian)
class CAFPacketTable:
    # note all signed integer fields here
    num_packets: int64
    num_valid_frames: int64
    priming_frames: int32
    remainder_frames: int32
    # The VarInt configuration doesn't have to be changed, as this file format uses
    # the default implementation.
    table_data: vint[this.num_packets]


@struct(order=BigEndian)
class CAFChannelDesc:
    channel_label: uint32
    channel_flags: uint32
    # fixed size arrays are also possible
    coordinates: float32[3]


@struct(order=BigEndian)
class CAFChannelLayout:
    channel_layout_tag: uint32
    channel_bitmap: uint32
    # REVISIT: the field 'num_descriptions' is obsolete here. There should be a
    # possibility to incorporate the field automatically into arrays.
    num_descriptions: uint32
    descriptions: CAFChannelDesc[this.num_descriptions]


@struct(order=BigEndian)
class CAFChunk:
    chunk_header: CAFChunkHeader
    # this is another simple switch-case structure, but this time we define a
    # default option. NOTE: not all chunk types are implemented
    data: Field(this.chunk_header.chunk_type) >> {
        b"desc": CAFAudioFormat,
        b"info": CAFStringsChunk,
        b"pakt": CAFPacketTable,
        b"data": CAFData,
        # In order to save memory space, we can define a simple padding that inserts
        # the missing data automatically
        b"free": padding[this.chunk_header.chunk_size],
        # NOTE: we use the special struct 'Memory' here as it makes the output more
        # clear (bytes would consume unnecessary decoding time)
        DEFAULT_OPTION: Memory(this.chunk_header.chunk_size),
    }


@struct(order=BigEndian)
class CAF:
    # interestingly, this file format does not declare how many chunks are
    # stored in one file, so we have to use greedy parsing here.
    header: CAFHeader
    chunks: CAFChunk[...]


if __name__ == "__main__":
    import sys

    obj = unpack_file(CAF, sys.argv[1])
    print(obj)
    pack_file(obj, sys.argv[2])
