import typing
import pytest
import sys

from caterpillar.exception import ValidationError
from caterpillar.py import Bytes, Struct, unpack, pack, struct
from caterpillar.fields.digest import (
    DigestField,
    Md5,
    Md5_Field,
    Sha2_256,
    Md5_Algo,
    Sha2_256_Algo,
    Sha2_256_Field,
)
from caterpillar.shared import ATTR_ACTION_PACK, getstruct
from caterpillar.shortcuts import f

UserDataT = f[bytes, Bytes(10)]

if (sys.version_info.major, sys.version_info.minor) < (3, 14):

    @struct
    class FormatMd5:
        with Md5("hash", verify=False):
            user_data: UserDataT

    @struct
    class FormatSha2_256:
        with Sha2_256("hash", verify=True):
            user_data: UserDataT

else:

    @struct
    class FormatMd5:
        # actions won't be visible afterwards
        if not typing.TYPE_CHECKING:
            _hash_begin: DigestField.begin("hash", Md5_Algo)

        user_data: UserDataT
        hash: f[bytes, Md5_Field("hash", verify=False)] = b""

    @struct
    class FormatSha2_256:
        if not typing.TYPE_CHECKING:
            _hash_begin: DigestField.begin("hash", Sha2_256_Algo)

        user_data: UserDataT
        hash: f[bytes, Sha2_256_Field("hash", verify=True)] = b""


def test_digest_init():
    # must be an action
    # actions are stored in tuples
    s = getstruct(FormatMd5)
    assert isinstance(s, Struct)
    assert hasattr(s.fields[0].field, ATTR_ACTION_PACK)

    _ = FormatMd5(user_data=b"1234567890")
    # assert obj.hash.__class__ is _DigestValue


def test_digest_md5():
    obj = FormatMd5(user_data=b"1234567890")
    valid = b"1234567890\xe8\x07\xf1\xfc\xf8-\x13/\x9b\xb0\x18\xcag8\xa1\x9f"

    assert pack(obj) == valid
    # as verify is set to false, we can parse arbitrary hashes
    assert unpack(FormatMd5, valid[:-1] + b"0")


def test_digest_verify():
    invalid = b"1234567890" + b"\x00" * 32
    with pytest.raises(ValidationError):
        _ = unpack(FormatSha2_256, invalid)
