# type: ignore
from caterpillar.py import uint16, uint32, boolean, union

try:
    from rich import print
except ImportError:
    pass


@union
class Format:
    foo: uint16
    bar: uint32
    baz: boolean


# we don't need any arguments here
obj = Format()
print(obj)

obj.bar = 0xFF00FF00
print(obj)
