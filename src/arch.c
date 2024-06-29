/* CpArch and CpEndian */
#include "caterpillar/arch.h"
#include "caterpillar/field.h"
#include "structmember.h"

/* CpArch */
static PyObject*
cp_arch_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpArchObject* self;
  self = (CpArchObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->name = PyUnicode_FromString("");
  if (!self->name) {
    Py_DECREF(self->name);
    return NULL;
  }
  self->pointer_size = 0;
  return (PyObject*)self;
}

static void
cp_arch_dealloc(CpArchObject* self)
{
  Py_XDECREF(self->name);
  self->pointer_size = 0;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_arch_init(CpArchObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "name", "ptr_size", NULL };
  PyObject* name = NULL;
  int value = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "Ui", kwlist, &name, &value))
    return -1;

  if (name) {
    Py_XSETREF(self->name, name);
    Py_INCREF(self->name);
  }
  self->pointer_size = value;
  if (PyUnicode_GET_LENGTH(self->name) == 0) {
    PyErr_SetString(PyExc_ValueError, "name cannot be an empty string");
    return -1;
  }
  return 0;
}

static PyObject*
cp_arch_repr(CpArchObject* self)
{
  return PyUnicode_FromFormat(
    "CpArch(name=%R, ptr_size=%i)", self->name, self->pointer_size);
}

static PyObject*
cp_arch_richcmp(CpArchObject* self, PyObject* other, int op)
{
  if (!PyObject_IsInstance(other, (PyObject*)&CpArch_Type)) {
    Py_RETURN_NOTIMPLEMENTED;
  }
  return PyObject_RichCompare(self->name, ((CpArchObject*)other)->name, op);
}

static Py_hash_t
cp_arch_hash(CpArchObject* self)
{
  return PyObject_Hash(self->name);
}

/* Doc strings */

PyDoc_STRVAR(cp_arch_doc, "\
CpArch(name, value)\n\
--\n\
Represents a system architecture with a name and an indication of \
pointer size.");

/* type setup */

static PyMemberDef CpArch_Members[] = { { "name",
                                          T_OBJECT,
                                          offsetof(CpArchObject, name),
                                          READONLY,
                                          "the architecture's name" },
                                        { "ptr_size",
                                          T_INT,
                                          offsetof(CpArchObject, pointer_size),
                                          READONLY,
                                          "the pointer size in bytes" },
                                        { NULL } /* Sentinel */ };

PyTypeObject CpArch_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(Arch), /* tp_name */
  sizeof(CpArchObject),                          /* tp_basicsize */
  0,                                             /* tp_itemsize */
  (destructor)cp_arch_dealloc,                   /* tp_dealloc */
  0,                                             /* tp_print */
  0,                                             /* tp_getattr */
  0,                                             /* tp_setattr */
  0,                                             /* tp_reserved */
  (reprfunc)cp_arch_repr,                        /* tp_repr */
  0,                                             /* tp_as_number */
  0,                                             /* tp_as_sequence */
  0,                                             /* tp_as_mapping */
  (hashfunc)cp_arch_hash,                        /* tp_hash */
  (ternaryfunc)cp_arch_richcmp,                  /* tp_call */
  0,                                             /* tp_str */
  0,                                             /* tp_getattro */
  0,                                             /* tp_setattro */
  0,                                             /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,                            /* tp_flags */
  cp_arch_doc,                                   /* tp_doc */
  0,                                             /* tp_traverse */
  0,                                             /* tp_clear */
  0,                                             /* tp_richcompare */
  0,                                             /* tp_weaklistoffset */
  0,                                             /* tp_iter */
  0,                                             /* tp_iternext */
  0,                                             /* tp_methods */
  CpArch_Members,                                /* tp_members */
  0,                                             /* tp_getset */
  0,                                             /* tp_base */
  0,                                             /* tp_dict */
  0,                                             /* tp_descr_get */
  0,                                             /* tp_descr_set */
  0,                                             /* tp_dictoffset */
  (initproc)cp_arch_init,                        /* tp_init */
  0,                                             /* tp_alloc */
  cp_arch_new,                                   /* tp_new */
  0,                                             /* tp_free */
  0,                                             /* tp_is_gc */
  0,                                             /* tp_bases */
  0,                                             /* tp_mro */
  0,                                             /* tp_cache */
  0,                                             /* tp_subclasses */
  0,                                             /* tp_weaklist */
  0,                                             /* tp_del */
  0,                                             /* tp_version_tag */
  0,                                             /* tp_finalize */
};

/* CpEndian */
int
CpEndian_IsLittleEndian(CpEndianObject* endian, _modulestate* mod)
{
  if (endian->id == '=') {
    #ifdef PY_LITTLE_ENDIAN
      return 1;
    #else
      return 0;
    #endif
  }
  return endian->id == '<';
}

