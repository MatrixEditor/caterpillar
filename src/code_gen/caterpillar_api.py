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
__reserved__ = "__reserved__"

cp_types = {} # struct and typedefs
cp_type_api = {}
cp_api_src = []
cp_func_api = {} # <name>: <index> <<-->> <name>: (rtype, [args])

for line in CAPI_PATH.read_text("utf-8").splitlines():
    if line.startswith("#"):
        continue

    line = line.strip()
    if not line:
        continue

    def_type, *parts = line.split(":")
    match def_type:
        case "obj":
            # obj:INDEX:NAME:TYPE
            #   Defines a C API object.
            index, name, type_ = parts
            cp_type_api[name] = (int(index), type_ if type_ != "-" else "PyTypeObject")

        case "type":
            # type:INDEX:STRUCT_NAME:TYPEDEF_NAME:CAPI_TYPE
            #   Defines a C API type for a C structure. The index is optional and
            #   the CAPI_TYPE will be inferred as PyTypeObject if none set
            index, struct_name, typedef_name, c_api_type = parts
            cp_types[struct_name] = typedef_name
            if index != '-':
                if typedef_name.endswith("Object"):
                    typedef_name = typedef_name[:-6] + "_Type"
                cp_type_api[typedef_name] = (int(index), c_api_type if c_api_type != "-" else "PyTypeObject")

        case "src":
            # src:FILE
            #   Defines the source file (relative to this file) that contains the
            #   function definitions.
            cp_api_src.append(parts[0])

        case "func":
            # func:INDEX:NAME:RETURN_TYPE:REFCOUNT
            #   Defines a C API function. The function must be present within the
            #   source set of this file.
            index, name, *_ = parts
            if index != '-':
                cp_func_api[name] = int(index)


def cp_api_functions() -> dict[str, tuple]:
    base_path = os.path.dirname(__file__)

    func_api = {}
    # REVISIT: dirty parsing algorithm
    for f in cp_api_src:
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
