/* builtinatom C implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

/* impl */
static PyObject*
cp_builtinatomobj_new(PyTypeObject* type, PyObject* args, PyObject* kw)
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
cp_builtinatomobj_dealloc(CpBuiltinAtomObject* self)
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
cp_builtinatomobj_init(CpBuiltinAtomObject* self, PyObject* args, PyObject* kw)
{
  _Cp_InitNoArgs(CpBuiltinAtomObject, args, kw);
}

// TODO member methods
static PyObject*
cp_builtinatomobj_as_mapping_getitem(CpBuiltinAtomObject* self,
                                     PyObject* length)
{
  return (PyObject*)CpRepeatedAtom_New((PyObject*)self, length);
}

static PyMappingMethods CpFieldAtom_MappingMethods = {
  .mp_subscript = (binaryfunc)cp_builtinatomobj_as_mapping_getitem,
};

PyTypeObject CpBuiltinAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) "CpBuiltinAtom", // tp_name
  .tp_basicsize = sizeof(CpBuiltinAtomObject),
  .tp_dealloc = (destructor)cp_builtinatomobj_dealloc,
  .tp_init = (initproc)cp_builtinatomobj_init,
  .tp_new = (newfunc)cp_builtinatomobj_new,
  .tp_as_mapping = &CpFieldAtom_MappingMethods,
};
