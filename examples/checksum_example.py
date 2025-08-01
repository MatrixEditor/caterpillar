from rich import print
from cryptography.hazmat.primitives import hashes

from caterpillar.py import struct, Bytes, pack, unpack, this
from caterpillar.fields.digest import HMAC


@struct
class Format:
    key: b"MAGIC"

    with HMAC(this.key, hashes.SHA256(), "hmac", verify=True):
        user_data: Bytes(11)

    # attribute 'hmac' is added by HMAC


print(Format(user_data=b"hello world"))
print(Format.__struct__.fields)
data = pack(Format(user_data=b"hello world"))
print(data)

print("Unpacking invalid data:")
print(unpack(Format, data[:-1] + b"\x00"))
