#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include "cp_macros.h"

// ------------------------------------------------------------------------------
// structs
// ------------------------------------------------------------------------------
struct CpOption;
struct CpArch;
struct CpEndian;

// ------------------------------------------------------------------------------
// state
// ------------------------------------------------------------------------------
typedef struct
{
  // global options
  PyObject* cp_option__dynamic;
  PyObject* cp_option__sequential;
  PyObject* cp_option__keep_position;

  // global default options
  PyObject* cp_option__global_field_options;

  // global arch
  PyObject* cp_arch__host;
} _coremodulestate;

static inline _coremodulestate*
get_core_state(PyObject* module)
{
  void* state = PyModule_GetState(module);
  assert(state != NULL);
  return (_coremodulestate*)state;
}

// ------------------------------------------------------------------------------
// CpOption
// ------------------------------------------------------------------------------
typedef struct CpOption
{
  PyObject_HEAD PyObject* name;
  PyObject* value;
} CpOption;

static PyObject*
cp_option_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpOption* self;
  self = (CpOption*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

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
cp_option_dealloc(CpOption* self)
{
  Py_XDECREF(self->name);
  Py_XDECREF(self->value);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
cp_option_repr(CpOption* self)
{
  return PyUnicode_FromFormat(
    "CpOption(name=%R value=%R)", self->name, self->value);
}

static PyObject*
cp_option_richcmp(CpOption* self, CpOption* other, int op)
{
  return PyObject_RichCompare(self->name, other->name, op);
}

static Py_hash_t
cp_option_hash(CpOption* self)
{
  return PyObject_Hash(self->name);
}

static int
cp_option_init(CpOption* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "name", "value", NULL };
  PyObject *name = NULL, *value = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "|UO", kwlist, &name, &value))
    return -1;

  if (name) {
    Py_XSETREF(self->name, name);
    Py_INCREF(self->name);
  }
  if (value) {
    Py_XSETREF(self->value, value);
    Py_INCREF(self->value);
  }

  if (PyUnicode_GET_LENGTH(self->name) == 0) {
    PyErr_SetString(PyExc_ValueError, "name cannot be an empty string");
    return -1;
  }
  return 0;
}

static const char cp_option__doc__[] =
  ("CpOption(name, value)\n"
   "\n"
   "Simple customizable user option.\n"
   "\n"
   ":param name: The name of this option (must be unique).\n"
   ":type name: str\n"
   ":param value: The value of this option, defaults to None\n"
   ":type value: Optional[Any]\n");

static PyMemberDef CpOption_Members[] = {
  { "name",
    T_OBJECT_EX,
    offsetof(CpOption, name),
    READONLY,
    PyDoc_STR("The name of this option (must be unique).") },
  { "value",
    T_OBJECT_EX,
    offsetof(CpOption, value),
    0,
    PyDoc_STR("The value of this option (optional).") },
  { NULL } /* Sentinel */
};

PyTypeObject CpOption_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = _Cp_Name(_core.CpOption),
  .tp_doc = cp_option__doc__,
  .tp_basicsize = sizeof(CpOption),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = cp_option_new,
  .tp_dealloc = (destructor)cp_option_dealloc,
  .tp_init = (initproc)cp_option_init,
  .tp_members = CpOption_Members,
  .tp_repr = (reprfunc)cp_option_repr,
  .tp_richcompare = (richcmpfunc)cp_option_richcmp,
  .tp_hash = (hashfunc)cp_option_hash,
};

// ------------------------------------------------------------------------------
// CpArch
// ------------------------------------------------------------------------------
typedef struct CpArch
{
  PyObject_HEAD PyObject* m_name;
  int m_ptr_size;
} CpArch;

static PyObject*
cp_arch_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpArch* self;
  self = (CpArch*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->m_name = PyUnicode_FromString("");
  if (!self->m_name) {
    Py_DECREF(self->m_name);
    return NULL;
  }
  self->m_ptr_size = 0;
  return (PyObject*)self;
}

static void
cp_arch_dealloc(CpOption* self)
{
  Py_XDECREF(self->name);
  self->value = 0;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_arch_init(CpArch* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "name", "ptr_size", NULL };
  PyObject* name = NULL;
  int value = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "Ui", kwlist, &name, &value))
    return -1;

  if (name) {
    Py_XSETREF(self->m_name, name);
    Py_INCREF(self->m_name);
  }
  self->m_ptr_size = value;
  if (PyUnicode_GET_LENGTH(self->m_name) == 0) {
    PyErr_SetString(PyExc_ValueError, "name cannot be an empty string");
    return -1;
  }
  return 0;
}

