from caterpillar.py import pack, struct_factory, struct, unpack
from caterpillar.types import uint16_t, uint32_t


# Problem: type checkers will complain about missing [...] operation
# support; calling unpack or pack requires import in all files;
#
# Solution: inherit wrapper methods from a 'mixin' class that
# defines:
#   - cls.from_bytes(data) for parsing data
#   - cls.from_file(path) for parsing data from files
#   - obj.to_bytes() to pack data
#   . __class_getitem__ for [] operator
@struct
class Format(struct_factory.mixin):
    a: uint16_t
    b: uint32_t


# creation is same
obj = Format(1, 2)
# packing and unpacking can be done using wrapper methods
data = obj.to_bytes()
assert Format.from_bytes(data) == obj

# the mixin also defines the [] operation, so static type checkers
# won't complain here:
values = [Format(i, i) for i in range(2)]
buffer = pack(values, Format[...])
assert unpack(Format[...], buffer) == values