static PyObject*
cp_endian_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpEndianObject* self;
  self = (CpEndianObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->name = PyUnicode_FromString("");
  if (!self->name) {
    Py_DECREF(self->name);
    return NULL;
  }
  self->id = 0;
  return (PyObject*)self;
}

static void
cp_endian_dealloc(CpEndianObject* self)
{
  Py_XDECREF(self->name);
  self->id = '=';
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_endian_init(CpEndianObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "name", "ch", NULL };
  PyObject* name = NULL;
  char value = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "Ub", kwlist, &name, &value))
    return -1;

  if (name) {
    Py_XSETREF(self->name, name);
    Py_INCREF(self->name);
  }
  self->id = value;
  if (PyUnicode_GET_LENGTH(self->name) == 0) {
    PyErr_SetString(PyExc_ValueError, "name cannot be an empty string");
    return -1;
  }
  return 0;
}

static PyObject*
cp_endian_repr(CpEndianObject* self)
{
  return PyUnicode_FromFormat(
    "CpEndian(name=%R, ch='%c')", self->name, self->id);
}

static PyObject*
cp_endian_richcmp(CpEndianObject* self, PyObject* other, int op)
{
  if (!PyObject_IsInstance(other, (PyObject*)&CpEndian_Type)) {
    Py_RETURN_NOTIMPLEMENTED;
  }

  return PyObject_RichCompare(self->name, ((CpEndianObject*)other)->name, op);
}

static Py_hash_t
cp_endian_hash(CpEndianObject* self)
{
  return PyObject_Hash(self->name);
}

static PyObject*
cp_endian_as_number_add(CpEndianObject* self, PyObject* atom)
{
  CpFieldObject* field = (CpFieldObject*)CpField_New(atom);
  if (!field) {
    return NULL;
  }
  _Cp_SetObj(field->m_endian, self);
  return (PyObject*)field;
}

/* Doc strings */

PyDoc_STRVAR(cp_endian_doc, "\
CpEndian(name, ch)\n\
--\n\
\n\
Represents common byte order information. The format character is \
used to incorporate the struct module internally.");

/* type setup */

static PyNumberMethods CpEndian_NumberMethods = {
  .nb_add = (binaryfunc)cp_endian_as_number_add
};


static PyMemberDef CpEndian_Members[] = {
  { "name",
    T_OBJECT_EX,
    offsetof(CpEndianObject, name),
    READONLY,
    "the name of the byte order" },
  { "ch",
    T_CHAR,
    offsetof(CpEndianObject, id),
    READONLY,
    "the byte order in format strings" },
  { NULL }
};

PyTypeObject CpEndian_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(Endian), /* tp_name */
  sizeof(CpEndianObject),                          /* tp_basicsize */
  0,                                               /* tp_itemsize */
  (destructor)cp_endian_dealloc,                   /* tp_dealloc */
  0,                                               /* tp_print */
  0,                                               /* tp_getattr */
  0,                                               /* tp_setattr */
  0,                                               /* tp_reserved */
  (reprfunc)cp_endian_repr,                        /* tp_repr */
  &CpEndian_NumberMethods,                                               /* tp_as_number */
  0,                                               /* tp_as_sequence */
  0,                                               /* tp_as_mapping */
  (hashfunc)cp_endian_hash,                        /* tp_hash */
  0,                                               /* tp_call */
  0,                                               /* tp_str */
  0,                                               /* tp_getattro */
  0,                                               /* tp_setattro */
  0,                                               /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,                              /* tp_flags */
  cp_endian_doc,                                   /* tp_doc */
  0,                                               /* tp_traverse */
  0,                                               /* tp_clear */
  (richcmpfunc)cp_endian_richcmp,                  /* tp_richcompare */
  0,                                               /* tp_weaklistoffset */
  0,                                               /* tp_iter */
  0,                                               /* tp_iternext */
  0,                                               /* tp_methods */
  CpEndian_Members,                                /* tp_members */
  0,                                               /* tp_getset */
  0,                                               /* tp_base */
  0,                                               /* tp_dict */
  0,                                               /* tp_descr_get */
  0,                                               /* tp_descr_set */
  0,                                               /* tp_dictoffset */
  (initproc)cp_endian_init,                        /* tp_init */
  0,                                               /* tp_alloc */
  cp_endian_new,                                   /* tp_new */
  0,                                               /* tp_free */
  0,                                               /* tp_is_gc */
  0,                                               /* tp_bases */
  0,                                               /* tp_mro */
  0,                                               /* tp_cache */
  0,                                               /* tp_subclasses */
  0,                                               /* tp_weaklist */
  0,                                               /* tp_del */
  0                                                /* tp_version_tag */
};