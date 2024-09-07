# type: ignore
from caterpillar.py import struct, pack, unpack, this, uint8, int32, Bytes

try:
    from rich import print
except ImportError:
    pass


@struct
class BaseFormat:
    magic: b"BASE"
    length: uint8


# Extending our struct can be achieved through basic inheritance. All fields
# defined in 'BaseFormat' will precede those in this class. You can verify
# the importation of all fields by using help(Format.__init__).
#
# NOTE: A struct class is also capable of inheriting from non-struct classes,
# which will be ignored during processing.
@struct
class Format(BaseFormat):
    foo: int32
    # Referencing fields from the super class is possible
    data: Bytes(this.length)


obj = Format(length=5, foo=-1, data=bytes([i for i in range(5)]))
data = pack(obj)
print(data)

# as Format extends BaseFormat, we can also just unpack a FormatBase
# object.
print(unpack(BaseFormat, data))
print(unpack(Format, data))
