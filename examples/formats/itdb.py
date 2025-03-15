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
import enum
import plistlib
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher

try:
    from rich import print
except ImportError:
    pass
# ---------------------------------------------------------------------
# Key information for the structs were taken from here:
#   - https://home.vollink.com/gary/playlister/ituneslib.html
#   - https://gitlab.home.vollink.com/external/musicdb-poc/
#   - Internal TypeLib of iTunes (accessible from within the application
#     binary)
# ---------------------------------------------------------------------

from caterpillar.model import struct
from caterpillar.shortcuts import *
from caterpillar.fields import *

opt.set_struct_flags(opt.S_DISCARD_UNNAMED)

KEY = None


# Unfortunately, we have to implement the decryption process on
# our own. But let it be an example of how to extend this library.
@singleton
class EncryptedBlob(Transformer):
    # The base struct will be a memory instance
    def __init__(self) -> None:
        super().__init__(Memory(...))

    # PACKING:
    def encode(self, obj: bytes, context) -> bytes:
        # we just have to encrypt the content before it gets written
        # to the stream.
        cipher = Cipher(algorithms.AES(KEY), modes.ECB())
        encryptor = cipher.encryptor()

        # Encryption is a little bit different. The last 16 bytes are
        # static and won't be encrypted
        length = len(obj)
        pos = length - (length % 16)
        encrypted = encryptor.update(obj[:pos]) + encryptor.finalize()
        # usually, an instance of Encrypted(...) would be used here
        return encrypted + obj[pos:]

    # UNPACKING
    def decode(self, parsed: memoryview, context) -> bytes:
        # the same again: note that the parsed object is encrypted
        # and must be decompressed afterwards
        cipher = Cipher(algorithms.AES(KEY), modes.ECB())
        decryptor = cipher.decryptor()

        # REVISIT: Trailer struct that servers as a copy-only padding
        length = len(parsed)
        pos = length - (length % 16)
        decrypted = decryptor.update(parsed[:pos]) + decryptor.finalize()
        return decrypted + parsed[pos:]


# We create a chain to first, decrypt the data, then decompress it
# and later on, we can use this chain to parse chunks from the
# decompressed data.
ITDBEncrypted = EncryptedBlob & ZLibCompressed(..., comp_kwargs={"level": 1})


# This will be the base class for all data chunks
@struct(order=LittleEndian)
class MHChunk:
    type: Bytes(4)
    header_len: uint32
    total_len: uint32


# First of all, define the global header
@struct(order=LittleEndian)
class MHFileData(MHChunk):  # mdfh
    unknown: uint32
    # Prefixed wouldn't help here, as the string is fixed. We could add
    # a padding to the prefixed class.
    version: Prefixed(uint8, encoding="utf-8")
    _: padding[31 - lenof(this.version)]
    chunk_count: uint32
    # This id is important to iTunes
    library_id: uint64
    # the rest of the data will be copied
    pad: Memory(this.header_len - 60)


class ObjectType(enum.IntEnum):
    __struct__ = uint32

    kTrackName = 0x02
    kTrackAlbumName = 0x03
    kTrackArtist = 0x04
    kTrackGenre = 0x05
    kTrackKind = 0x06
    kTrackEQ = 0x07
    kTrackComments = 0x08
    kTrackCategory = 0x09
    kTrackFileURL = 0x0B
    kTrackComponist = 0x0C
    kTrackLocation = 0x0D
    kTrackGroup = 0x0E

    kTrackShortDescription = 0x12
    kTrackFullDescription = 0x16
    kTVShowName = 0x18
    kTVEpisode = 0x19
    kTrackAlbumArtist = 0x1B

    kSmartPlaylistTitle = 0x64
    kSmartCriteria = 0x65
    kSmartInfo = 0x66
    kSmartPList = 0x6D

    kAlbumName = 0x12C
    kAlbumArtist = 0x12D
    kAlbumArtistSort = 0x12E

    kVideoDirector = 0x190
    kVideoDirectorSort = 0x191

    kPlaySmartFilter = 0x2BC
    kPLaySmartName = 0x2BE
    kPlaySmartInfo = 0x2BF

    kPlist = 0x320


class StringType(enum.IntEnum):
    __struct__ = uint32

    kURI = 0
    kWString = 1
    kEscapedURI = 2
    kUTF8 = 3


@struct(order=LittleEndian)
class MHString:
    type: StringType
    length: uint32
    _: padding[8]
    text: F(this.type) >> {
        # Wide characters can be decoded just like this
        StringType.kWString: String(this.length, encoding="utf-16"),
        DEFAULT_OPTION: String(this.length),
    }


# Using this simple class we can simply transform the bytes into
# a dictionary
class PList(Transformer):
    def __init__(self, length) -> None:
        super().__init__(Bytes(length))

    def encode(self, obj: dict, context) -> bytes:
        return plistlib.dumps(obj)

    def decode(self, parsed, context) -> dict:
        return plistlib.loads(parsed)


# NOTE: this is an example of how to apply your own swtich-case logic
# with a context function
def get_object_struct(value: ObjectType, context):
    if value in list(range(1, 15)):
        return MHString

    if value == ObjectType.kPlist:
        return PList(this.total_len - 24)

    # this will be our default option
    return Memory(this.total_len - 24)


