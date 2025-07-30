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
import pathlib

CAPI_PATH = pathlib.Path(__file__).parent.parent / "capi.dat"
if not CAPI_PATH.exists():
    raise FileNotFoundError(f"File not found: {CAPI_PATH}")

# Reserved for future use
RESERVED_STR = "__reserved__"

CP_TYPES: dict[str, str] = {}
CP_TYPE_API: dict[str, tuple[int, str]] = {}
CP_SRC: list[tuple[str, bool]] = []
CP_FUNC_API: dict[str, int] = {}

global_index = 0

for line in CAPI_PATH.read_text("utf-8").splitlines():
    line = line.strip()
    if line.startswith("#") or not line:
        continue

    def_type, *parts = line.split(":")
    match def_type:
        case "obj":
            # obj:INDEX:NAME:TYPE
            #   Defines a C API object.
            index, name, type_ = parts
            if index != "-":
                index = global_index
                global_index += 1
            CP_TYPE_API[name] = (int(index), type_ if type_ != "-" else "PyTypeObject")

        case "type":
            # type:INDEX:STRUCT_NAME:TYPEDEF_NAME:CAPI_TYPE
            #   Defines a C API type for a C structure. The index is optional and
            #   the CAPI_TYPE will be inferred as PyTypeObject if none set
            index, struct_name, typedef_name, c_api_type = parts

            CP_TYPES[struct_name] = typedef_name
            if index != "-":
                index = global_index
                global_index += 1
                if typedef_name.endswith("Object"):
                    typedef_name = typedef_name[:-6] + "_Type"
                CP_TYPE_API[typedef_name] = (
                    int(index),
                    c_api_type if c_api_type != "-" else "PyTypeObject",
                )

        case "src":
            # src:FILE:IGNORE
            #   Defines the source file (relative to this file) that contains the
            #   function definitions.
            name, *ignored = parts
            if not ignored:
                ignored = False
            CP_SRC.append((name, ignored))

        case "func":
            # func:INDEX:NAME:RETURN_TYPE:REFCOUNT
            #   Defines a C API function. The function must be present within the
            #   source set of this file.
            index, name, *_ = parts
            if index != "-":
                index = global_index
                global_index += 1
                CP_FUNC_API[name] = int(index)

        case _:
            pass


def cp_api_functions() -> dict[str, tuple[str, list[str]]]:
    base_path = os.path.dirname(__file__)

    func_api = {}
    # REVISIT: dirty parsing algorithm
    for f, _ in CP_SRC:
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
