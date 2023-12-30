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
import enum
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher

try:
    from rich import print
except ImportError:
    pass
# ---------------------------------------------------------------------
# Key information for the structs were taken from here:
#   - https://home.vollink.com/gary/playlister/ituneslib.html
#   - https://gitlab.home.vollink.com/external/musicdb-poc/
# ---------------------------------------------------------------------

from caterpillar.model import struct
from caterpillar.shortcuts import *
from caterpillar.fields import *

opt.set_struct_flags(opt.S_DISCARD_UNNAMED)

# The key used for decryption
KEY = b"BHUILuilfghuila3"


# Unfortunately, we have to implement the decryption process on
# our own. But let it be an example of how to extend this library.
@singleton
class EncryptedBlob(Transformer):
    # The base struct will be a memory instance
    def __init__(self) -> None:
        super().__init__(Memory(...))
        # The cipher doesn't have to be created every time, we want
        # to de/encrypt some data
        self.cipher = Cipher(algorithms.AES(KEY), modes.ECB())

    # PACKING:
    def encode(self, obj: bytes, context) -> bytes:
        # we just have to encrypt the content before it gets written
        # to the stream.
        encryptor = self.cipher.encryptor()

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
        decryptor = self.cipher.decryptor()

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
class MHDataFile(MHChunk):
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


# This enumeration should be subject to future expansion
class MHSubtype(enum.IntEnum):
    MUSIC_FOLDER = 0x04
    DATA_FILE = 0x10


# NOTE: all structs in the encrypted part of the database are using little endian
# encoding
@struct(order=LittleEndian)
class MHDataSet(MHChunk):
    # We can't just create an enum type here as we don't know all
    # chunk types.
    subtype: uint32
    # all following data must be zeros
    _: padding[this.header_len - 16]
    # The second switch structure, which will be used to implement
    # all subtypes.
    data: F(this.subtype) >> {
        # We can simply use the enum values here as it is an IntEnum
        # and supports comparison with integer objects.
        MHSubtype.MUSIC_FOLDER: String(this.total_len - this.header_len),
        MHSubtype.DATA_FILE: MHDataFile,
        DEFAULT_OPTION: Memory(this.total_len - this.header_len),
    }


@struct(order=BigEndian)
class ITDB:
    # Actually, the magic must be represented in reverse order, so
    #   hdfm => mhfd, which could be translated to MHFileData
    magic: b"hdfm"
    header_len: uint32
    total_len: uint32
    header: Memory(this.header_len - 12)
    # Chain + greedy parsing
    chunks: ITDBEncrypted & MHDataSet[...]


# TODO: implement other chunks
if __name__ == "__main__":
    import sys

    obj = unpack_file(ITDB, sys.argv[1])
    print(obj)
    if len(sys.argv) >= 3:
        pack_file(obj, sys.argv[2])
