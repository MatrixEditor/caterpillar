/* CpArch and CpEndian */
#include "caterpillar/caterpillar.h"

#include "private.h"
#include <structmember.h>

/* CpArch */
/* ----------------------------------------------------------------------- */
static PyObject*
cp_arch_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpArchObject* self;
  self = (CpArchObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->name = PyUnicode_FromString("");
  if (!self->name) {
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
    _Cp_SetObj(self->name, name);
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
  return PyUnicode_FromFormat("<Arch %R x%d>", self->name, self->pointer_size);
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
cArch(name, value)\n\
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
  PyVarObject_HEAD_INIT(NULL, 0)
  .tp_name = _Cp_NameStr(CpArch_NAME), /* tp_name */
  .tp_basicsize = sizeof(CpArchObject),
  .tp_dealloc = (destructor)cp_arch_dealloc,
  .tp_repr = (reprfunc)cp_arch_repr,
  .tp_hash = (hashfunc)cp_arch_hash,
  .tp_richcompare = (richcmpfunc)cp_arch_richcmp,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_doc = cp_arch_doc,
  .tp_members = CpArch_Members,
  .tp_init = (initproc)cp_arch_init,
  .tp_new = cp_arch_new,
};

/* CpEndian */
/* ------------------------------------------------------------------------- */

/*CpAPI*/
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
    return NULL;
  }
  self->id = 0;
  return (PyObject*)self;
}

static void
cp_endian_dealloc(CpEndianObject* self)
{
  Py_XDECREF(self->name);
  self->id = 0;
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
    Py_INCREF(name);
    Py_XSETREF(self->name, name);
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
  switch (self->id) {
    case '=':
      return PyUnicode_FromFormat("<native-endian>");
    case '<':
      return PyUnicode_FromFormat("<le>");
    case '>':
    case '!':
      return PyUnicode_FromFormat("<be>");
    default:
      return PyUnicode_FromFormat("<Endian: %S ch='%c'>", self->name, self->id);
  }
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
  if (!atom) {
    PyErr_SetString(PyExc_ValueError, "atom must be non-null");
    return NULL;
  }

  return CpEndian_SetEndian(atom, self);
}

/* Doc strings */

PyDoc_STRVAR(cp_endian_doc, "\
cEndian(name, ch)\n\
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
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpEndian_NAME), /* tp_name */
  .tp_basicsize = sizeof(CpEndianObject),
  .tp_dealloc = (destructor)cp_endian_dealloc,
  .tp_repr = (reprfunc)cp_endian_repr,
  .tp_as_number = &CpEndian_NumberMethods,
  .tp_hash = (hashfunc)cp_endian_hash,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_doc = cp_endian_doc,
  .tp_richcompare = (richcmpfunc)cp_endian_richcmp,
  .tp_members = CpEndian_Members,
  .tp_init = (initproc)cp_endian_init,
  .tp_new = cp_endian_new,
};

/* init*/
int
cp_arch__mod_types()
{
  CpModule_SetupType(&CpArch_Type, -1);
  CpModule_SetupType(&CpEndian_Type, -1);
  return 0;
}

void
cp_arch__mod_clear(PyObject* m, _modulestate* state)
{
  Py_CLEAR(state->cp_endian__native);
  Py_CLEAR(state->cp_endian__little);
  Py_CLEAR(state->cp_endian__big);
  Py_CLEAR(state->cp_arch__host);
}

int
cp_arch__mod_init(PyObject* m, _modulestate* state)
{
  CpModule_AddObject(CpArch_NAME, &CpArch_Type, -1);
  CpModule_AddObject(CpEndian_NAME, &CpEndian_Type, -1);

  CpModuleState_AddObject(
    cp_endian__native, "NATIVE_ENDIAN", -1, CpEndian_New("native", '='));
  CpModuleState_AddObject(
    cp_endian__little, "LITTLE_ENDIAN", -1, CpEndian_New("little", '<'));
  CpModuleState_AddObject(
    cp_endian__big, "BIG_ENDIAN", -1, CpEndian_New("big", '>'));
  CpModuleState_AddObject(
    cp_arch__host, "HOST_ARCH", -1, CpArch_New("<host>", sizeof(void*) * 8));
  return 0;
}