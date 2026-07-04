# dtype: ignore
from typing import TypeVar, Generic

from caterpillar.py import (
    f,
    field_of,
    struct,
    set_struct_flags,
    S_REPLACE_TYPES,
    uint8,
    template,
    derive,
    pack,
    this,
)
from caterpillar.types import uint16_t, uint8_t

set_struct_flags(S_REPLACE_TYPES)


@struct
class BaseFormat:
    """Default class documentation"""

    #: inline comment
    f1: uint8_t


A = TypeVar("A")
B = TypeVar("B")


@template
class FormatTemplate(Generic[A, B], BaseFormat):
    """Template class doc-comment"""

    # Use the field_of method to apply special operators on a type var
    # --> these will be applied to the field later on

    f2: f[list[A], field_of(A)[this.f1]]
    """Template field doc-comment"""

    #: inline template field comment
    f3: B


#: anonymous generated partial template
# Format8 = derive(FormatTemplate, uint8, partial=True)
# or direct approach
Format8 = FormatTemplate[uint8_t, B]


@struct
class Format(Format8[uint8_t]):
    #: inline comment
    f4: uint8_t


# Direct specialization via [] is also possible
Format16 = FormatTemplate[uint16_t, uint16_t]

if __name__ == "__main__":
    # Format(f1: int, f2: List, f3: int, f4: int)
    print(Format.__doc__)
    # Format16(f1: int, f2: List, f3: int)
    print(Format16.__doc__)

    obj = Format(2, [3, 4], 0xEE, 0xFF)
    # b'\x02\x03\x04\xee\xff'
    print(pack(obj))

    obj = Format16(2, [3, 4], 0xFF)
    # b'\x02\x03\x00\x04\x00\xff\x00'
    print(pack(obj))
