"""
Here we define all public functions and types to export into
our global struct. Each API dictionary contains the export
name and its target index. Therefore, one might break the whole
import system if an index is changed.

Make sure to check all standard indices before adding a new
function.
"""

# !! heavily inspired by numpy !!

import os

# Reserved for future use
__reserved__ = "__reserved__"

cp_types = {
    # struct and typedefs
    "_modulestate":             "_modulestate",
    "_endianobj":               "CpEndianObject",
    "_archobj":                 "CpArchObject",
    "_atomobj":                 "CpAtomObject",
    "_catomobj":                "CpCAtomObject",
    "_contextobj":              "CpContextObject",
    "_unaryexpr":               "CpUnaryExprObject",
    "_binaryexpr":              "CpBinaryExprObject",
    "_contextpath":             "CpContextPathObject",
    "_fieldobj":                "CpFieldObject",
    "_fieldatomobj":            "CpFieldAtomObject",
    "_fieldcatomobj":           "CpFieldCAtomObject",
    "_option":                  "CpOptionObject",
    "_stateobj":                "CpStateObject",
    "_layerobj":                "CpLayerObject",
    # REVISIT: maybe rename to _structfieldinfo
    "CpStructFieldInfo":        "CpStructFieldInfoObject",
    "_structobj":               "CpStructObject",
    "_floatatomobj":            "CpFloatAtomObject",
    "_intatomobj":              "CpIntAtomObject",
    "_boolatomobj":             "CpBoolAtomObject",
    "_charatomobj":             "CpCharAtomObject",
    "_paddingatomobj":          "CpPaddingAtomObject",
    "_stringatomobj":           "CpStringAtomObject",
}

cp_type_api = {
    "CpModule":                     (0, "PyModuleDef"),
    "CpCAtom_Type":                 (1,),
    "CpArch_Type":                  (2,),
    "CpEndian_Type":                (3,),
    "CpContext_Type":               (4,),
    "CpUnaryExpr_Type":             (5,),
    "CpBinaryExpr_Type":            (6,),
    "CpContextPath_Type":           (7,),
    "CpField_Type":                 (8,),
    "CpFieldAtom_Type":             (9,),
    "CpFieldCAtom_Type":            (10,),
    "CpInvalidDefault_Type":        (11,),
    "CpDefaultOption_Type":         (12,),
    "_CpInvalidDefault_Object":     (13, "PyObject"),
    "_CpDefaultOption_Object":      (14, "PyObject"),
    "CpAtom_Type":                  (15,),
    "CpOption_Type":                (16,),
    "CpState_Type":                 (17,),
    "CpLayer_Type":                 (18,),
    "CpStructFieldInfo_Type":       (19,),
    "CpStruct_Type":                (20,),
    "CpFloatAtom_Type":             (21,),
    "CpIntAtom_Type":               (22,),
    "CpBoolAtom_Type":              (23,),
    "CpCharAtom_Type":              (24,),
    "CpPaddingAtom_Type":           (25,),
    "CpStringAtom_Type":            (26,),
}

cp_func_api = {
    # <name>: <index> <<-->> <name>: (rtype, [args])
    "CpEndian_IsLittleEndian": 50,
    # "CpContext_GetAttr": 51,
    # "CpContext_GetAttrString": 52,
    "CpContext_New":                53,
    "CpUnaryExpr_New":              54,
    "CpBinaryExpr_New":             55,
    "CpContextPath_New":            56,
    "CpContextPath_FromString":     57,
    "CpField_New":                  58,
    "CpField_HasCondition":         59,
    "CpField_IsEnabled":            60,
    "CpField_GetOffset":            61,
    "CpField_EvalSwitch":           62,
    "CpField_GetLength":            63,
    "CpTypeOf":                     64,
    "CpTypeOf_Field":               65,
    "CpTypeOf_Common":              66,
    "CpPack":                       67,
    "CpPack_Field":                 68,
    "CpPack_Common":                69,
    "CpPack_Struct":                70,
    "_Cp_Pack":                     71,
    "_CpPack_EvalLength":           72,
    "CpSizeOf":                     73,
    "CpSizeOf_Field":               74,
    "CpSizeOf_Struct":              75,
    "CpSizeOf_Common":              76,
    "_Cp_SizeOf":                   77,
    "CpUnpack":                     78,
    "CpUnpack_Field":               79,
    "CpUnpack_Common":              80,
    "CpUnpack_Struct":              81,
    "_Cp_Unpack":                   82,
    "_CpUnpack_EvalLength":         83,
    "CpUnpack_CAtom":               84,
    "CpPack_CAtom":                 85,
    "CpSizeOf_CAtom":               86,
    "CpTypeOf_CAtom":               87,
    "CpState_New":                  88,
    "CpState_Tell":                 89,
    "CpState_Seek":                 90,
    "CpState_Read":                 91,
    "CpState_ReadFully":            92,
    "CpState_Write":                93,
    "CpState_SetGlobals":           94,
    "CpLayer_New":                  95,
    "CpLayer_Invalidate":           96,
    "CpLayer_SetSequence":          97,
    "CpStructFieldInfo_New" :       98,
    "CpStruct_AddFieldInfo":        99,
    "CpStruct_AddField":           100,
    "CpStruct_New":                101,
    "CpStruct_GetAnnotations":     102,
    "CpStruct_ReplaceType":        103,
    "CpStruct_HasOption":          104,
    "CpStructModel_Check":         105,
    "CpStructModel_GetStruct":     106,

    # atom api
    "CpIntAtom_Pack":              120,
    "CpIntAtom_Unpack":            121,
    "CpFloatAtom_Pack":            122,
    "CpFloatAtom_Unpack":          123,
    "CpBoolAtom_Pack":             124,
    "CpBoolAtom_Unpack":           125,
    "CpCharAtom_Pack":             126,
    "CpCharAtom_Unpack":           127,
    "CpPaddingAtom_Pack":          128,
    "CpPaddingAtom_PackMany":      129,
    "CpPaddingAtom_Unpack":        130,
    "CpPaddingAtom_UnpackMany":    131,
    "CpStringAtom_Pack":           132,
    "CpStringAtom_Unpack":         133,
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
                    if not signature.endswith(")"):
                        while not signature.endswith(")"):
                            signature += c_src.readline().strip()
                    args = signature[:-1].split(", ")
                    func_api[name] = (rtype, args)

    return func_api
