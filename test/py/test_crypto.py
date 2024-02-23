# file: test_crypto
# The tests performed here are not only related to encryption, but also show
# how to apply logic-related structs to the stream.
from caterpillar.fields.crypto import Encrypted, Xor
from caterpillar.fields import uint8, Prefixed
from caterpillar.shortcuts import struct, this

from _utils import _test_pack, _test_unpack

# NOTE: the same tests can be written for 'Or' and 'And'. We won't write them
# here as it would produce duplicate code.


###############################################################################
# simple xor
###############################################################################
@struct
class Format_SimpleXor:
    data: Xor(0xEE)


def test_simple_xor():
    obj = Format_SimpleXor(b"Hello World")
    data = b"\xa6\x8b\x82\x82\x81\xce\xb9\x81\x9c\x82\x8a"
    _test_pack(obj, data)
    _test_unpack(Format_SimpleXor, data, obj)


###############################################################################
# chained Xor
###############################################################################
@struct
class Format_ChainedXor_Payload:
    name: Prefixed(uint8, encoding="utf-8")
    magic: b"END"


@struct
class Format_ChainedXor:
    # to keep this test simple, we won't use a length field here
    key: uint8
    payload: Xor(this.key) & Format_ChainedXor_Payload


def test_chained_xor():
    obj = Format_ChainedXor(0x0F, Format_ChainedXor_Payload("FooBar"))
    expected = b"\x0f\tI``Mn}JAK"
    _test_pack(obj, expected)
    _test_unpack(Format_ChainedXor, expected, obj)


###############################################################################
# simple AES encryption
###############################################################################
from cryptography.hazmat.primitives.ciphers import modes, algorithms
from cryptography.hazmat.primitives.padding import PKCS7
from caterpillar.fields.crypto import KwArgs

SimpleAES_KEY = b"1234567890123456"
SimpleAES_IV = bytes(16)

@struct
class Format_SimpleAES:
    data: Encrypted(
        ...,  # length
        algorithms.AES,  # algorithm
        modes.CBC,  # mode
        None,  # padding
        KwArgs(key=SimpleAES_KEY),  # algorithm args
        (SimpleAES_IV,)  # mode args
    )

def test_simple_aes():
    obj = Format_SimpleAES(data=b'Secret Message: Hello World!1234')
    data = b'jf\xce3\x10\x83_\xc8\x0f\xec\x7f>\xbb\x81\x92\xe5I\xeaeS\x17bqA\xb7YO\x19q\xc9\xf1w'
    _test_pack(obj, data)
    _test_unpack(Format_SimpleAES, data, obj)
