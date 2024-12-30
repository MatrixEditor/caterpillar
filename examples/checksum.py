from rich import print
from cryptography.hazmat.primitives import hashes

from caterpillar.py import Digest, struct, Algorithm, Bytes, pack, unpack, uint32, this
from caterpillar.fields.digest import *


@struct
class Format:
    key: b"MAGIC"

    # with HMAC(this.key, hashes.SHA256(), "hmac", verify=True):
    with Sha3_224("hash", verify=True):
        user_data: Bytes(11)


    # attribute 'sha256' is added by Checksum

print(Format(user_data=b"hello world"))
print(Format.__struct__.fields)
data = pack(Format(user_data=b"hello world"))
print(data)
print("unpacking..")
print(unpack(Format, data[:-1] + b"\x00"))
