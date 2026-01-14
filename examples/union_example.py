# type: ignore
from caterpillar.py import uint16, uint32, boolean, union
from caterpillar.shortcuts import f

try:
    from rich import print
except ImportError:
    pass


@union
class Format:
    foo: f[int, uint16]
    bar: f[int, uint32]
    baz: f[bool, boolean]


# we don't need any arguments here, even if it is marked by
# the type checker
obj = Format()
print(obj)

obj.bar = 0xFF00FF00
print(obj)
