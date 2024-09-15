/* primitive atom C implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

/* impl */
static PyObject*
cp_primitiveatom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
    CpPrimitiveAtomObject* self;
    self = (CpPrimitiveAtomObject*)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;
    return (PyObject*)self;
}

static void
cp_primitiveatom_dealloc(CpPrimitiveAtomObject* self)
{
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_primitiveatom_init(CpPrimitiveAtomObject* self, PyObject* args, PyObject* kw)
{
    _Cp_InitNoArgs(CpPrimitiveAtomObject, args, kw);
}


static PyObject *
cp_primitiveatom_repr(CpPrimitiveAtomObject *self)
{
    return PyUnicode_FromString("<patom>");
}

// TODO member methods
static PyObject*
cp_primitiveatom_as_mapping_getitem(CpPrimitiveAtomObject* self, PyObject* length)
{
    return (PyObject*)CpRepeatedAtom_New((PyObject*)self, length);
}

static PyObject*
cp_primitiveatom_as_number_rshift(PyObject* self, PyObject* other)
{
    return (PyObject*)CpSwitchAtom_New(self, other);
}

static PyObject*
cp_primitiveatom_as_number_floordiv(PyObject* self, PyObject* other)
{
    return (PyObject*)CpConditionAtom_New(self, other);
}

static PyObject*
cp_primitiveatom_as_number_matmul(PyObject* self, PyObject* other)
{
  return (PyObject*)CpOffsetAtom_New(self, other);
}

static PyMappingMethods CpPrimitiveAtom_MappingMethods = {
  .mp_subscript = (binaryfunc)cp_primitiveatom_as_mapping_getitem,
};

static PyNumberMethods CpPrimitiveAtom_NumberMethods = {
  .nb_rshift = (binaryfunc)cp_primitiveatom_as_number_rshift,
  .nb_floor_divide = (binaryfunc)cp_primitiveatom_as_number_floordiv,
  .nb_matrix_multiply = (binaryfunc)cp_primitiveatom_as_number_matmul,
};

PyTypeObject CpPrimitiveAtom_Type = {
    PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpPrimitiveAtom_NAME),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_basicsize = sizeof(CpPrimitiveAtomObject),
    .tp_dealloc = (destructor)cp_primitiveatom_dealloc,
    .tp_init = (initproc)cp_primitiveatom_init,
    .tp_repr = (reprfunc)cp_primitiveatom_repr,
    .tp_new = (newfunc)cp_primitiveatom_new,
    .tp_doc = NULL,
    .tp_as_mapping = &CpPrimitiveAtom_MappingMethods,
    .tp_as_number = &CpPrimitiveAtom_NumberMethods,
};