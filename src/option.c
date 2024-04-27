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
    "CpOption(name=%R value=%R)", self->name, self->value);
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
  sizeof(CpOptionObject),         /* tp_basicsize */
  0,                              /* tp_itemsize */
  (destructor)cp_option_dealloc,  /* tp_dealloc */
  0,                              /* tp_vectorcall_offset */
  0,                              /* tp_getattr */
  0,                              /* tp_setattr */
  0,                              /* tp_as_async */
  (reprfunc)cp_option_repr,       /* tp_repr */
  0,                              /* tp_as_number */
  0,                              /* tp_as_sequence */
  0,                              /* tp_as_mapping */
  (hashfunc)cp_option_hash,       /* tp_hash */
  0,                              /* tp_call */
  0,                              /* tp_str */
  0,                              /* tp_getattro */
  0,                              /* tp_setattro */
  0,                              /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,             /* tp_flags */
  cp_option_doc,                  /* tp_doc */
  0,                              /* tp_traverse */
  0,                              /* tp_clear */
  (richcmpfunc)cp_option_richcmp, /* tp_richcompare */
  0,                              /* tp_weaklistoffset */
  0,                              /* tp_iter */
  0,                              /* tp_iternext */
  0,                              /* tp_methods */
  CpOption_Members,               /* tp_members */
  0,                              /* tp_getset */
  0,                              /* tp_base */
  0,                              /* tp_dict */
  0,                              /* tp_descr_get */
  0,                              /* tp_descr_set */
  0,                              /* tp_dictoffset */
  (initproc)cp_option_init,       /* tp_init */
  0,                              /* tp_alloc */
  cp_option_new,                  /* tp_new */
  0,                              /* tp_free */
  0,                              /* tp_is_gc */
  0,                              /* tp_bases */
  0,                              /* tp_mro */
  0,                              /* tp_cache */
  0,                              /* tp_subclasses */
  0,                              /* tp_weaklist */
  0,                              /* tp_del */
  0,                              /* tp_version_tag */
  0,                              /* tp_finalize */
  0,                              /* tp_vectorcall */
  0,                              /* tp_watched */
};