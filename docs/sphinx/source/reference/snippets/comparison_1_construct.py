from construct import *

d = Struct(
    "count" / Int32ul,
    "items"
    / Array(
        this.count,
        Struct(
            "num1" / Int8ul,
            "num2" / Int24ul,
            "flags"
            / BitStruct(
                "bool1" / Flag,
                "num4" / BitsInteger(3),
                Padding(4),
            ),
            "fixedarray1" / Array(3, Int8ul),
            "name1" / CString("utf8"),
            "name2" / PascalString(Int8ul, "utf8"),
        ),
    ),
)
d_compiled = d.compile()
