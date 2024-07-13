"""
Here we define all public functions and types to export into
our global struct. Each API dictionary contains the export
name and its target index. Therefore, one might break the whole
import system if an index is changed.

Make sure to check all standard indices before adding a new
function.
"""

import os

# Reserved for future use
__reserved__ = "__reserved__"

cp_types = {
    # struct and typedefs
    "_modulestate": "_modulestate",
    "_endianobj": "CpEndianObject",
    "_archobj": "CpArchObject",
    "_atomobj": "CpAtomObject",
    "_catomobj": "CpCAtomObject",
    "_contextobj": "CpContextObject",
    "_unaryexpr": "CpUnaryExprObject",
    "_binaryexpr": "CpBinaryExprObject",
    "_contextpath": "CpContextPathObject",
    "_fieldobj": "CpFieldObject",
    "_fieldatomobj": "CpFieldAtomObject",
    "_fieldcatomobj": "CpFieldCAtomObject",
    "_option": "CpOptionObject",
    "_stateobj": "CpStateObject",
    "_layerobj": "CpLayerObject",
    # REVISIT: maybe rename to _structfieldinfo
    "CpStructFieldInfo": "CpStructFieldInfoObject",
    "_structobj": "CpStructObject",
    "_floatatomobj": "CpFloatAtomObject",
    "_intatomobj": "CpIntAtomObject",
    "_boolatomobj": "CpBoolAtomObject",
    "_charatomobj": "CpCharAtomObject",
    "_paddingatomobj": "CpPaddingAtomObject",
    "_stringatomobj": "CpStringAtomObject",
}

cp_type_api = {
    "CpModule": (0, "PyModuleDef"),
    "CpCAtom_Type": (1,),
    "CpArch_Type": (2,),
    "CpEndian_Type": (3,),
    "CpContext_Type": (4,),
    "CpUnaryExpr_Type": (5,),
    "CpBinaryExpr_Type": (6,),
    "CpContextPath_Type": (7,),
    "CpField_Type": (8,),
    "CpFieldAtom_Type": (9,),
    "CpFieldCAtom_Type": (10,),
    "CpInvalidDefault_Type": (11,),
    "CpDefaultOption_Type": (12,),
    "_CpInvalidDefault_Object": (13, "PyObject"),
    "_CpDefaultOption_Object": (14, "PyObject"),
    "CpAtom_Type": (15,),
    "CpOption_Type": (16,),
    "CpState_Type": (17,),
    "CpLayer_Type": (18,),
    "CpStructFieldInfo_Type": (19,),
    "CpStruct_Type": (20,),
    "CpFloatAtom_Type": (21,),
    "CpIntAtom_Type": (22,),
    "CpBoolAtom_Type": (23,),
    "CpCharAtom_Type": (24,),
    "CpPaddingAtom_Type": (25,),
    "CpStringAtom_Type": (26,),
}

cp_func_api = {
    # <name>: <index> <<-->> <index>: (name, rtype, [args])
    "CpEndian_IsLittleEndian": 30,
}

API_SRC = [
    "field.c",
    "context.c",
    "arch.c",
    "atomobj.c",
    "option.c",
    "struct.c",
    "state.c",
    "parsing_pack.c",
    "parsing_unpack.c",
    "parsing_typeof.c",
    "parsing_sizeof.c",
    "atomimpl/boolatomobj.c",
    "atomimpl/floatatomobj.c",
    "atomimpl/charatomobj.c",
    "atomimpl/intatomobj.c",
    "atomimpl/padatomobj.c",
    "atomimpl/stringatomobj.c",
]


def cp_api_functions() -> dict[str, tuple]:
    base_path = os.path.dirname(__file__)

    func_api = {}
    # REVISIT: dirty parsing algorithm
    for f in API_SRC:
        with open(os.path.join(base_path, "..", f), "r", encoding="utf-8") as c_src:
            while True:
                line = c_src.readline()
                if not line:
                    break

                line = line.strip()
                if line.startswith("/*CpAPI"):
                    # API function tag
                    if not line.endswith("*/"):
                        while not line.endswith("*/"):
                            line = c_src.readline()
                            if not line:
                                break
                    else:
                        line = c_src.readline().strip()

                    rtype = line.strip()
                    name, signature = c_src.readline().strip().split("(", 1)
                    args = signature[:-1].split(", ")
                    func_api[name] = (rtype, args)

    return func_api
