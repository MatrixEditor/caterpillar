/* option implementation */

#include "caterpillar/option.h"
#include "structmember.h"

/* impl */

static PyObject*
cp_option_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpOptionObject* self;
  self = (CpOptionObject*)type->tp_alloc(type, 0);
  if (self == NULL) {
    return NULL;
  }

  self->name = PyUnicode_FromString("");
  if (!self->name) {
    Py_DECREF(self->name);
    return NULL;
  }

  Py_INCREF(Py_None);
  self->value = Py_None;
  return (PyObject*)self;
}

static void
cp_option_dealloc(CpOptionObject* self)
{
  Py_XDECREF(self->name);
  Py_XDECREF(self->value);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
cp_option_repr(CpOptionObject* self)
{
  return PyUnicode_FromFormat(
    "<option %R=%R>", self->name, self->value);
}

static PyObject*
cp_option_richcmp(CpOptionObject* self, PyObject* other, int op)
{
  if (!PyObject_IsInstance(other, (PyObject*)&CpOption_Type)) {
    Py_RETURN_NOTIMPLEMENTED;
  }
  return PyObject_RichCompare(self->name, ((CpOptionObject*)other)->name, op);
}

static Py_hash_t
cp_option_hash(CpOptionObject* self)
{
  return PyObject_Hash(self->name);
}

static int
cp_option_init(CpOptionObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "name", "value", NULL };
  PyObject *name = NULL, *value = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "|UO", kwlist, &name, &value))
    return -1;

  if (name) {
    Py_XSETREF(self->name, Py_NewRef(name));
  }
  if (value) {
    Py_XSETREF(self->value, Py_NewRef(value));
  }

  if (PyUnicode_GET_LENGTH(self->name) == 0) {
    PyErr_SetString(PyExc_ValueError, "name cannot be an empty string");
    return -1;
  }
  return 0;
}

/* docs */

PyDoc_STRVAR(cp_option_doc, "\
Option(name, value)\n\
--\n\
\n\
Simple customizable user option.");

/* type setup */
static PyMemberDef CpOption_Members[] = {
  { "name",
    T_OBJECT,
    offsetof(CpOptionObject, name),
    READONLY,
    PyDoc_STR("The name of this option (must be unique).") },
  { "value",
    T_OBJECT,
    offsetof(CpOptionObject, value),
    0,
    PyDoc_STR("The value of this option (optional).") },
  { NULL } /* Sentinel */
};

PyTypeObject CpOption_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(Option),
  .tp_basicsize =sizeof(CpOptionObject),
  .tp_dealloc =(destructor)cp_option_dealloc,
  .tp_repr =(reprfunc)cp_option_repr,
  .tp_hash =(hashfunc)cp_option_hash,
  .tp_flags =Py_TPFLAGS_DEFAULT,
  .tp_doc =cp_option_doc,
  .tp_richcompare =(richcmpfunc)cp_option_richcmp,
  .tp_members =CpOption_Members,
  .tp_init =(initproc)cp_option_init,
  .tp_new =cp_option_new,
};