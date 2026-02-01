import typing

from cryptography.hazmat.primitives import hashes

from caterpillar.py import Struct, getstruct, struct, Bytes, pack, unpack, this
from caterpillar.fields.digest import HMAC
from caterpillar.shortcuts import f


@struct(kw_only=True)
class Format:
    key: f[bytes, b"MAGIC"] = b"MAGIC"

    with HMAC(this.key, hashes.SHA256(), "hmac", verify=True):
        user_data: f[bytes, Bytes(11)]

    # attribute 'hmac' is added by HMAC, but not visible to the type checker
    if typing.TYPE_CHECKING:
        hmac: bytes = b""


print(Format(user_data=b"hello world"))
s = getstruct(Format)
assert isinstance(s, Struct)
print(s.fields)
data = pack(Format(user_data=b"hello world"))
print(data)

print("Unpacking invalid data:")
print(unpack(Format, data[:-1] + b"\x00"))
