"""
Custom script to generate the public Caterpillar API.
=====================================================
"""

import pathlib
import argparse
import dataclasses
from typing_extensions import override

from caterpillar_api import (
    CP_FUNC_API,
    CP_TYPE_API,
    cp_api_functions,
    CP_SRC,
    CP_TYPES,
)


# Base class for all API objects (functions or types)
@dataclasses.dataclass
class APIObj:
    name: str
    index: int
    api_name: str
    type: str

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
    def __insit__(
        self, name: str, index: int, api_name: str, type_: str | None = None
    ) -> None:
        super().__init__(name, index, api_name, type_ or "PyTypeObject")

    @override
    def cp_internal_def(self) -> str:
        # REVISIT: what about struct definitions?
        if self.type.startswith("Py"):
            return f"extern {self.type} {self.name};"

        extra_def = f"#define {self.name.replace('_Type', '')}_NAME \"{self.type}\""
        return f"extern PyTypeObject {self.name};\n{extra_def}"

    @override
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
    rtype: str
    args: list[str]

    def __init__(
        self, name: str, index: int, api_name: str, rtype: str, args: list[str]
    ) -> None:
        self.rtype = rtype
        self.args = args
        type_ = "(%s (*)(%s))" % (rtype, ", ".join(args))
        super().__init__(name, index, api_name, type_)

    @override
    def cp_internal_def(self) -> str:
        return f"{self.rtype} {self.name}({', '.join(self.args)});"

    @override
    def cp_external_def(self) -> str:
        return f"#define {self.name} (*({self.type}){self.api_name}[{self.index}])"


def genapi(
    api_h: pathlib.Path,
    api_c: pathlib.Path,
    mod_c: pathlib.Path,
    private_h: pathlib.Path,
) -> None:
    api_h_out = pathlib.Path(str(api_h).replace(".in", ""))
    api_c_out = pathlib.Path(str(api_c).replace(".in", ""))
    mod_c_out = pathlib.Path(str(mod_c).replace(".in", ""))
    private_h_out = pathlib.Path(str(private_h).replace(".in", ""))

    func_api = cp_api_functions()
    max_func_index = max(CP_FUNC_API.values())
    max_type_index = max(map(lambda x: x[0], CP_TYPE_API.values()))

    api_objects = [None] * (max(max_func_index, max_type_index) + 1)
    for name, args in CP_TYPE_API.items():
        if name == "__reserved__":
            continue
        index = args[0]
        if api_objects[index] is not None:
            raise ValueError(f"Duplicate API object: {name} at index {index}")

        type_ = None if len(args) == 1 else args[1]
        api_objects[index] = APIType(name, index, "Cp_API", type_)

    for name, index in CP_FUNC_API.items():
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
    for struct_name, type_name in CP_TYPES.items():
        typedefs.append(f"struct {struct_name};")
        typedefs.append(f"typedef struct {struct_name} {type_name};")

    api_h_source = api_h.read_text(encoding="utf-8")
    mod_types = []
    for name, ignored in CP_SRC:
        if not ignored:
            target_name = pathlib.Path(name).stem
            mod_types.append(f"cp_{target_name}")

    with api_h_out.open("w", encoding="utf-8") as f:
        f.write(
            api_h_source
            % ("\n".join(typedefs), "\n".join(internal_def), "\n".join(external_def))
        )

    api_c_source = api_c.read_text(encoding="utf-8")
    with api_c_out.open("w", encoding="utf-8") as f:
        f.write(api_c_source % (",\n    ".join(array_def),))

    mod_source = mod_c.read_text(encoding="utf-8")
    mod_c_out.write_text(
        mod_source
        % (
            "\n    ".join([f"{name}__mod_clear(m, state);" for name in mod_types]),
            "\n  ".join([f"SETUP_TYPES({name})" for name in mod_types]),
            "\n  ".join([f"ADD_OBJECTS({name})" for name in mod_types]),
        ),
        encoding="utf-8",
    )

    private_h_source = private_h.read_text(encoding="utf-8")
    private_h_out.write_text(
        private_h_source % ("\n".join([f"_CpDef_ModFn({name});" for name in mod_types]))
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("api_header", type=pathlib.Path)
    parser.add_argument("api_source", type=pathlib.Path)
    parser.add_argument("mod_source", type=pathlib.Path)
    parser.add_argument("private_header", type=pathlib.Path)

    argv = parser.parse_args()
    genapi(argv.api_header, argv.api_source, argv.mod_source, argv.private_header)
