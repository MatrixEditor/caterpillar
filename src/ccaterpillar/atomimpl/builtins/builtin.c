/* builtinatom C implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

/* impl */
static PyObject*
cp_builtinatom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpBuiltinAtomObject* self;
  self = (CpBuiltinAtomObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;
  self->ob_base.ob_bits = NULL;
  self->ob_base.ob_pack = NULL;
  self->ob_base.ob_pack_many = NULL;
  self->ob_base.ob_unpack = NULL;
  self->ob_base.ob_unpack_many = NULL;
  self->ob_base.ob_size = NULL;
  self->ob_base.ob_type = NULL;
  return (PyObject*)self;
}

static void
cp_builtinatom_dealloc(CpBuiltinAtomObject* self)
{
  self->ob_base.ob_bits = NULL;
  self->ob_base.ob_pack = NULL;
  self->ob_base.ob_pack_many = NULL;
  self->ob_base.ob_unpack = NULL;
  self->ob_base.ob_unpack_many = NULL;
  self->ob_base.ob_size = NULL;
  self->ob_base.ob_type = NULL;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_builtinatom_init(CpBuiltinAtomObject* self, PyObject* args, PyObject* kw)
{
  _Cp_InitNoArgs(CpBuiltinAtomObject, args, kw);
}

// TODO member methods
static PyObject*
cp_builtinatom_as_mapping_getitem(CpBuiltinAtomObject* self, PyObject* length)
{
  return (PyObject*)CpRepeatedAtom_New((PyObject*)self, length);
}

static PyObject*
cp_builtinatom_as_number_rshift(PyObject* self, PyObject* other)
{
  return (PyObject*)CpSwitchAtom_New(self, other);
}

static PyObject*
cp_builtinatom_as_number_floordiv(PyObject* self, PyObject* other)
{
  return (PyObject*)CpConditionAtom_New(self, other);
}

static PyObject*
cp_builtinatom_as_number_matmul(PyObject* self, PyObject* other)
{
  return (PyObject*)CpOffsetAtom_New(self, other);
}

static PyMappingMethods CpBuiltinAtom_MappingMethods = {
  .mp_subscript = (binaryfunc)cp_builtinatom_as_mapping_getitem,
};

static PyNumberMethods CpBuiltinAtom_NumberMethods = {
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
  .tp_as_mapping = &CpBuiltinAtom_MappingMethods,
  .tp_as_number = &CpBuiltinAtom_NumberMethods,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
};
