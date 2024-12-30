# type: ignore
from caterpillar.py import (
    struct,
    set_struct_flags,
    S_REPLACE_TYPES,
    uint8,
    uint16,
    TemplateTypeVar,
    template,
    derive,
    pack,
    this,
)

try:
    from rich import print
except ImportError:
    pass

set_struct_flags(S_REPLACE_TYPES)


@struct
class BaseFormat:
    """Default class documentation"""

    #: inline comment
    f1: uint8


A = TemplateTypeVar("A")
B = TemplateTypeVar("B")


@template(A, B)
class FormatTemplate(BaseFormat):
    """Template class doc-comment"""

    f2: A[this.f1]
    """Template field doc-comment"""

    #: inline template field comment
    f3: B


#: anonymous generated partial template
Format8 = derive(FormatTemplate, uint8, partial=True)


@struct
class Format(derive(Format8, B=uint8)):
    #: inline comment
    f4: uint8


#: inline data comment
Format16 = derive(FormatTemplate, uint16, uint16, name=...)

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
