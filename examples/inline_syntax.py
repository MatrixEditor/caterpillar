from io import BytesIO
from caterpillar.py import uint8

# data can be unpacked INLINE using a special operator
data = b"\x00\x00\x01\xff"

# If using on a static bytes object, the struct will always begin at offset zero
value = uint8 << data
other_value = uint8 << data
assert value == other_value

# When using a stream, the current stream position will be modified
stream = BytesIO(data)
_ = stream.seek(2)
value = uint8 << stream
other_value = uint8 << stream
assert value != other_value

# Instead of using the special operator, all default struct classes provide
# wrapper functions for packing and unpacking:
value = uint8.from_bytes(data)
assert uint8.to_bytes(value) == data[:1]