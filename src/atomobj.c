/* atom base object */

#include "atomobj.h"
#include "macros.h"

#include <stddef.h>

static PyObject*
cp_atom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  return type->tp_alloc(type, 0);
}

static void
cp_atom_dealloc(CpAtomObject* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_atom_pack(CpAtomObject* self, PyObject* args, PyObject* kw)
{
  PyErr_Format(PyExc_NotImplementedError,
               "The atom of type '%s' cannot be packed (missing __pack__)",
               Py_TYPE(self)->tp_name);
  return NULL;
}

static PyObject*
cp_atom_unpack(CpAtomObject* self, PyObject* args, PyObject* kw)
{
  PyErr_Format(PyExc_NotImplementedError,
               "The atom of type '%s' cannot be unpacked (missing __unpack__)",
               Py_TYPE(self)->tp_name);
  return NULL;
}

static PyObject*
cp_atom_type(CpAtomObject* self)
{
  Py_RETURN_NOTIMPLEMENTED;
}

static PyObject*
cp_atom_size(CpAtomObject* self, PyObject* args, PyObject* kw)
{
  PyErr_Format(PyExc_NotImplementedError,
               "The atom of type '%s' has no size (missing __size__)",
               Py_TYPE(self)->tp_name);
  return NULL;
}

/* Doc strings */

PyDoc_STRVAR(cp_atom_doc, "\
atom()\n\
--\n\
\n\
The base class for all atom objects. It does not define any functionality, only \
default implementations for special methods.");

PyDoc_STRVAR(cp_atom__pack__doc, "\
__pack__(self, obj, ctx)\n\
\n\
Should pack the given object (`obj`) using the current context. The default \
behaviour is to raise a `NotImplementedError`.");

PyDoc_STRVAR(cp_atom__unpack__doc, "\
__unpack__(self, ctx)\n\
\n\
Unpacks an object from the current context. The default \
behaviour is to raise a `NotImplementedError`.");

PyDoc_STRVAR(cp_atom__type__doc, "\
__type__(self)\n\
\n\
Returns the type of the atom (representation type, not this class).");

PyDoc_STRVAR(cp_atom__size__doc, "\
__size__(self, ctx)\n\
\n\
Returns the size of the atom in bytes. The default \
behaviour is to raise a `NotImplementedError`.");

/* method definition */

static PyMethodDef CpAtom_Methods[] = {
  { "__pack__", (PyCFunction)cp_atom_pack, METH_VARARGS, cp_atom__pack__doc },
  { "__unpack__", (PyCFunction)cp_atom_unpack, METH_VARARGS, cp_atom__unpack__doc },
  { "__type__", (PyCFunction)cp_atom_type, METH_NOARGS, cp_atom__type__doc },
  { "__size__", (PyCFunction)cp_atom_size, METH_VARARGS, cp_atom__size__doc },
  { NULL }, /* Sentinel */
};

/* The type object for _atomobj */

PyTypeObject CpAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(_core.atom),
  sizeof(CpAtomObject),                     /* tp_basicsize */
  0,                                        /* tp_itemsize */
  (destructor)cp_atom_dealloc,              /* tp_dealloc */
  0,                                        /* tp_vectorcall_offset */
  0,                                        /* tp_getattr */
  0,                                        /* tp_setattr */
  0,                                        /* tp_as_async */
  0,                                        /* tp_repr */
  0,                                        /* tp_as_number */
  0,                                        /* tp_as_sequence */
  0,                                        /* tp_as_mapping */
  0,                                        /* tp_hash */
  0,                                        /* tp_call */
  0,                                        /* tp_str */
  0,                                        /* tp_getattro */
  0,                                        /* tp_setattro */
  0,                                        /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
  cp_atom_doc,                              /* tp_doc */
  0,                                        /* tp_traverse */
  0,                                        /* tp_clear */
  0,                                        /* tp_richcompare */
  0,                                        /* tp_weaklistoffset */
  0,                                        /* tp_iter */
  0,                                        /* tp_iternext */
  CpAtom_Methods,                           /* tp_methods */
  0,                                        /* tp_members */
  0,                                        /* tp_getset */
  0,                                        /* tp_base */
  0,                                        /* tp_dict */
  0,                                        /* tp_descr_get */
  0,                                        /* tp_descr_set */
  0,                                        /* tp_dictoffset */
  0,                                        /* tp_init */
  0,                                        /* tp_alloc */
  cp_atom_new,                              /* tp_new */
  0,                                        /* tp_vectorcall */
};