static PyObject*
cp_arch_repr(CpArch* self)
{
  return PyUnicode_FromFormat(
    "CpArch(name=%R, ptr_size=%i)", self->m_name, self->m_ptr_size);
}

static PyObject*
cp_arch_richcmp(CpArch* self, CpArch* other, int op)
{
  return PyObject_RichCompare(self->m_name, other->m_name, op);
}

static Py_hash_t
cp_arch_hash(CpArch* self)
{
  return PyObject_Hash(self->m_name);
}

static const char cp_arch__doc__[] =
  ("CpArch(name, value)\n"
   "\n"
   "Represents a system architecture with a name and an indication of "
   "whether it is 64-bit\n"
   "\n"
   ":param name: The name of this architecture (must be unique).\n"
   ":type name: str\n"
   ":param ptr_size: the amount of bits one pointer takes\n"
   ":type ptr_size: int\n");

static PyMemberDef CpArch_Members[] = {
  { "name",
    T_OBJECT_EX,
    offsetof(CpArch, m_name),
    READONLY,
    PyDoc_STR("The name of this architecture (must be unique).") },
  { "ptr_size",
    T_OBJECT_EX,
    offsetof(CpArch, m_ptr_size),
    0,
    PyDoc_STR("the amount of bits one pointer takes.") },
  { NULL } /* Sentinel */
};

PyTypeObject CpArch_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = _Cp_Name(_core.CpArch),
  .tp_doc = cp_arch__doc__,
  .tp_basicsize = sizeof(CpArch),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = cp_arch_new,
  .tp_dealloc = (destructor)cp_arch_dealloc,
  .tp_init = (initproc)cp_arch_init,
  .tp_members = CpArch_Members,
  .tp_repr = (reprfunc)cp_arch_repr,
  .tp_richcompare = (richcmpfunc)cp_arch_richcmp,
  .tp_hash = (hashfunc)cp_arch_hash,
};

// ------------------------------------------------------------------------------
// CpEndian
// ------------------------------------------------------------------------------
typedef struct CpEndian {
  PyObject_HEAD
  PyObject* m_name;
  char m_id;
} CpEndian;



// ------------------------------------------------------------------------------
// Module
// ------------------------------------------------------------------------------
static int
_coremodule_clear(PyObject* m)
{
  _coremodulestate* state = get_core_state(m);
  if (state) {
    Py_CLEAR(state->cp_option__dynamic);
    Py_CLEAR(state->cp_option__sequential);
    Py_CLEAR(state->cp_option__keep_position);
    Py_CLEAR(state->cp_option__global_field_options);
  }
  return 0;
}

static void
_coremodule_free(void* m)
{
  _coremodule_clear((PyObject*)m);
}

static const char _coremodule__doc__[] = ("...");

static struct PyModuleDef _coremodule = {
  PyModuleDef_HEAD_INIT,       .m_name = _Cp_Name(_core),
  .m_doc = _coremodule__doc__, .m_size = sizeof(_coremodulestate),
  .m_methods = NULL,           .m_clear = _coremodule_clear,
  .m_free = _coremodule_free,
};

PyMODINIT_FUNC
PyInit__core(void)
{

  PyObject* m;
  m = PyState_FindModule(&_coremodule);
  if (m) {
    Py_INCREF(m);
    return m;
  }

  CpType_Ready(&CpOption_Type);
  CpType_Ready(&CpArch_Type);

  m = PyModule_Create(&_coremodule);
  if (!m) {
    return NULL;
  }
  CpModule_AddObject("CpOption", &CpOption_Type);
  CpModule_AddObject("CpArch", &CpArch_Type);

  // setup state
  _coremodulestate* state = get_core_state(m);

  CpModule_AddOption(cp_option__dynamic, "field:dynamic", "F_DYNAMIC");
  CpModule_AddOption(cp_option__sequential, "field:sequential", "F_SEQUENTIAL");
  CpModule_AddOption(
    cp_option__keep_position, "field:keep_position", "F_KEEP_POSITION");

  CpModule_AddGlobalOptions(cp_option__global_field_options, "G_FIELD_OPTIONS");

  CpModule_AddArch(cp_arch__host, "<host>", sizeof(void*) * 8, "HOST_ARCH");
  return m;
}