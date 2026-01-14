# type: ignore
from caterpillar.py import union
from caterpillar.types import boolean_t, uint16_t, uint32_t


@union
class Format:
    foo: uint16_t
    bar: uint32_t
    baz: boolean_t


# we don't need any arguments here, even if it is marked by
# the type checker
obj = Format()  # pyright: ignore[reportCallIssue]
print(obj)

obj.bar = 0xFF00FF00
print(obj)
