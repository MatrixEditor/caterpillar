"""
Custom script to generate the public Caterpillar API.
=====================================================


"""

import sys
import os

from caterpillar_api import cp_type_api, cp_func_api, cp_api_functions, cp_types


# Base class for all API objects (functions or types)
class APIObj:
    def __init__(
        self, name: str = None, index: int = 0, api_name: str = None, type_: str = None
    ) -> None:
        self.name = name
        self.index = index
        self.api_name = api_name
        self.type = type_

    def cp_api_table(self) -> str:
        if not self.name:
            return "NULL"
        return f"(void *) &{self.name}"

    def cp_internal_def(self) -> str:
        # must be overridden in subclasses
        return ""

    def cp_external_def(self) -> str:
        return ""


class APIType(APIObj):
    def __init__(self, name: str, index: int, api_name: str, type_: str = None) -> None:
        super().__init__(name, index, api_name, type_ or "PyTypeObject")

    def cp_internal_def(self) -> str:
        # REVISIT: what about struct definitions?
        return f"PyAPI_DATA({self.type}) {self.name};"

    def cp_external_def(self):
        """Return the external definition for this API object

        Example: Consider the simple C type `CpAtom_Type`. Its external definition
        will be `#define CpAtom_Type (*(PyTypeObject *)Cp_API[0])` in case `CpAtom`
        is assigned to index zero.

        :return: C source code string
        :rtype: str
        """
        return f"#define {self.name} (*({self.type} *){self.api_name}[{self.index}])"


class APIFunc(APIObj):
    def __init__(
        self, name: str, index: int, api_name: str, rtype: str, args: list[str]
    ) -> None:
        self.rtype = rtype
        self.args = args
        type_ = "(%s (*)(%s))" % (rtype, ", ".join(args))
        super().__init__(name, index, api_name, type_)

    def cp_internal_def(self) -> str:
        return f"PyAPI_FUNC({self.rtype}) {self.name}({', '.join(self.args)});"

    def cp_external_def(self) -> str:
        return f"#define {self.name} (*({self.type}){self.api_name}[{self.index}])"


def genapi(api_h: str, api_c: str) -> None:
    api_h_out = api_h.replace(".in", "")
    api_c_out = api_c.replace(".in", "")

    func_api = cp_api_functions()
    max_func_index = max(cp_func_api.values())
    max_type_index = max(map(lambda x: x[0], cp_type_api.values()))

    api_objects = [None] * (max(max_func_index, max_type_index) + 1)
    for name, args in cp_type_api.items():
        if name == "__reserved__":
            continue
        index = args[0]
        if api_objects[index] is not None:
            raise ValueError(f"Duplicate API object: {name} at index {index}")

        type_ = None if len(args) == 1 else args[1]
        api_objects[index] = APIType(name, index, "Cp_API", type_)

    for name, index in cp_func_api.items():
        if api_objects[index] is not None:
            raise ValueError(f"Duplicate API object: {name} at index {index}")

        rtype, args = func_api[name]
        api_objects[index] = APIFunc(name, index, "Cp_API", rtype, args)

    array_def = []
    external_def = []
    internal_def = []
    for obj in api_objects:
        if not obj:
            array_def.append("NULL")
        else:
            array_def.append(obj.cp_api_table())
            external_def.append(obj.cp_external_def())
            internal_def.append(obj.cp_internal_def())

    typedefs = []
    for struct_name, type_name in cp_types.items():
        typedefs.append(f"struct {struct_name};")
        typedefs.append(f"typedef struct {struct_name} {type_name};")

    with open(api_h, "r", encoding="utf-8") as f:
        api_h_source = f.read()

    with open(api_h_out, "w", encoding="utf-8") as f:
        f.write(
            api_h_source
            % ("\n".join(typedefs), "\n".join(internal_def), "\n".join(external_def))
        )

    with open(api_c, "r", encoding="utf-8") as f:
        api_c_source = f.read()

    with open(api_c_out, "w", encoding="utf-8") as f:
        f.write(api_c_source % (",\n    ".join(array_def),))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <api.h> <api.c>")
        sys.exit(1)

    api_h = sys.argv[1]
    api_c = sys.argv[2]

    genapi(api_h, api_c)
