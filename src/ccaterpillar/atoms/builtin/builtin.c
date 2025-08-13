#include "../../private.h"
#include "caterpillar/caterpillar.h"

#include <structmember.h>

PyObject*
cp_builtinatom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpBuiltinAtomObject* self;
  if ((self = (CpBuiltinAtomObject*)type->tp_alloc(type, 0), !self)) {
    return NULL;
  }

  Cp_ATOM(self).ob_bits = NULL;
  Cp_ATOM(self).ob_pack = NULL;
  Cp_ATOM(self).ob_pack_many = NULL;
  Cp_ATOM(self).ob_unpack = NULL;
  Cp_ATOM(self).ob_unpack_many = NULL;
  Cp_ATOM(self).ob_type = NULL;
  Cp_ATOM(self).ob_size = NULL;
  return _Cp_CAST(PyObject*, self);
}

void
cp_builtinatom_dealloc(CpBuiltinAtomObject* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
cp_builtinatom_repr(CpBuiltinAtomObject* self)
{
  return PyUnicode_FromString("<BuiltinAtom>");
}

static int
cp_builtinatom_init(CpBuiltinAtomObject* self, PyObject* args, PyObject* kw)
{
  _Cp_InitNoArgs(BuiltinAtoms, args, kw);
}

static PyObject*
cp_builtinatom_getitem(PyObject* self, PyObject* pLength)
{
  return CpRepeatedAtom_New(self, pLength);
}

static PyObject*
cp_builtinatom_as_number_rshift(PyObject* self, PyObject* pCases)
{
  return CpSwitchAtom_New(self, pCases);
}

static PyObject*
cp_builtinatom_as_number_floordiv(PyObject* self, PyObject* pCondition)
{
  return CpConditionalAtom_New(self, pCondition);
}

static PyObject*
cp_builtinatom_as_number_matmul(PyObject* self, PyObject* pOffset)
{
  return CpOffsetAtom_New(self, pOffset, PY_SEEK_SET);
}

PyMappingMethods CpBuiltinAtom_MappingMethods = {
  .mp_subscript = (binaryfunc)cp_builtinatom_getitem,
};

PyNumberMethods CpBuiltinAtom_NumberMethods = {
  .nb_rshift = (binaryfunc)cp_builtinatom_as_number_rshift,
  .nb_floor_divide = (binaryfunc)cp_builtinatom_as_number_floordiv,
  .nb_matrix_multiply = (binaryfunc)cp_builtinatom_as_number_matmul,
};

PyTypeObject CpBuiltinAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpBuiltinAtom_NAME),
  .tp_basicsize = sizeof(CpBuiltinAtomObject),
  .tp_dealloc = (destructor)cp_builtinatom_dealloc,
  .tp_init = (initproc)cp_builtinatom_init,
  .tp_new = (newfunc)cp_builtinatom_new,
  .tp_repr = (reprfunc)cp_builtinatom_repr,
  .tp_as_mapping = &CpBuiltinAtom_MappingMethods,
  .tp_as_number = &CpBuiltinAtom_NumberMethods,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
};

/* init */
int
cp_builtin__mod_types()
{
  CpBuiltinAtom_Type.tp_base = &CpAtom_Type;
  CpModule_SetupType(&CpBuiltinAtom_Type, -1);
  return 0;
}

void
cp_builtin__mod_clear(PyObject* m, _modulestate* state)
{
}

int
cp_builtin__mod_init(PyObject* m, _modulestate* state)
{
  CpModule_AddObject(CpBuiltinAtom_NAME, &CpBuiltinAtom_Type, -1);
  return 0;
}