@struct(order=LittleEndian)
class MHObjectHeader(MHChunk):  # mhoh
    # The enum can be used here, because we haven't explicitly enabled
    # *strict* mode. The resulting value will be either an integer or
    # the mapped enum value.
    obj_type: ObjectType
    unknown1: uint32
    unknown2: uint32
    data: F(this.obj_type) >> get_object_struct


class RatingType(enum.IntEnum):
    __struct__ = uint8

    kManual = 1
    kAuto = 0x20


@struct(order=LittleEndian)
class MHAlbumItem(MHChunk):  # miah
    child_count: uint32
    unknown: uint32
    item_id: uint64
    unknown_1: uint32
    album_id: uint64
    rating: uint8
    rated_by: RatingType
    _: padding[46]
    objects: MHObjectHeader[this.child_count]


@struct(order=LittleEndian)
class MHAlbumList(MHChunk):  # mlah
    selected: uint32
    _: padding[this.header_len - 16]
    items: MHAlbumItem[this.total_len]


@struct(order=LittleEndian)
class MHImageItem(MHChunk):  # miih
    child_count: uint32
    image_id: uint32
    song_id: uint64
    _: padding[72]
    # Just use an array here
    objects: MHObjectHeader[this.child_count]


@struct(order=LittleEndian)
class MHImageList(MHChunk):  # mlih
    # the last header data is always filled up with zeros
    _: padding[this.header_len - 12]
    items: MHImageItem[this.total_len]


@struct(order=LittleEndian)
class MHTrackItem(MHChunk):  # mtih
    # strings are set at the end
    string_count: uint32
    track_id: uint32
    track_type: uint8
    file_type: uint32
    compiled: boolean
    _unknown: Memory(6)
    play_date: uint32
    length: uint32
    total_time: uint32
    track_number: uint32
    total_tracks: uint32
    year: uint32
    bitrate: uint32
    sample_rate: uint32
    volume_adjustment: int32
    start_time: uint32
    stop_time: uint32
    play_count: uint32
    _1: padding[24]
    disc_num: uint16
    disc_total: uint16
    _2: padding[20]
    persistent_id: uint64
    _3: padding[620]
    strings: MHObjectHeader[this.string_count]


@struct(order=LittleEndian)
class MHTrackList(MHChunk):
    # same list structure
    _: padding[this.header_len - 12]
    tracks: MHTrackItem[this.total_len]


@struct(order=LittleEndian)
class MHSmartPlaylistItem(MHChunk):  # miph
    object_count: uint32
    _: padding[0x20]
    obejcts: MHObjectHeader[this.object_count]


@struct(order=LittleEndian)
class MHSmartPlaylist(MHChunk):  # mlph
    _: padding[0x20]
    items: MHSmartPlaylistItem[this.total_len]


# This enumeration should be subject to future expansion
class MHSubtype(enum.IntEnum):
    __struct__ = uint32

    kFileData = 0x10
    kImageList = 0x0B
    kAlbumList = 0x09
    kTrackList = 0x01
    kPlaylist = 0x02
    kTrackList2 = 0x0D
    kSmartPlaylist = 0x15
    kPlayFilterInfo = 0x17
    kLocation = 0x04
    kRecentPlaylists = 0x0F


# NOTE: all structs in the encrypted part of the database are using little endian
# encoding
@struct(order=LittleEndian)
class MHSectionData(MHChunk):  # msdh
    # We can just use the enum here.
    subtype: MHSubtype
    # all following data must be zeros
    _: padding[this.header_len - 16]
    # The second switch structure, which will be used to implement
    # all subtypes.
    data: F(this.subtype) >> {
        # We can simply use the enum values here as it is an IntEnum
        # and supports comparison with integer objects.
        MHSubtype.kLocation: String(this.total_len - this.header_len),
        MHSubtype.kFileData: MHFileData,
        MHSubtype.kAlbumList: MHAlbumList,
        MHSubtype.kImageList: MHImageList,
        MHSubtype.kTrackList: MHTrackList,
        MHSubtype.kTrackList2: MHTrackList,
        MHSubtype.kSmartPlaylist: MHSmartPlaylist,
        # just copy the raw data
        DEFAULT_OPTION: Memory(this.total_len - this.header_len),
    }


@struct(order=BigEndian)
class ITDB:
    # Actually, the magic must be represented in reverse order, so
    #   hdfm => mhfd, which could be translated to MHFileData
    magic: b"hdfm"
    header_len: uint32
    total_len: uint32
    # The fields below are the same from MHFileData, but with big-endian
    # encoding
    unknown: uint32
    # Prefixed wouldn't help here, as the string is fixed. We could add
    # a padding to the prefixed class.
    version: Prefixed(uint8, encoding="utf-8")
    _: padding[31 - lenof(this.version)]
    chunk_count: uint32
    # This id is important to iTunes
    library_id: uint64
    # the rest of the data will be copied
    pad: Memory(this.header_len - 60)
    # Chain + greedy parsing
    sections: ITDBEncrypted & MHSectionData[...]


# TODO: implement other chunks
if __name__ == "__main__":
    import sys

    KEY = sys.argv[2].encode()
    obj = unpack_file(ITDB, sys.argv[1])
    print(obj)
    if len(sys.argv) >= 4:
        pack_file(obj, sys.argv[3])
