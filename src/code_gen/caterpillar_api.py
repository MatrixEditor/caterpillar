"""
Here we define all public functions and types to export into
our global struct. Each API dictionary contains the export
name and its target index. Therefore, one might break the whole
import system if an index is changed.

Make sure to check all standard indices before adding a new
function.
"""

# Reserved for future use
__reserved__ = '__reserved__'

cp_type_api = {
    0: "CpAtom_Type",
    1: "CpCAtom_Type",
}

cp_func_api = {
    # 1: "PyObject* CpAtom_Pack(PyObject* atom, PyObject* attrname, PyObject* op, PyObject* ctx)"
}