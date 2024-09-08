/* atom base object */

#include "caterpillar/atomobj.h"
#include "caterpillar/macros.h"

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
cp_atom_init(CpAtomObject* self, PyObject* args, PyObject* kw)
{
  if ((args && PyTuple_Size(args)) || (kw && PyDict_Size(kw))) {
    PyErr_SetString(PyExc_TypeError,
                    "atoms cannot be initialized with arguments");
    return -1;
  }
  return 0;
}

static PyObject*
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
  { "__unpack__",
    (PyCFunction)cp_atom_unpack,
    METH_VARARGS,
    cp_atom__unpack__doc },
  { "__type__", (PyCFunction)cp_atom_type, METH_NOARGS, cp_atom__type__doc },
  { "__size__", (PyCFunction)cp_atom_size, METH_VARARGS, cp_atom__size__doc },
  { NULL }, /* Sentinel */
};

/* The type object for _atomobj */

PyTypeObject CpAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(atom),
  .tp_basicsize = sizeof(CpAtomObject),
  .tp_dealloc =(destructor)cp_atom_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = cp_atom_doc,
  .tp_methods = CpAtom_Methods,
  .tp_init =(initproc)cp_atom_init,
  .tp_new = (newfunc)cp_atom_new,
};

// ------------------------------------------------------------------------------
// catom

static PyObject*
cp_catom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpCAtomObject* self;
  self = (CpCAtomObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->ob_bits = NULL;
  self->ob_pack = NULL;
  self->ob_pack_many = NULL;
  self->ob_unpack = NULL;
  self->ob_unpack_many = NULL;
  self->ob_size = NULL;
  self->ob_type = NULL;
  return (PyObject*)self;
}

static void
cp_catom_dealloc(CpCAtomObject* self)
{
  self->ob_bits = NULL;
  self->ob_pack = NULL;
  self->ob_pack_many = NULL;
  self->ob_unpack = NULL;
  self->ob_unpack_many = NULL;
  self->ob_size = NULL;
  self->ob_type = NULL;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_catom_init(CpCAtomObject* self, PyObject* args, PyObject* kw)
{
  // We don't have to initialize anything here, because subclasses
  // will overload the `__init__` method and place their method
  // implementations.
  _Cp_InitNoArgs(catom, args, kw);
}

static PyObject*
cp_catom_pack(CpCAtomObject* self, PyObject* args, PyObject* kw)
{
  if (self->ob_pack == NULL) {
    PyErr_Format(PyExc_NotImplementedError,
                 "The atom of type '%s' cannot be packed (missing __pack__)",
                 Py_TYPE(self)->tp_name);
    return NULL;
  }

  static char* kwlist[] = { "op", "context", NULL };
  PyObject *op = NULL, *context = NULL;
  if (PyArg_ParseTupleAndKeywords(args, kw, "OO", kwlist, &op, &context) < 0) {
    return NULL;
  }

  return self->ob_pack((PyObject*)self, op, context) ? NULL
                                                     : Py_NewRef(Py_None);
}

static PyObject*
cp_catom_pack_many(CpCAtomObject* self, PyObject* args, PyObject* kw)
{
  if (self->ob_pack_many == NULL) {
    PyErr_Format(
      PyExc_NotImplementedError,
      "The atom of type '%s' cannot be packed (missing __pack_many__)",
      Py_TYPE(self)->tp_name);
    return NULL;
  }

  static char* kwlist[] = { "ops", "context", NULL };
  PyObject *ops = NULL, *context = NULL;
  if (PyArg_ParseTupleAndKeywords(args, kw, "OO", kwlist, &ops, &context) < 0) {
    return NULL;
  }

  return self->ob_pack_many((PyObject*)self, ops, context) ? NULL : Py_NewRef(Py_None);
}

static PyObject*
cp_catom_unpack(CpCAtomObject* self, PyObject* args, PyObject* kw)
{
  if (self->ob_unpack == NULL) {
    PyErr_Format(
      PyExc_NotImplementedError,
      "The atom of type '%s' cannot be unpacked (missing __unpack__)",
      Py_TYPE(self)->tp_name);
    return NULL;
  }

  static char* kwlist[] = { "context", NULL };
  PyObject* context = NULL;
  if (PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &context) < 0) {
    return NULL;
  }
  return self->ob_unpack((PyObject*)self, context);
}

static PyObject*
cp_catom_unpack_many(CpCAtomObject* self, PyObject* args, PyObject* kw)
{
  if (self->ob_unpack_many == NULL) {
    PyErr_Format(
      PyExc_NotImplementedError,
      "The atom of type '%s' cannot be unpacked (missing __unpack_many__)",
      Py_TYPE(self)->tp_name);
    return NULL;
  }

  static char* kwlist[] = { "context", NULL };
  PyObject* context = NULL;
  if (PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &context) < 0) {
    return NULL;
  }
  return self->ob_unpack_many((PyObject*)self, context);
}

static PyObject*
cp_catom_type(CpCAtomObject* self)
{
  if (self->ob_type == NULL) {
    Py_RETURN_NOTIMPLEMENTED;
  }
  return self->ob_type((PyObject*)self);
}

static PyObject*
cp_catom_size(CpCAtomObject* self, PyObject* args, PyObject* kw)
{
  if (self->ob_size == NULL) {
    PyErr_Format(PyExc_NotImplementedError,
                 "The atom of type '%s' has no size (missing __size__)",
                 Py_TYPE(self)->tp_name);
    return NULL;
  }

  static char* kwlist[] = { "context", NULL };
  PyObject* context = NULL;
  if (PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &context) < 0) {
    return NULL;
  }

  if (context == Py_None || context == NULL) {
    PyErr_SetString(PyExc_ValueError, "context must be set!");
    return NULL;
  }

  return self->ob_size((PyObject*)self, context);
}

/* docs */

PyDoc_STRVAR(cp_catom__doc__, "\
catom()\n\
--\n\
\n\
Base class for C atom types.");

/* type */
static PyMethodDef CpCAtom_Methods[] = {
  { "__pack__",
    (PyCFunction)cp_catom_pack,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { "__pack_many__",
    (PyCFunction)cp_catom_pack_many,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { "__unpack__",
    (PyCFunction)cp_catom_unpack,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { "__unpack_many__",
    (PyCFunction)cp_catom_unpack_many,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { "__type__", (PyCFunction)cp_catom_type, METH_NOARGS, NULL },
  { "__size__",
    (PyCFunction)cp_catom_size,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { NULL } /* Sentinel */
};

PyTypeObject CpCAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(catom),
  .tp_basicsize = sizeof(CpCAtomObject),
  .tp_dealloc = (destructor)cp_catom_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = cp_catom__doc__,
  .tp_methods = CpCAtom_Methods,
  .tp_init = (initproc)cp_catom_init,
  .tp_new = (newfunc)cp_catom_new,
};