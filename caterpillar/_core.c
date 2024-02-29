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
struct CpContext;
struct CpContextPath;
struct CpUnaryExpr;
struct CpBinaryExpr;
struct CpAtom;
struct CpField;
struct CpFieldAtom;
struct CpState;
struct CpStruct;

static PyTypeObject CpContextPath_Type;
static PyTypeObject CpEndian_Type;
static PyTypeObject CpContext_Type;
static PyTypeObject CpOption_Type;
static PyTypeObject CpArch_Type;
static PyTypeObject CpUnaryExpr_Type;
static PyTypeObject CpBinaryExpr_Type;
static PyTypeObject CpAtom_Type;
static PyTypeObject CpInvalidDefault_Type;
static PyTypeObject CpDefaultSwitchOption_Type;
static PyTypeObject CpField_Type;
static PyTypeObject CpFieldAtom_Type;
static PyTypeObject CpState_Type;
static PyTypeObject CpStruct_Type;

static PyObject _InvalidDefault_Object;
#define CP_INVALID_DEFAULT &_InvalidDefault_Object
#define Cp_IsInvalidDefault(o) ((o) == CP_INVALID_DEFAULT)

static PyObject _DefaultSwitchOption_Object;
#define CP_DEFAULT_OPTION &_DefaultSwitchOption_Object

static struct PyModuleDef _coremodule;

// ------------------------------------------------------------------------------
// function defs
// ------------------------------------------------------------------------------
typedef PyObject* (*packfunc)(PyObject*,
                              PyObject*,
                              PyObject*); // (self, obj, ctx)
typedef PyObject* (*unpackfunc)(PyObject*, PyObject*, PyObject*); // (self, ctx)
typedef PyObject* (*sizefunc)(PyObject*, PyObject*, PyObject*);   // (self, ctx)
typedef PyObject* (*typefunc)(PyObject*);                         // (self)
typedef PyObject* (*bitsfunc)(PyObject*);                         // (self)

typedef char* (*resizefunc)(PyObject**, Py_ssize_t);        // (*buf, newsize)
typedef PyObject* (*writefunc)(struct CpState*, PyObject*); // (self, obj)
typedef PyObject* (*readfunc)(struct CpState*, Py_ssize_t); // (self, size)
typedef PyObject* (*seekfunc)(struct CpState*,
                              PyObject*,
                              int);             // (self, offset, whence)
typedef PyObject* (*tellfunc)(struct CpState*); // (self)

static PyObject*
cp_typeof(PyObject* op);

static PyObject*
cp_typeof_field(struct CpField* op);

static PyObject*
cp_typeof_common(PyObject* op);

static int
cp_pack_internal(PyObject* op, PyObject* struct_, struct CpState* state);

static int
cp_pack_field(PyObject* op, struct CpField* field, struct CpState* state);

static int
cp_pack_common(PyObject* op, PyObject* atom, struct CpState* state);

static int
cp_pack(PyObject* op, PyObject* atom, PyObject* io, PyObject* globals, int raw);

// ------------------------------------------------------------------------------
// special attribute names
// ------------------------------------------------------------------------------
#define CpType_Template "__template__"
#define CpType_Struct "__struct__"
#define CpType_MRO "__mro__"

#define CpAtomType_Pack "__pack__"
#define CpAtomType_PackMany "__pack_many__"
#define CpAtomType_Unpack "__unpack__"
#define CpAtomType_UnpackMany "__unpack_many__"
#define CpAtomType_Size "__size__"
#define CpAtomType_Type "__type__"

#define CpUnionHook_Init "__model_init__"
#define CpUnionHook_SetAttr "__model_setattr__"

#define CpContext_GetAttr "__context_getattr__"

// ------------------------------------------------------------------------------
// state
// ------------------------------------------------------------------------------
typedef struct
{
  // global options
  PyObject* cp_option__dynamic;
  PyObject* cp_option__sequential;
  PyObject* cp_option__keep_position;
  PyObject* cp_option__union;
  PyObject* cp_option__eval;
  PyObject* cp_option__discard_unnamed;
  PyObject* cp_option__discard_const;
  PyObject* cp_option__replace_types;
  PyObject* cp_option__slots;

  // global default options
  PyObject* cp_option__global_field_options;
  PyObject* cp_option__global_struct_options;

  // compiled regex for unnamed fields
  PyObject* cp_regex__unnamed;

  // global arch
  PyObject* cp_arch__host;

  // default endian object
  PyObject* cp_endian__native;

  // typing constants
  PyObject* typing_any;
  PyObject* typing_list;
  PyObject* typing_union;

  // io buffers
  PyObject* io_bytesio;

  // inspect:
  // Why? - https://docs.python.org/3/howto/annotations.html
  PyObject* inspect_getannotations;

  // strings
  PyObject* str_tell;
  PyObject* str_seek;
  PyObject* str_write;
  PyObject* str_read;
  PyObject* str_close;
  PyObject* str___pack__;
  PyObject* str___pack_many__;
  PyObject* str___unpack__;
  PyObject* str___unpack_many__;
  PyObject* str___size__;
  PyObject* str___type__;
  PyObject* str___annotations__;
  PyObject* str___mro__;
  PyObject* str___struct__;
  PyObject* str___slots__;
  PyObject* str___match_args__;

  PyObject* str_start;
  PyObject* str_ctx__root;
  PyObject* str_ctx__getattr;
  PyObject* str_bytesio_getvalue;
  PyObject* str_builder_process;
  PyObject* str_pattern_match;
} _coremodulestate;

static inline _coremodulestate*
get_core_state(PyObject* module)
{
  void* state = PyModule_GetState(module);
  assert(state != NULL);
  return (_coremodulestate*)state;
}

static inline _coremodulestate*
get_global_core_state(void)
{
  PyObject* m = PyState_FindModule(&_coremodule);
  assert(m != NULL);
  return get_core_state(m);
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
cp_option_richcmp(CpOption* self, PyObject* other, int op)
{
  if (!PyObject_IsInstance(other, (PyObject*)&CpOption_Type)) {
    Py_RETURN_NOTIMPLEMENTED;
  }
  return PyObject_RichCompare(self->name, ((CpOption*)other)->name, op);
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
    T_OBJECT,
    offsetof(CpOption, name),
    READONLY,
    PyDoc_STR("The name of this option (must be unique).") },
  { "value",
    T_OBJECT,
    offsetof(CpOption, value),
    0,
    PyDoc_STR("The value of this option (optional).") },
  { NULL } /* Sentinel */
};

static PyTypeObject CpOption_Type = {
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
cp_arch_dealloc(CpArch* self)
{
  Py_XDECREF(self->m_name);
  self->m_ptr_size = 0;
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
cp_arch_richcmp(CpArch* self, PyObject* other, int op)
{
  if (!PyObject_IsInstance(other, (PyObject*)&CpArch_Type)) {
    Py_RETURN_NOTIMPLEMENTED;
  }
  return PyObject_RichCompare(self->m_name, ((CpArch*)other)->m_name, op);
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
    T_OBJECT,
    offsetof(CpArch, m_name),
    READONLY,
    PyDoc_STR("The name of this architecture (must be unique).") },
  { "ptr_size",
    T_OBJECT,
    offsetof(CpArch, m_ptr_size),
    0,
    PyDoc_STR("the amount of bits one pointer takes.") },
  { NULL } /* Sentinel */
};

static PyTypeObject CpArch_Type = {
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
typedef struct CpEndian
{
  /// the name of this endian object
  PyObject_HEAD PyObject* m_name;
  /// the format character
  char m_id;
} CpEndian;

static PyObject*
cp_endian_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpEndian* self;
  self = (CpEndian*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->m_name = PyUnicode_FromString("");
  if (!self->m_name) {
    Py_DECREF(self->m_name);
    return NULL;
  }
  self->m_id = 0;
  return (PyObject*)self;
}

static void
cp_endian_dealloc(CpEndian* self)
{
  Py_XDECREF(self->m_name);
  self->m_id = '=';
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_endian_init(CpEndian* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "name", "ch", NULL };
  PyObject* name = NULL;
  char value = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "Ub", kwlist, &name, &value))
    return -1;

  if (name) {
    Py_XSETREF(self->m_name, name);
    Py_INCREF(self->m_name);
  }
  self->m_id = value;
  if (PyUnicode_GET_LENGTH(self->m_name) == 0) {
    PyErr_SetString(PyExc_ValueError, "name cannot be an empty string");
    return -1;
  }
  return 0;
}

static PyObject*
cp_endian_repr(CpEndian* self)
{
  return PyUnicode_FromFormat(
    "CpEndian(name=%R, ch='%c')", self->m_name, self->m_id);
}

static PyObject*
cp_endian_richcmp(CpEndian* self, PyObject* other, int op)
{
  if (!PyObject_IsInstance(other, (PyObject*)&CpEndian_Type)) {
    Py_RETURN_NOTIMPLEMENTED;
  }

  return PyObject_RichCompare(self->m_name, ((CpEndian*)other)->m_name, op);
}

static Py_hash_t
cp_endian_hash(CpEndian* self)
{
  return PyObject_Hash(self->m_name);
}

static const char cp_endian__doc__[] =
  ("CpEndian(name, ch)\n"
   "\n"
   "Represents common byte order information. The format character is "
   "used to incorporate the struct module internally.\n"
   "\n"
   ":param name:  A string representing the name of the byte order.\n"
   ":type name: str\n"
   ":param ch: a single character representing the byte order in format "
   "strings.\n"
   ":type ch: str\n");

static PyMemberDef CpEndian_Members[] = {
  { "name",
    T_OBJECT,
    offsetof(CpEndian, m_name),
    READONLY,
    PyDoc_STR("The name of this architecture (must be unique).") },
  { "ptr_size",
    T_CHAR,
    offsetof(CpEndian, m_id),
    0,
    PyDoc_STR(
      "a single character representing the byte order in format strings.") },
  { NULL } /* Sentinel */
};

static PyTypeObject CpEndian_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = _Cp_Name(_core.CpEndian),
  .tp_doc = cp_arch__doc__,
  .tp_basicsize = sizeof(CpEndian),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = cp_endian_new,
  .tp_dealloc = (destructor)cp_endian_dealloc,
  .tp_init = (initproc)cp_endian_init,
  .tp_members = CpEndian_Members,
  .tp_repr = (reprfunc)cp_endian_repr,
  .tp_richcompare = (richcmpfunc)cp_endian_richcmp,
  .tp_hash = (hashfunc)cp_endian_hash,
};

// ------------------------------------------------------------------------------
// CpContext
// ------------------------------------------------------------------------------
typedef struct CpContext
{
  PyDictObject m_dict;
} CpContext;

static inline PyObject*
CpContext_Call(PyObject* op, PyObject* context)
{
  return PyObject_CallFunction(op, "O", context);
}

static int
cp_context_init(CpContext* self, PyObject* args, PyObject* kw)
{
  return PyDict_Type.tp_init((PyObject*)self, args, kw) < 0;
}

static int
cp_context__setattr__(CpContext* self, char* name, PyObject* value)
{
  return PyDict_SetItemString((PyObject*)&self->m_dict, name, value);
}

static inline PyObject*
_cp_context__context_getattr__(CpContext* self, char* name)
{
  PyObject *result = NULL, *tmp = NULL;
  char* line = name;
  char* token = strtok(line, ".");
  if (token == NULL) {
    PyErr_Format(PyExc_AttributeError, "CpContext has no attribute '%s'", name);
    return NULL;
  }

  result = PyDict_GetItemString((PyObject*)&self->m_dict, token);
  Py_XINCREF(result);
  while (result != NULL && (token = strtok(NULL, ".")) != NULL) {
    tmp = PyObject_GetAttrString(result, token);
    Py_XSETREF(result, tmp);
  };

  if (result == NULL) {
    PyErr_Format(
      PyExc_AttributeError, "'%s' has no attribute '%s'", name, token);
    return NULL;
  }
  return Py_NewRef(result);
}

static PyObject*
cp_context__context_getattr__(CpContext* self, PyObject* args)
{
  char* name;
  if (!PyArg_ParseTuple(args, "s", &name)) {
    return NULL;
  }
  return _cp_context__context_getattr__(self, name);
}

static PyObject*
cp_context__getattr__(CpContext* self, char* name)
{
  PyObject *key = PyUnicode_FromString(name), *tmp = NULL;
  PyObject* result = PyObject_GenericGetAttr((PyObject*)&self->m_dict, key);
  Py_XDECREF(key);
  if (result) {
    return result;
  }

  PyErr_Clear();
  return _cp_context__context_getattr__(self, name);
}

const char cp_context__doc__[] =
  ("CpContext(**kwargs)\n"
   "\n"
   "Represents a context object with attribute-style access.\n"
   "\n"
   ":param kwargs: The name and value of each keyword argument are used to "
   "initialize the context.\n"
   ":type kwargs: dict\n");

static PyMethodDef CpContext_Methods[] = {
  { CpContext_GetAttr,
    (PyCFunction)cp_context__context_getattr__,
    METH_VARARGS,
    NULL },
  { NULL } /* Sentinel */
};

static PyTypeObject CpContext_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = _Cp_Name(_core.CpContext),
  .tp_doc = cp_context__doc__,
  .tp_basicsize = sizeof(CpContext),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_init = (initproc)cp_context_init,
  .tp_setattr = (setattrfunc)cp_context__setattr__,
  .tp_getattr = (getattrfunc)cp_context__getattr__,
  .tp_methods = CpContext_Methods,
};

// ------------------------------------------------------------------------------
// CpUnaryExpr
// ------------------------------------------------------------------------------
enum
{
  CpUnaryExpr_OpNeg = 1,
  CpUnaryExpr_OpNot = 2,
  CpUnaryExpr_OpPos = 3
};

typedef struct CpUnaryExpr
{
  PyObject_HEAD int m_expr;
  PyObject* m_value;
} CpUnaryExpr;

static PyObject*
cp_unaryexpr_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpUnaryExpr* self;
  self = (CpUnaryExpr*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  Py_INCREF(Py_None);
  self->m_value = Py_None;
  self->m_expr = -1;
  return (PyObject*)self;
}

static void
cp_unaryexpr_dealloc(CpUnaryExpr* self)
{
  Py_XDECREF(self->m_value);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_unaryexpr_init(CpUnaryExpr* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "expr", "value", NULL };
  PyObject* value = NULL;
  int expr = -1;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "iO", kwlist, &expr, &value))
    return -1;

  if (value) {
    Py_XSETREF(self->m_value, value);
    Py_INCREF(self->m_value);
  }

  self->m_expr = expr;
  if (self->m_expr < 0 || self->m_expr > 3) {
    PyErr_SetString(PyExc_ValueError, "invalid expression type");
    return -1;
  }
  return 0;
}

static PyObject*
cp_unaryexpr_repr(CpUnaryExpr* self)
{
  char ch;
  switch (self->m_expr) {
    case CpUnaryExpr_OpNeg:
      ch = '-';
      break;
    case CpUnaryExpr_OpNot:
      ch = '!';
      break;
    case CpUnaryExpr_OpPos:
      ch = '+';
      break;
    default:
      ch = '?';
  }
  return PyUnicode_FromFormat("%c(%R)", ch, self->m_value);
}

static Py_hash_t
cp_unaryexpr_hash(CpUnaryExpr* self)
{
  PyObject* expr = PyLong_FromSize_t(self->m_expr);
  Py_hash_t hash = PyObject_Hash(expr);
  Py_XDECREF(expr);
  return hash;
}

static PyObject*
cp_unaryexpr__call__(CpUnaryExpr* self, PyObject* args, PyObject* kw)
{
  PyObject* value = self->m_value;
  if (PyCallable_Check(value)) {
    value = PyObject_Call(value, args, kw);
    if (!value) {
      if (!PyErr_Occurred()) {
        PyErr_SetString(PyExc_TypeError, "value must be callable");
      }
      Py_XDECREF(value);
      return NULL;
    }
  } else {
    Py_XINCREF(value);
  }

  if (!PyNumber_Check(value)) {
    PyErr_Format(PyExc_TypeError, "value must be a number, got %R", value);
    Py_XDECREF(value);
    return NULL;
  }

  PyObject* result;
  switch (self->m_expr) {
    case CpUnaryExpr_OpNeg:
      result = PyNumber_Negative(value);
      break;
    case CpUnaryExpr_OpNot:
      result = PyNumber_Invert(value);
      break;
    case CpUnaryExpr_OpPos:
      result = PyNumber_Positive(value);
      break;
    default:
      result = NULL;
      break;
  }

  Py_XDECREF(value);
  if (!result) {
    if (!PyErr_Occurred()) {
      PyErr_SetString(PyExc_TypeError, "invalid expression type");
    }
    return NULL;
  }
  return result;
}

static const char cp_unaryexpr__doc__[] = "CpUnaryExpr(expr, value)";

static PyMemberDef CpUnaryExpr_Members[] = {
  { "expr", T_INT, offsetof(CpUnaryExpr, m_expr), READONLY },
  { "value", T_OBJECT, offsetof(CpUnaryExpr, m_value), 0 },
  { NULL } /* Sentinel */
};

static PyTypeObject CpUnaryExpr_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name =
    _Cp_Name(_core.CpUnaryExpr),
  .tp_doc = cp_unaryexpr__doc__,
  .tp_basicsize = sizeof(CpUnaryExpr),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = cp_unaryexpr_new,
  .tp_dealloc = (destructor)cp_unaryexpr_dealloc,
  .tp_init = (initproc)cp_unaryexpr_init,
  .tp_members = CpUnaryExpr_Members,
  .tp_repr = (reprfunc)cp_unaryexpr_repr,
  .tp_hash = (hashfunc)cp_unaryexpr_hash,
  .tp_call = (ternaryfunc)cp_unaryexpr__call__,
};

// ------------------------------------------------------------------------------
// CpBinaryExpr
// ------------------------------------------------------------------------------
enum
{
  // The first six operations store the same value as defined by Python,
  // minimizing the effort to translate *_richcmp calls into this enum.

  CpBinaryExpr_Op_LT = 0,
  CpBinaryExpr_Op_LE,
  CpBinaryExpr_Op_EQ,
  CpBinaryExpr_Op_NE,
  CpBinaryExpr_Op_GT,
  CpBinaryExpr_Op_GE,
  CpBinaryExpr_OpAdd,
  CpBinaryExpr_OpSub,
  CpBinaryExpr_OpMul,
  CpBinaryExpr_OpFloorDiv,
  CpBinaryExpr_OpTrueDiv,
  CpBinaryExpr_OpMod,
  CpBinaryExpr_OpPow,
  CpBinaryExpr_OpMatMul,
  CpBinaryExpr_OpAnd,
  CpBinaryExpr_OpOr,
  CpBinaryExpr_OpBitXor,
  CpBinaryExpr_OpBitAnd,
  CpBinaryExpr_OpBitOr,
  CpBinaryExpr_OpLShift,
  CpBinaryExpr_OpRShift,
};

typedef struct CpBinaryExpr
{
  PyObject_HEAD int m_expr;
  PyObject* m_left;
  PyObject* m_right;
} CpBinaryExpr;

static PyObject*
cp_binaryexpr_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpBinaryExpr* self;
  self = (CpBinaryExpr*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  Py_INCREF(Py_None);
  self->m_right = Py_None;
  Py_INCREF(Py_None);
  self->m_left = Py_None;
  self->m_expr = -1;
  return (PyObject*)self;
}

static void
cp_binaryexpr_dealloc(CpBinaryExpr* self)
{
  Py_XDECREF(self->m_left);
  Py_XDECREF(self->m_right);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_binaryexpr_init(CpBinaryExpr* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "expr", "left", "right", NULL };
  PyObject *left = NULL, *right = NULL;
  int expr = -1;
  if (!PyArg_ParseTupleAndKeywords(
        args, kw, "iOO", kwlist, &expr, &left, &right)) {
    return -1;
  }

  if (left) {
    Py_XSETREF(self->m_left, left);
    Py_XINCREF(self->m_left);
  }

  if (right) {
    Py_XSETREF(self->m_right, right);
    Py_XINCREF(self->m_right);
  }

  self->m_expr = expr;
  if (self->m_expr < CpBinaryExpr_Op_LT ||
      self->m_expr > CpBinaryExpr_OpRShift) {
    PyErr_SetString(PyExc_ValueError, "invalid expression type");
    return -1;
  }
  return 0;
}

static PyObject*
cp_binaryexpr_repr(CpBinaryExpr* self)
{
  char* s;
  switch (self->m_expr) {
    case CpBinaryExpr_OpAdd:
      s = "+";
      break;
    case CpBinaryExpr_OpSub:
      s = "-";
      break;
    case CpBinaryExpr_OpMul:
      s = "*";
      break;
    case CpBinaryExpr_OpFloorDiv:
      s = "//";
      break;
    case CpBinaryExpr_OpTrueDiv:
      s = "/";
      break;
    case CpBinaryExpr_OpMod:
      s = "%";
      break;
    case CpBinaryExpr_OpPow:
      s = "**";
      break;
    case CpBinaryExpr_OpBitXor:
      s = "^";
      break;
    case CpBinaryExpr_OpBitAnd:
      s = "&";
      break;
    case CpBinaryExpr_OpBitOr:
      s = "|";
      break;
    case CpBinaryExpr_OpLShift:
      s = "<<";
      break;
    case CpBinaryExpr_OpRShift:
      s = ">>";
      break;
    case CpBinaryExpr_Op_GT:
      s = ">";
      break;
    case CpBinaryExpr_Op_GE:
      s = ">=";
      break;
    case CpBinaryExpr_Op_LT:
      s = "<";
      break;
    case CpBinaryExpr_Op_LE:
      s = "<=";
      break;
    case CpBinaryExpr_Op_EQ:
      s = "==";
      break;
    case CpBinaryExpr_Op_NE:
      s = "!=";
      break;
    case CpBinaryExpr_OpAnd:
      s = "and";
      break;
    case CpBinaryExpr_OpOr:
      s = "or";
      break;
    case CpBinaryExpr_OpMatMul:
      s = "@";
      break;
    default:
      PyErr_SetString(PyExc_ValueError, "invalid expression type");
      return NULL;
  }
  return PyUnicode_FromFormat("(%R) %s (%R)", self->m_left, s, self->m_right);
}

static PyObject*
cp_binaryexpr__call__(CpBinaryExpr* self, PyObject* args, PyObject* kw)
{
  PyObject* left = self->m_left;
  if (PyCallable_Check(left)) {
    left = PyObject_Call(left, args, kw);
    if (!left) {
      if (!PyErr_Occurred()) {
        PyErr_SetString(PyExc_RuntimeError, "Error during lhs evaluation");
      }
      Py_XDECREF(left);
      return NULL;
    }
  } else {
    Py_XINCREF(left);
  }

  PyObject* right = self->m_right;
  if (PyCallable_Check(right)) {
    right = PyObject_Call(right, args, kw);
    if (!right) {
      if (!PyErr_Occurred()) {
        PyErr_SetString(PyExc_RuntimeError, "Error during rhs evaluation");
      }
      Py_XDECREF(right);
      return NULL;
    }
  } else {
    Py_XINCREF(right);
  }

  PyObject* result;
  switch (self->m_expr) {
    case CpBinaryExpr_OpAdd:
      result = PyNumber_Add(left, right);
      break;
    case CpBinaryExpr_OpSub:
      result = PyNumber_Subtract(left, right);
      break;
    case CpBinaryExpr_OpMul:
      result = PyNumber_Multiply(left, right);
      break;
    case CpBinaryExpr_OpFloorDiv:
      result = PyNumber_FloorDivide(left, right);
      break;
    case CpBinaryExpr_OpTrueDiv:
      result = PyNumber_TrueDivide(left, right);
      break;
    case CpBinaryExpr_OpMod:
      result = PyNumber_Remainder(left, right);
      break;
    case CpBinaryExpr_OpPow:
      result = PyNumber_Power(left, right, Py_None);
      break;
    case CpBinaryExpr_OpBitXor:
      result = PyNumber_Xor(left, right);
      break;
    case CpBinaryExpr_OpBitAnd:
      result = PyNumber_And(left, right);
      break;
    case CpBinaryExpr_OpBitOr:
      result = PyNumber_Or(left, right);
      break;
    case CpBinaryExpr_OpLShift:
      result = PyNumber_Lshift(left, right);
      break;
    case CpBinaryExpr_OpRShift:
      result = PyNumber_Rshift(left, right);
      break;
    case CpBinaryExpr_Op_GT:
      result = PyObject_RichCompare(left, right, Py_GT);
      break;
    case CpBinaryExpr_Op_GE:
      result = PyObject_RichCompare(left, right, Py_GE);
      break;
    case CpBinaryExpr_Op_LT:
      result = PyObject_RichCompare(left, right, Py_LT);
      break;
    case CpBinaryExpr_Op_LE:
      result = PyObject_RichCompare(left, right, Py_LE);
      break;
    case CpBinaryExpr_Op_EQ:
      result = PyObject_RichCompare(left, right, Py_EQ);
      break;
    case CpBinaryExpr_Op_NE:
      result = PyObject_RichCompare(left, right, Py_NE);
      break;
    case CpBinaryExpr_OpAnd:
      result = PyNumber_And(left, right);
      break;
    case CpBinaryExpr_OpOr:
      result = PyNumber_Or(left, right);
      break;
    case CpBinaryExpr_OpMatMul:
      result = PyNumber_MatrixMultiply(left, right);
      break;
    default:
      result = NULL;
      break;
  }

  Py_XDECREF(left);
  Py_XDECREF(right);
  if (!result) {
    if (!PyErr_Occurred()) {
      PyErr_SetString(PyExc_TypeError, "invalid expression type");
    }
    return NULL;
  }
  return result;
}

static const char cp_binaryexpr__doc__[] = "CpBinaryExpr(expr, left, right)";

static PyMemberDef CpBinaryExpr_Members[] = {
  { "expr", T_INT, offsetof(CpBinaryExpr, m_expr), READONLY },
  { "lhs", T_OBJECT, offsetof(CpBinaryExpr, m_left), 0 },
  { "rhs", T_OBJECT, offsetof(CpBinaryExpr, m_left), 0 },
  { NULL } /* Sentinel */
};

static PyTypeObject CpBinaryExpr_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name =
    _Cp_Name(_core._CpBinaryExpr),
  .tp_doc = cp_binaryexpr__doc__,
  .tp_basicsize = sizeof(CpBinaryExpr),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = cp_binaryexpr_new,
  .tp_dealloc = (destructor)cp_binaryexpr_dealloc,
  .tp_init = (initproc)cp_binaryexpr_init,
  .tp_members = CpUnaryExpr_Members,
  .tp_repr = (reprfunc)cp_binaryexpr_repr,
  .tp_call = (ternaryfunc)cp_binaryexpr__call__,
};

// ------------------------------------------------------------------------------
// ContextPath
// ------------------------------------------------------------------------------
typedef struct CpContextPath
{
  PyObject_HEAD PyObject* m_path;

  _coremodulestate* m_state;
} CpContextPath;

static PyObject*
cp_contextpath_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpContextPath* self;
  self = (CpContextPath*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->m_path = PyUnicode_FromString("");
  if (!self->m_path) {
    Py_DECREF(self->m_path);
    return NULL;
  }
  self->m_state = get_global_core_state();
  return (PyObject*)self;
}

static void
cp_contextpath_dealloc(CpContextPath* self)
{
  Py_XDECREF(self->m_path);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_contextpath_init(CpContextPath* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "path", NULL };
  PyObject* path = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "|U", kwlist, &path))
    return -1;

  if (path) {
    Py_XSETREF(self->m_path, path);
    Py_INCREF(self->m_path);
  }
  return 0;
}

static PyObject*
cp_contextpath_repr(CpContextPath* self)
{
  return PyUnicode_FromFormat("CpPath(%R)", self->m_path);
}

static Py_hash_t
cp_contextpath_hash(CpContextPath* self)
{
  return PyObject_Hash(self->m_path);
}

static PyObject*
cp_contextpath__type__(CpContextPath* self)
{
  PyObject* type = get_global_core_state()->typing_any;
  Py_INCREF(type);
  return type;
}

static PyObject*
cp_contextpath__size__(CpContextPath* self, PyObject* args)
{
  return PyLong_FromSize_t(0);
}

static PyObject*
cp_contextpath__getattr__(CpContextPath* self, char* name)
{
  PyObject* key = PyUnicode_FromString(name);
  PyObject* result = PyObject_GenericGetAttr((PyObject*)&self->ob_base, key);
  Py_XDECREF(key);
  if (result) {
    return result;
  }

  PyErr_Clear();

  if (!self->m_path || PyUnicode_GET_LENGTH(self->m_path) == 0) {
    result = PyObject_CallFunction((PyObject*)&CpContextPath_Type, "s", name);
  } else {
    PyObject* path =
      PyUnicode_FromFormat("%s.%s", PyUnicode_AsUTF8(self->m_path), name);
    result = PyObject_CallFunction((PyObject*)&CpContextPath_Type, "O", path);
    Py_XDECREF(path);
  }

  Py_XINCREF(result);
  return result;
}

static PyObject*
cp_contextpath__call__(CpContextPath* self, PyObject* args, PyObject* kwargs)
{
  static char* kwlist[] = { "context", NULL };
  PyObject* context = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O", kwlist, &context))
    return NULL;

  if (!context || context == Py_None) {
    PyErr_SetString(PyExc_ValueError, "context cannot be None");
    return NULL;
  }

  return PyObject_CallMethodOneArg(
    context, self->m_state->str_ctx__getattr, self->m_path);
}

static PyObject*
cp_contextpath_as_number_neg(CpContextPath* self)
{
  return PyObject_CallFunction(
    (PyObject*)&CpUnaryExpr_Type, "iO", CpUnaryExpr_OpNeg, self);
}

static PyObject*
cp_contextpath_as_number_pos(CpContextPath* self)
{
  return PyObject_CallFunction(
    (PyObject*)&CpUnaryExpr_Type, "iO", CpUnaryExpr_OpPos, self);
}

static PyObject*
cp_contextpath_as_number_not(CpContextPath* self)
{
  return PyObject_CallFunction(
    (PyObject*)&CpUnaryExpr_Type, "iO", CpUnaryExpr_OpNot, self);
}

#define _CpContextPath_BinaryNumberMethod(name, op)                            \
  static PyObject* cp_contextpath_as_number_##name(CpContextPath* self,        \
                                                   PyObject* other)            \
  {                                                                            \
    return PyObject_CallFunction(                                              \
      (PyObject*)&CpBinaryExpr_Type, "iOO", op, self, other);                  \
  }

_CpContextPath_BinaryNumberMethod(add, CpBinaryExpr_OpAdd);
_CpContextPath_BinaryNumberMethod(sub, CpBinaryExpr_OpSub);
_CpContextPath_BinaryNumberMethod(mul, CpBinaryExpr_OpMul);
_CpContextPath_BinaryNumberMethod(div, CpBinaryExpr_OpTrueDiv);
_CpContextPath_BinaryNumberMethod(truediv, CpBinaryExpr_OpTrueDiv);
_CpContextPath_BinaryNumberMethod(floordiv, CpBinaryExpr_OpFloorDiv);
_CpContextPath_BinaryNumberMethod(mod, CpBinaryExpr_OpMod);
_CpContextPath_BinaryNumberMethod(lshift, CpBinaryExpr_OpLShift);
_CpContextPath_BinaryNumberMethod(rshift, CpBinaryExpr_OpRShift);
_CpContextPath_BinaryNumberMethod(and, CpBinaryExpr_OpBitAnd);
_CpContextPath_BinaryNumberMethod(xor, CpBinaryExpr_OpBitXor);
_CpContextPath_BinaryNumberMethod(or, CpBinaryExpr_OpBitOr);
_CpContextPath_BinaryNumberMethod(pow, CpBinaryExpr_OpPow);
_CpContextPath_BinaryNumberMethod(matmul, CpBinaryExpr_OpMatMul);

static PyObject*
cp_contextpath_richcmp(CpContextPath* self, PyObject* other, int op)
{
  return PyObject_CallFunction(
    (PyObject*)&CpBinaryExpr_Type, "iOO", op, self, other);
}

static PyMemberDef CpContextPath_Members[] = {
  { "path", T_OBJECT, offsetof(CpContextPath, m_path), READONLY },
  { NULL }
};

static PyMethodDef CpContextPath_Methods[] = {
  { "__type__", (PyCFunction)(typefunc)cp_contextpath__type__, METH_NOARGS },
  { "__size__", (PyCFunction)(sizefunc)cp_contextpath__size__, METH_VARARGS },

  { NULL, NULL }
};

static PyNumberMethods CpContextPath_NumberMethods = {
  // unary
  .nb_negative = (unaryfunc)cp_contextpath_as_number_neg,
  .nb_positive = (unaryfunc)cp_contextpath_as_number_pos,
  .nb_invert = (unaryfunc)cp_contextpath_as_number_not,
  // binary
  .nb_add = (binaryfunc)cp_contextpath_as_number_add,
  .nb_subtract = (binaryfunc)cp_contextpath_as_number_sub,
  .nb_multiply = (binaryfunc)cp_contextpath_as_number_mul,
  .nb_true_divide = (binaryfunc)cp_contextpath_as_number_truediv,
  .nb_floor_divide = (binaryfunc)cp_contextpath_as_number_floordiv,
  .nb_remainder = (binaryfunc)cp_contextpath_as_number_mod,
  .nb_power = (ternaryfunc)cp_contextpath_as_number_pow,
  .nb_lshift = (binaryfunc)cp_contextpath_as_number_lshift,
  .nb_rshift = (binaryfunc)cp_contextpath_as_number_rshift,
  .nb_and = (binaryfunc)cp_contextpath_as_number_and,
  .nb_xor = (binaryfunc)cp_contextpath_as_number_xor,
  .nb_or = (binaryfunc)cp_contextpath_as_number_or,
  .nb_matrix_multiply = (binaryfunc)cp_contextpath_as_number_matmul,
};

static PyTypeObject CpContextPath_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name =
    _Cp_Name(_core.CpContextPath),
  .tp_doc = "...",
  .tp_basicsize = sizeof(CpContextPath),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_init = (initproc)cp_contextpath_init,
  .tp_dealloc = (destructor)cp_contextpath_dealloc,
  .tp_repr = (reprfunc)cp_contextpath_repr,
  .tp_hash = (hashfunc)cp_contextpath_hash,
  .tp_getattr = (getattrfunc)cp_contextpath__getattr__,
  .tp_methods = CpContextPath_Methods,
  .tp_members = CpContextPath_Members,
  .tp_new = (newfunc)cp_contextpath_new,
  .tp_call = (ternaryfunc)cp_contextpath__call__,
  .tp_as_number = &CpContextPath_NumberMethods,
  .tp_richcompare = (richcmpfunc)cp_contextpath_richcmp,
};

#undef _CpContextPath_BinaryNumberMethod

// ------------------------------------------------------------------------------
// CpAtom
// ------------------------------------------------------------------------------
static inline bool
CpAtom_CanPack(PyObject* op)
{
  PyObject* attr = PyObject_GetAttrString(op, CpAtomType_Pack);
  if (attr) {
    Py_DECREF(attr);
    return true;
  }
  PyErr_Clear();
  return false;
}

static inline bool
CpAtom_CanUnpack(PyObject* op)
{
  PyObject* attr = PyObject_GetAttrString(op, CpAtomType_Unpack);
  if (attr) {
    Py_DECREF(attr);
    return true;
  }
  PyErr_Clear();
  return false;
}

static inline int
CpAtom_HasType(PyObject* op)
{
  PyObject* attr = PyObject_GetAttrString(op, CpAtomType_Type);
  if (attr) {
    Py_DECREF(attr);
    return true;
  }
  PyErr_Clear();
  return false;
}

static inline int
CpAtom_HasSize(PyObject* op)
{
  PyObject* attr = PyObject_GetAttrString(op, CpAtomType_Size);
  if (attr) {
    Py_DECREF(attr);
    return true;
  }
  PyErr_Clear();
  return false;
}

static inline int
CpAtom_FastCanPack(PyObject* op, _coremodulestate* state)
{
  PyObject* attr = PyObject_GetAttr(op, state->str___pack__);
  if (attr) {
    Py_DECREF(attr);
    return 1;
  }
  PyErr_Clear();
  return 0;
}

static inline int
CpAtom_FastCanUnpack(PyObject* op, _coremodulestate* state)
{
  PyObject* attr = PyObject_GetAttr(op, state->str___unpack__);
  if (attr) {
    Py_DECREF(attr);
    return 1;
  }
  PyErr_Clear();
  return 0;
}

static inline int
CpAtom_FastHasType(PyObject* op, _coremodulestate* state)
{
  PyObject* attr = PyObject_GetAttr(op, state->str___type__);
  if (attr) {
    Py_DECREF(attr);
    return 1;
  }
  PyErr_Clear();
  return 0;
}

static inline int
CpAtom_FastHasSize(PyObject* op, _coremodulestate* state)
{
  PyObject* attr = PyObject_GetAttr(op, state->str___size__);
  if (attr) {
    Py_DECREF(attr);
    return 1;
  }
  PyErr_Clear();
  return 0;
}

static inline int
CpAtom_Check(PyObject* op)
{
  return op && CpAtom_HasSize(op) && CpAtom_CanPack(op) && CpAtom_CanUnpack(op);
}

static inline int
CpAtom_CheckExact(PyObject* op)
{
  return op && op->ob_type == &CpAtom_Type;
}

typedef struct CpAtom
{
  PyObject_HEAD
} CpAtom;

static PyObject*
CpAtom_CallPack(PyObject* self, PyObject* name, PyObject* op, PyObject* ctx)
{
  PyObject* args = Py_BuildValue("(OO)", self, op, ctx);
  PyObject* attr = PyObject_GetAttr(self, name);
  if (!attr) {
    Py_DECREF(args);
    return NULL;
  }
  PyObject* res = PyObject_Call(attr, args, NULL);
  Py_DECREF(args);
  return res;
}

static PyObject*
cp_atom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpAtom* self;
  self = (CpAtom*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;
  return (PyObject*)self;
}

static void
cp_atom_dealloc(CpAtom* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_atom_pack(CpAtom* self, PyObject* args, PyObject* kw)
{
  PyErr_SetString(PyExc_NotImplementedError, "pack");
  return NULL;
}

static PyObject*
cp_atom_unpack(CpAtom* self, PyObject* args, PyObject* kw)
{
  PyErr_SetString(PyExc_NotImplementedError, "unpack");
  return NULL;
}

static PyObject*
cp_atom_type(CpAtom* self)
{
  Py_RETURN_NOTIMPLEMENTED;
}

static PyObject*
cp_atom_size(CpAtom* self, PyObject* args, PyObject* kw)
{
  PyErr_SetString(PyExc_NotImplementedError, "size");
  return NULL;
}

static PyMethodDef CpAtom_Methods[] = {
  { CpAtomType_Pack, (PyCFunction)cp_atom_pack, METH_VARARGS | METH_KEYWORDS },
  { CpAtomType_Unpack,
    (PyCFunction)cp_atom_unpack,
    METH_VARARGS | METH_KEYWORDS },
  { CpAtomType_Type, (PyCFunction)cp_atom_type, METH_NOARGS },
  { CpAtomType_Size, (PyCFunction)cp_atom_size, METH_VARARGS | METH_KEYWORDS },
  { NULL } /* Sentinel */
};

static PyTypeObject CpAtom_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = _Cp_Name(_core.CpAtom),
  .tp_doc = "...",
  .tp_basicsize = sizeof(CpAtom),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_new = cp_atom_new,
  .tp_dealloc = (destructor)cp_atom_dealloc,
  .tp_methods = CpAtom_Methods,
};

// ------------------------------------------------------------------------------
// Invalid default object
// ------------------------------------------------------------------------------
static PyObject*
cp_invaliddefault_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  if (PyTuple_GET_SIZE(args) || PyDict_GET_SIZE(kw)) {
    PyErr_SetString(PyExc_TypeError,
                    "InvalidDefaultType does not accept arguments");
    return NULL;
  }

  Py_INCREF(CP_INVALID_DEFAULT);
  return CP_INVALID_DEFAULT;
}

static PyObject*
cp_invaliddefault_repr(PyObject* self)
{
  return PyUnicode_FromString("<InvalidDefault>");
}

static PyTypeObject CpInvalidDefault_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name =
    _Cp_Name(_core.CpInvalidDefaultType),
  .tp_doc = "...",
  .tp_basicsize = 0,
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = cp_invaliddefault_new,
  .tp_repr = cp_invaliddefault_repr,
};

_Cp_Immortal(_InvalidDefault, CpInvalidDefault_Type);

// ------------------------------------------------------------------------------
// default switch option
// ------------------------------------------------------------------------------
static PyObject*
cp_defaultoption_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  if (PyTuple_GET_SIZE(args) || PyDict_GET_SIZE(kw)) {
    PyErr_SetString(PyExc_TypeError,
                    "InvalidDefaultType does not accept arguments");
    return NULL;
  }

  Py_INCREF(CP_DEFAULT_OPTION);
  return CP_DEFAULT_OPTION;
}

static PyObject*
cp_defaultoption_repr(PyObject* self)
{
  return PyUnicode_FromString("<DefaultSwitchOption>");
}

static PyTypeObject CpDefaultSwitchOption_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name =
    _Cp_Name(_core.CpDefaultSwitchOptionType),
  .tp_doc = "...",
  .tp_basicsize = 0,
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = cp_defaultoption_new,
  .tp_repr = cp_defaultoption_repr,
};

_Cp_Immortal(_DefaultSwitchOption, CpDefaultSwitchOption_Type);

// ------------------------------------------------------------------------------
// CpField
// ------------------------------------------------------------------------------
typedef struct CpField
{
  PyObject_HEAD PyObject* m_atom;
  PyObject* m_name;
  PyObject* m_endian;
  PyObject* m_offset;
  PyObject* m_arch;
  PyObject* m_length;
  PyObject* m_default;
  PyObject* m_switch;
  PyObject* m_options;
  PyObject* m_condition;

  // internal state
  int8_t s_size;
  int8_t s_type;
  int8_t s_sequential;
  int8_t s_keep_pos;
} CpField;

// Public API

static inline int
CpField_HasCondition(CpField* self)
{
  return !Py_IsTrue(self->m_condition);
}

static inline int
CpField_IsEnabled(CpField* self, PyObject* context)
{
  if (self->m_condition == NULL) {
    return true;
  }

  if (PyCallable_Check(self->m_condition)) {
    PyObject* result = CpContext_Call(self->m_condition, context);
    if (result == NULL) {
      return -1;
    }
    int truth = PyObject_IsTrue(result);
    Py_DECREF(result);
    return truth;
  }

  return PyObject_IsTrue(self->m_condition);
}

static inline Py_ssize_t
CpField_GetOffset(CpField* self, PyObject* context)
{
  Py_ssize_t offset = -1;
  if (self->m_offset != NULL) {

    if (PyCallable_Check(self->m_offset)) {
      PyObject* result = CpContext_Call(self->m_offset, context);
      if (result == NULL) {
        return -1;
      }
      offset = PyLong_AsSsize_t(result);
      Py_DECREF(result);
    } else {
      offset = PyLong_AsSsize_t(self->m_offset);
    }
  }
  return offset;
}

static inline PyObject*
CpField_GetSwitchAtom(CpField* self, PyObject* op, PyObject* context)
{
  if (self->m_switch == NULL) {
    PyErr_SetString(PyExc_TypeError, "field does not have a switch");
    return NULL;
  }

  PyObject* result = NULL;
  if (PyCallable_Check(self->m_switch)) {
    result = CpContext_Call(self->m_switch, context);
    if (!result)
      return NULL;
  } else {
    result = PyObject_GetItem(self->m_switch, op);
    if (!result) {
      result = PyObject_GetItem(self->m_switch, CP_INVALID_DEFAULT);
      if (!result)
        return NULL;
    }
  }

  // TODO: check for nested struct
  return result;
}

static inline PyObject*
CpField_GetLength(CpField* self, PyObject* context)
{
  if (self->m_length == NULL) {
    PyErr_SetString(PyExc_TypeError, "field does not have a length");
    return NULL;
  }

  if (PyCallable_Check(self->m_length)) {
    PyObject* result = CpContext_Call(self->m_length, context);
    if (!result)
      return NULL;
    return result;
  }
  return Py_NewRef(self->m_length);
}

static inline int
CpField_Check(PyObject* o)
{
  return o && o->ob_type == &CpField_Type;
}

// end Public API

static PyObject*
cp_field_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpField* self;
  self = (CpField*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->m_name = PyUnicode_FromString("_");
  self->m_atom = NULL;
  self->m_endian = NULL;
  self->m_offset = NULL;
  self->m_arch = NULL;
  self->m_length = NULL;

  Py_XINCREF(CP_INVALID_DEFAULT);
  self->m_default = CP_INVALID_DEFAULT;
  self->m_switch = NULL;
  self->m_options = NULL;
  self->m_condition = Py_NewRef(Py_True);

  // internal state
  self->s_size = false;
  self->s_type = false;
  self->s_sequential = false;
  self->s_keep_pos = false;
  return (PyObject*)self;
}

static void
cp_field_dealloc(CpField* self)
{
  Py_XDECREF(self->m_name);
  Py_XDECREF(self->m_endian);
  Py_XDECREF(self->m_offset);
  Py_XDECREF(self->m_arch);
  Py_XDECREF(self->m_length);
  Py_XDECREF(self->m_default);
  Py_XDECREF(self->m_switch);
  Py_XDECREF(self->m_options);
  Py_XDECREF(self->m_condition);
  Py_XDECREF(self->m_atom);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
cp_field_repr(CpField* self)
{
  return PyUnicode_FromFormat("<CpField %R>", self->m_name);
}

static int
cp_field_set_length(CpField* self, PyObject* value, void* closure);

static int
cp_field_set_offset(CpField* self, PyObject* value, void* closure);

static int
cp_field_init(CpField* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "atom",    "name",      "endian",  "offset",
                            "arch",    "length",    "default", "switch",
                            "options", "condition", NULL };
  PyObject *name = NULL, *endian = NULL, *offset = NULL, *arch = NULL,
           *length = NULL, *default_ = NULL, *switch_ = NULL, *options = NULL,
           *condition = NULL, *atom = NULL;
  if (!PyArg_ParseTupleAndKeywords(args,
                                   kw,
                                   "O|UOOOOOOOO",
                                   kwlist,
                                   &atom,
                                   &name,
                                   &endian,
                                   &offset,
                                   &arch,
                                   &length,
                                   &default_,
                                   &switch_,
                                   &options,
                                   &condition))
    return -1;

  _coremodulestate* state = get_global_core_state();

  _Cp_SetObj(self->m_name, name);
  _Cp_SetObj(self->m_endian, endian);
  _Cp_SetObj(self->m_arch, arch);

  _Cp_SetObj(self->m_default, default_);
  _Cp_SetObj(self->m_switch, switch_);
  _Cp_SetObj(self->m_options, options);
  _Cp_SetObj(self->m_condition, condition);
  _Cp_SetObj(self->m_atom, atom);

  if (!self->m_options) {
    self->m_options = PySet_New(NULL);
    if (!self->m_options)
      return -1;

    if (PySet_Add(self->m_options, state->cp_option__keep_position) < 0) {
      return -1;
    };
  }

  if (!self->m_atom || self->m_atom == Py_None) {
    PyErr_SetString(PyExc_TypeError, "atom is required");
    return -1;
  }

  if (!self->m_arch) {
    _Cp_SetObj(self->m_arch, state->cp_arch__host);
  }
  if (!self->m_endian) {
    _Cp_SetObj(self->m_endian, state->cp_endian__native);
  }

  if (length)
    if (cp_field_set_length(self, length, NULL) < 0)
      return -1;
  if (offset)
    if (cp_field_set_offset(self, offset, NULL) < 0)
      return -1;

  self->s_size = CpAtom_FastHasSize(self->m_atom, state);
  self->s_type = CpAtom_FastHasType(self->m_atom, state);
  return 0;
}

static PyObject*
cp_field_get_length(CpField* self)
{
  return Py_NewRef(self->m_length ? self->m_length : Py_None);
}

static int
cp_field_set_length(CpField* self, PyObject* value, void* closure)
{
  if (!value || value == Py_None ||
      (!PyLong_Check(value) && !PyCallable_Check(value) &&
       !PyObject_IsInstance(value, (PyObject*)&PyEllipsis_Type) &&
       !PyObject_IsInstance(value, (PyObject*)&PySlice_Type))) {
    PyErr_SetString(PyExc_TypeError,
                    "length must be an integer, context lambda or a special "
                    "type");
    return -1;
  }

  _Cp_SetObj(self->m_length, value);
  _coremodulestate* state = get_global_core_state();
  if (PyLong_Check(self->m_length) && PyLong_AsSize_t(self->m_length) <= 1) {
    // remove sequential option automatically
    PySet_Discard(self->m_options, state->cp_option__sequential);
    self->s_sequential = false;
  } else {
    PySet_Add(self->m_options, state->cp_option__sequential);
    self->s_sequential = true;
  }
  return 0;
}

static PyObject*
cp_field_get_offset(CpField* self)
{
  return Py_NewRef(self->m_offset ? self->m_offset : Py_None);
}

static int
cp_field_set_offset(CpField* self, PyObject* value, void* closure)
{
  if (!value || value == Py_None ||
      (!PyLong_Check(value) && !PyCallable_Check(value))) {
    PyErr_SetString(PyExc_TypeError,
                    "offset must be an integer or a context lambda");
    return -1;
  }

  _Cp_SetObj(self->m_offset, value);
  _coremodulestate* state = get_global_core_state();
  if (PyLong_Check(self->m_offset) && PyLong_AsSize_t(self->m_offset) != -1) {
    PySet_Discard(self->m_options, state->cp_option__keep_position);
    self->s_keep_pos = false;
  } else {
    PySet_Add(self->m_options, state->cp_option__keep_position);
    self->s_keep_pos = true;
  }
  return 0;
}

static PyObject*
cp_field_get_switch(CpField* self)
{
  return Py_NewRef(self->m_switch ? self->m_switch : Py_None);
}

static int
cp_field_set_switch(CpField* self, PyObject* value, void* closure)
{
  if (!value || value == Py_None ||
      (!PyCallable_Check(value) && !PyDict_Check(value))) {
    PyErr_SetString(PyExc_TypeError,
                    "switch must be a callable or a dictionary");
    return -1;
  }

  _Cp_SetObj(self->m_switch, value);
  return 0;
}

static PyObject*
cp_field_get_condition(CpField* self)
{
  return Py_NewRef(self->m_condition ? self->m_condition : Py_None);
}

static int
cp_field_set_condition(CpField* self, PyObject* value, void* closure)
{
  if (!value || value == Py_None ||
      (!PyCallable_Check(value) && !PyBool_Check(value))) {
    PyErr_SetString(PyExc_TypeError,
                    "condition must be a callable or a boolean");
    return -1;
  }

  _Cp_SetObj(self->m_condition, value);
  return 0;
}

static PyObject*
cp_field_as_number_matmul(CpField* self, PyObject* other)
{
  if (cp_field_set_offset(self, other, NULL) < 0) {
    return NULL;
  }
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_number_or(CpField* self, PyObject* other)
{
  if (!other || other->ob_type != &CpOption_Type) {
    Py_RETURN_NOTIMPLEMENTED;
  }

  PySet_Add(self->m_options, other);
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_number_xor(CpField* self, PyObject* other)
{
  if (!other || other->ob_type != &CpOption_Type) {
    Py_RETURN_NOTIMPLEMENTED;
  }

  PySet_Discard(self->m_options, other);
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_number_rshift(CpField* self, PyObject* other)
{
  if (cp_field_set_switch(self, other, NULL) < 0) {
    return NULL;
  }
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_number_floordiv(CpField* self, PyObject* other)
{
  if (cp_field_set_condition(self, other, NULL) < 0) {
    return NULL;
  }
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_number_add(CpField* self, PyObject* other)
{
  if (!other || other->ob_type != &CpEndian_Type) {
    Py_RETURN_NOTIMPLEMENTED;
  }
  _Cp_SetObj(self->m_endian, other);
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_mapping_getitem(CpField* self, PyObject* key)
{
  // allow multiple dimensions
  if (cp_field_set_length(self, key, NULL) < 0) {
    return NULL;
  }
  return Py_NewRef((PyObject*)self);
}

static PyMemberDef CpField_Members[] = {
  { "name", T_OBJECT, offsetof(CpField, m_name), 0 },
  { "default", T_OBJECT, offsetof(CpField, m_default), 0 },
  { "options", T_OBJECT, offsetof(CpField, m_options), 0 },
  { "atom", T_OBJECT, offsetof(CpField, m_atom), READONLY },
  { "endian", T_OBJECT, offsetof(CpField, m_endian), 0 },
  { "arch", T_OBJECT, offsetof(CpField, m_arch), 0 },
  { NULL } /* Sentinel */
};

static PyGetSetDef CpField_GetSetters[] = {
  { "length",
    (getter)cp_field_get_length,
    (setter)cp_field_set_length,
    NULL,
    NULL },
  { "offset",
    (getter)cp_field_get_offset,
    (setter)cp_field_set_offset,
    NULL,
    NULL },
  { "switch",
    (getter)cp_field_get_switch,
    (setter)cp_field_set_switch,
    NULL,
    NULL },
  { "condition",
    (getter)cp_field_get_condition,
    (setter)cp_field_set_condition,
    NULL,
    NULL },
  { NULL } /* Sentinel */
};

static PyNumberMethods CpField_NumberMethods = {
  .nb_matrix_multiply = (binaryfunc)cp_field_as_number_matmul,
  .nb_or = (binaryfunc)cp_field_as_number_or,
  .nb_xor = (binaryfunc)cp_field_as_number_xor,
  .nb_rshift = (binaryfunc)cp_field_as_number_rshift,
  .nb_floor_divide = (binaryfunc)cp_field_as_number_floordiv,
  .nb_add = (binaryfunc)cp_field_as_number_add,
};

static PyMappingMethods CpField_MappingMethods = {
  .mp_subscript = (binaryfunc)cp_field_as_mapping_getitem,
};

static PyMethodDef CpField_Methods[] = {
  { "__type__", (PyCFunction)(typefunc)cp_typeof_field, METH_NOARGS },
  { NULL } /* Sentinel */
};

static PyTypeObject CpField_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = _Cp_Name(_core.CpField),
  .tp_doc = "...",
  .tp_basicsize = sizeof(CpField),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_new = cp_field_new,
  .tp_dealloc = (destructor)cp_field_dealloc,
  .tp_init = (initproc)cp_field_init,
  .tp_repr = (reprfunc)cp_field_repr,
  .tp_members = CpField_Members,
  .tp_getset = CpField_GetSetters,
  .tp_as_number = &CpField_NumberMethods,
  .tp_as_mapping = &CpField_MappingMethods,
  .tp_methods = CpField_Methods,
};

// ------------------------------------------------------------------------------
// CpFieldAtom
// ------------------------------------------------------------------------------
typedef struct CpFieldAtom
{
  CpAtom _base;
} CpFieldAtom;

static PyObject*
cp_fieldatom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpFieldAtom* self;
  self = (CpFieldAtom*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;
  return (PyObject*)self;
}

static void
cp_fieldatom_dealloc(CpAtom* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

#define _CpFieldAtom_DefMethod(name, func)                                     \
  static PyObject* cp_fieldatom_##name(CpFieldAtom* self, PyObject* other)     \
  {                                                                            \
    PyObject* field = CpField_New(self);                                       \
    if (!field) {                                                              \
      return NULL;                                                             \
    }                                                                          \
    if (func((CpField*)field, other, NULL) < 0) {                              \
      Py_XDECREF(field);                                                       \
      return NULL;                                                             \
    }                                                                          \
    return field;                                                              \
  }

_CpFieldAtom_DefMethod(as_number_matmul, cp_field_set_offset);
_CpFieldAtom_DefMethod(as_number_floordiv, cp_field_set_condition);
_CpFieldAtom_DefMethod(as_number_rshift, cp_field_set_switch);
_CpFieldAtom_DefMethod(as_mapping_getitem, cp_field_set_length);

#undef _CpFieldAtom_DefMethod

static PyObject*
cp_fieldatom_as_number_add(CpFieldAtom* self, PyObject* other)
{
  if (other->ob_type != &CpEndian_Type) {
    Py_RETURN_NOTIMPLEMENTED;
  }

  CpField* field = (CpField*)CpField_New(self);
  if (!field) {
    return NULL;
  }
  _Cp_SetObj(field->m_endian, other);
  return (PyObject*)field;
}

static PyObject*
cp_fieldatom_as_number_or(CpFieldAtom* self, PyObject* other)
{
  if (other->ob_type != &CpOption_Type) {
    Py_RETURN_NOTIMPLEMENTED;
  }

  CpField* field = (CpField*)CpField_New(self);
  if (!field) {
    return NULL;
  }
  PySet_Add(field->m_options, other);
  return (PyObject*)field;
}

static PyObject*
cp_fieldatom_as_number_xor(CpFieldAtom* self, PyObject* other)
{
  if (other->ob_type != &CpOption_Type) {
    Py_RETURN_NOTIMPLEMENTED;
  }

  CpField* field = (CpField*)CpField_New(self);
  if (!field) {
    return NULL;
  }
  PySet_Discard(field->m_options, other);
  return (PyObject*)field;
}

static PyNumberMethods CpFieldAtom_NumberMethods = {
  .nb_matrix_multiply = (binaryfunc)cp_fieldatom_as_number_matmul,
  .nb_floor_divide = (binaryfunc)cp_fieldatom_as_number_floordiv,
  .nb_add = (binaryfunc)cp_fieldatom_as_number_add,
  .nb_rshift = (binaryfunc)cp_fieldatom_as_number_rshift,
  .nb_or = (binaryfunc)cp_fieldatom_as_number_or,
  .nb_xor = (binaryfunc)cp_fieldatom_as_number_xor,
};

static PyMappingMethods CpFieldAtom_MappingMethods = {
  .mp_subscript = (binaryfunc)cp_fieldatom_as_mapping_getitem,
};

static PyTypeObject CpFieldAtom_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name =
    _Cp_Name(_core.CpFieldAtom),
  .tp_doc = "...",
  .tp_basicsize = sizeof(CpFieldAtom),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_new = cp_fieldatom_new,
  .tp_dealloc = (destructor)cp_fieldatom_dealloc,
  .tp_as_number = &CpFieldAtom_NumberMethods,
  .tp_as_mapping = &CpFieldAtom_MappingMethods,
};

// ------------------------------------------------------------------------------
// CpState
// ------------------------------------------------------------------------------
typedef struct CpState
{
  PyObject_HEAD _coremodulestate* mod;

  // common state variables
  PyObject* m_io;
  PyObject* m_globals;
  PyObject* m_offset_table;

  // context-sensitive variables
  PyObject* m_path;
  PyObject* m_obj;
  PyObject* m_field;
  PyObject* m_value;

  // context-sensitive sequence variables
  PyObject* m_sequence;
  Py_ssize_t m_length;
  Py_ssize_t m_index;

  // context-sensitive state variables
  int8_t s_sequential;
  int8_t s_greedy;

  // raw buffer variables
  char* m_raw_buf;
  Py_ssize_t m_raw_length;
  Py_ssize_t m_raw_offset;
  Py_ssize_t m_raw_alloc_length;

  // io functions
  writefunc m_io_write;
  readfunc m_io_read;
  seekfunc m_io_seek;
  tellfunc m_io_tell;
} CpState;

static inline PyObject*
cp_state_io_tell(struct CpState* self)
{
  return PyObject_CallMethodNoArgs(self->m_io, self->mod->str_tell);
}

static inline PyObject*
cp_state_io_seek(struct CpState* self, PyObject* offset, int whence)
{
  return PyObject_CallMethodObjArgs(
    self->m_io, self->mod->str_seek, "Oi", offset, whence);
}

static inline PyObject*
cp_state_io_read(struct CpState* self, Py_ssize_t size)
{
  PyObject* sizeobj = PyLong_FromSsize_t(size);
  PyObject* res =
    PyObject_CallMethodOneArg(self->m_io, self->mod->str_read, sizeobj);
  Py_DECREF(sizeobj);
  return res;
}

static inline PyObject*
cp_state_io_write(struct CpState* self, PyObject* value)
{
  return PyObject_CallMethodOneArg(self->m_io, self->mod->str_write, value);
}

static PyObject*
cp_state_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpState* self = (CpState*)type->tp_alloc(type, 0);
  if (!self) {
    return NULL;
  }
  self->mod = get_global_core_state();
  self->m_io = NULL;
  self->m_globals = CpContext_NewEmpty();
  self->m_offset_table = PyDict_New();
  self->m_path = NULL;
  self->m_obj = NULL;
  self->m_field = NULL;
  self->m_index = 0;
  self->m_value = NULL;
  self->m_length = 0;
  self->s_sequential = false;
  self->s_greedy = false;
  self->m_raw_buf = NULL;
  self->m_raw_length = 0;
  self->m_raw_alloc_length = 0;
  self->m_sequence = NULL;
  self->m_io_write = (writefunc)&cp_state_io_write;
  self->m_io_read = (readfunc)&cp_state_io_read;
  self->m_io_seek = (seekfunc)&cp_state_io_seek;
  self->m_io_tell = (tellfunc)&cp_state_io_tell;
  return (PyObject*)self;
}

static void
cp_state_dealloc(CpState* self)
{
  Py_CLEAR(self->m_io);
  Py_CLEAR(self->m_globals);
  Py_CLEAR(self->m_offset_table);
  Py_CLEAR(self->m_path);
  Py_CLEAR(self->m_obj);
  Py_CLEAR(self->m_field);
  Py_CLEAR(self->m_value);
  Py_CLEAR(self->m_sequence);
  self->m_length = 0;
  self->m_index = 0;
  self->m_raw_buf = NULL;
  self->m_raw_length = 0;
  self->m_raw_alloc_length = 0;
  self->mod = NULL;
  self->m_io_write = NULL;
  self->m_io_read = NULL;
  self->m_io_seek = NULL;
  self->m_io_tell = NULL;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_state_set_globals(CpState* self, PyObject* globals, void*);

static int
cp_state_set_offset_table(CpState* self, PyObject* offset_table, void*);

static int
cp_state_init(CpState* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "io",     "globals", "offset_table", "path",
                            "obj",    "field",   "index",        "value",
                            "length", "greedy",  "sequence",     NULL };
  PyObject *io = NULL, *globals = NULL, *offset_table = NULL,
           *path = self->mod->str_ctx__root, *obj = NULL, *field = NULL,
           *value = NULL, *sequence = NULL;
  int8_t greedy = false;
  Py_ssize_t index = 0, length = 0;
  if (!PyArg_ParseTupleAndKeywords(args,
                                   kw,
                                   "|OOOOOOnOnpOp",
                                   kwlist,
                                   &io,
                                   &globals,
                                   &offset_table,
                                   &path,
                                   &obj,
                                   &field,
                                   &index,
                                   &value,
                                   &length,
                                   &greedy,
                                   &sequence)) {
    return -1;
  }

  if (!io) {
    PyErr_SetString(PyExc_ValueError, "io is NULL!");
    return -1;
  }
  _Cp_SetObj(self->m_io, io);
  if (globals)
    if (cp_state_set_globals(self, globals, NULL) < 0)
      return -1;

  if (offset_table)
    if (cp_state_set_offset_table(self, offset_table, NULL) < 0) {
      return -1;
    }

  _Cp_SetObj(self->m_path, path);
  _Cp_SetObj(self->m_obj, obj);
  _Cp_SetObj(self->m_field, field);
  _Cp_SetObj(self->m_value, value);
  _Cp_SetObj(self->m_sequence, sequence);
  self->s_greedy = greedy;
  self->m_index = index;
  self->m_length = length;
  self->s_sequential = greedy || length > 0;
  return 0;
}

static int
cp_state_set_globals(CpState* self, PyObject* globals, void* unused)
{
  if (!globals) {
    PyErr_SetString(PyExc_ValueError, "globals is NULL!");
    return -1;
  }

  if (PyObject_IsInstance(globals, (PyObject*)&CpContext_Type)) {
    _Cp_SetObj(self->m_globals, globals);
  } else {
    if (!PyMapping_Check(globals)) {
      PyErr_SetString(PyExc_TypeError, "globals must be a mapping");
      return -1;
    }
    self->m_globals = CpContext_New(globals);
  }
  return 0;
}

static PyObject*
cp_state_get_globals(CpState* self)
{
  return Py_NewRef(self->m_globals ? self->m_globals : Py_None);
}

static int
cp_state_set_offset_table(CpState* self, PyObject* offset_table, void* unused)
{
  if (!offset_table) {
    PyErr_SetString(PyExc_ValueError, "offset_table is NULL!");
    return -1;
  }
  if (!PyMapping_Check(offset_table)) {
    PyErr_SetString(PyExc_TypeError, "offset_table must be a mapping");
    return -1;
  }
  _Cp_SetObj(self->m_offset_table, offset_table);
  return 0;
}

static PyObject*
cp_state_get_offset_table(CpState* self)
{
  return Py_NewRef(self->m_offset_table ? self->m_offset_table : Py_None);
}

static PyObject*
cp_state__context_getattr__(CpState* self, PyObject* args)
{
  PyObject *result = NULL, *tmp = NULL;
  char* line;
  if (!PyArg_ParseTuple(args, "s", &line)) {
    return NULL;
  }

  char* token = strtok(line, ".");
  if (token == NULL) {
    PyErr_Format(PyExc_AttributeError, "CpState has no attribute '%s'", line);
    return NULL;
  }

  PyObject* key = PyUnicode_FromString(token);
  if (!key) {
    return NULL;
  }
  result = PyObject_GenericGetAttr((PyObject*)self, key);
  Py_DECREF(key);
  while (result != NULL && (token = strtok(NULL, ".")) != NULL) {
    tmp = PyObject_GetAttrString(result, token);
    Py_XSETREF(result, tmp);
  };

  if (result == NULL) {
    PyErr_Format(
      PyExc_AttributeError, "'%s' has no attribute '%s'", token, line);
    return NULL;
  }
  return result;
}

static PyObject*
cp_state_write(CpState* self, PyObject* args)
{
  PyObject* value = NULL;
  if (!PyArg_ParseTuple(args, "O", &value)) {
    return NULL;
  }
  return cp_state_io_write(self, value);
}

static PyObject*
cp_state_read(CpState* self, PyObject* args)
{
  Py_ssize_t size = 0;
  if (!PyArg_ParseTuple(args, "n", &size)) {
    return NULL;
  }
  return cp_state_io_read(self, size);
}

static PyObject*
cp_state_tell(CpState* self)
{
  return cp_state_io_tell(self);
}

static PyObject*
cp_state_seek(CpState* self, PyObject* args)
{
  PyObject* offset = NULL;
  int whence = 0;
  if (!PyArg_ParseTuple(args, "O|i", &offset, &whence)) {
    return NULL;
  }
  return cp_state_io_seek(self, offset, whence);
}

static PyGetSetDef CpState_GetSetters[] = {
  { "globals",
    (getter)cp_state_get_globals,
    (setter)cp_state_set_globals,
    NULL,
    NULL },
  { "offset_table",
    (getter)cp_state_get_offset_table,
    (setter)cp_state_set_offset_table,
    NULL,
    NULL },
  { NULL },
};

static PyMemberDef CpState_Members[] = {
  { "io", T_OBJECT, offsetof(CpState, m_io), 0, NULL },
  { "path", T_OBJECT, offsetof(CpState, m_path), 0, NULL },
  { "obj", T_OBJECT_EX, offsetof(CpState, m_obj), 0, NULL },
  { "field", T_OBJECT_EX, offsetof(CpState, m_field), 0, NULL },
  { "value", T_OBJECT_EX, offsetof(CpState, m_value), READONLY, NULL },
  { "index", T_INT, offsetof(CpState, m_index), READONLY, NULL },
  { "length", T_INT, offsetof(CpState, m_length), READONLY, NULL },
  { "sequential", T_BOOL, offsetof(CpState, s_sequential), 0, NULL },
  { "greedy", T_BOOL, offsetof(CpState, s_greedy), 0, NULL },
  { "sequence", T_OBJECT_EX, offsetof(CpState, m_sequence), 0, NULL },
  { NULL } /* Sentinel */
};

static PyMethodDef CpState_Methods[] = {
  { "write", (PyCFunction)cp_state_write, METH_VARARGS },
  { "read", (PyCFunction)cp_state_read, METH_VARARGS },
  { "tell", (PyCFunction)cp_state_tell, METH_NOARGS },
  { "seek", (PyCFunction)cp_state_seek, METH_VARARGS },
  { CpContext_GetAttr, (PyCFunction)cp_state__context_getattr__, METH_VARARGS },
  { NULL } /* Sentinel */
};

static PyTypeObject CpState_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = _Cp_Name(_core.CpState),
  .tp_doc = "...",
  .tp_basicsize = sizeof(CpState),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_new = cp_state_new,
  .tp_dealloc = (destructor)cp_state_dealloc,
  .tp_getset = CpState_GetSetters,
  .tp_members = CpState_Members,
  .tp_init = (initproc)cp_state_init,
  .tp_methods = CpState_Methods,
};

// ------------------------------------------------------------------------------
// CpStructFieldInfo
// ------------------------------------------------------------------------------
typedef struct CpStructFieldInfo
{
  PyObject_HEAD CpField* m_field;

  // Excluded: True if the field is included in the struct
  int8_t s_excluded;

  // TODO: here's space for more settings
} CpStructFieldInfo;

static PyObject*
cp_struct_fieldinfo_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpStructFieldInfo* self = (CpStructFieldInfo*)type->tp_alloc(type, 0);
  if (!self) {
    return NULL;
  }
  self->m_field = NULL;
  self->s_excluded = false;
  return (PyObject*)self;
}

static void
cp_struct_fieldinfo_dealloc(CpStructFieldInfo* self)
{
  Py_XDECREF(self->m_field);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_struct_fieldinfo_init(CpStructFieldInfo* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "field", "excluded", NULL };
  PyObject* field = NULL;
  int8_t excluded = false;

  if (!PyArg_ParseTupleAndKeywords(
        args, kw, "O|p", kwlist, &field, &excluded)) {
    return -1;
  }

  if (!field) {
    PyErr_SetString(PyExc_ValueError, "field is NULL!");
    return -1;
  }

  PyObject* o = Py_XNewRef(field);
  Py_XSETREF(self->m_field, (CpField*)(o));
  self->s_excluded = excluded;
  return 0;
}

static PyObject*
cp_struct_fieldinfo_repr(CpStructFieldInfo* self)
{
  return PyUnicode_FromFormat("<CpStructFieldInfo of %R>",
                              self->m_field->m_name);
}

static PyMemberDef CpStructFieldInfo_Members[] = {
  { "field", T_OBJECT, offsetof(CpStructFieldInfo, m_field), READONLY, NULL },
  { "excluded",
    T_BOOL,
    offsetof(CpStructFieldInfo, s_excluded),
    READONLY,
    NULL },
  { NULL } /* Sentinel */
};

static PyTypeObject CpStructFieldInfo_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name =
    _Cp_Name(_core.CpStructFieldInfo),
  .tp_doc = "...",
  .tp_basicsize = sizeof(CpStructFieldInfo),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = cp_struct_fieldinfo_new,
  .tp_dealloc = (destructor)cp_struct_fieldinfo_dealloc,
  .tp_init = (initproc)cp_struct_fieldinfo_init,
  .tp_repr = (reprfunc)cp_struct_fieldinfo_repr,
  .tp_members = CpStructFieldInfo_Members,
};

// ------------------------------------------------------------------------------
// CpStruct
// ------------------------------------------------------------------------------
typedef struct CpStruct
{
  PyObject_HEAD PyTypeObject* m_model; // underlying class

  PyObject* m_members; // Dict[str, FieldInfo]
  PyObject* m_options; // set[CpOption]

  PyObject* m_endian;
  PyObject* m_arch;
  PyObject* m_field_options;

  // internal states
  int8_t s_union;
  int8_t s_kwonly;
  PyObject* s_std_init_fields;    // list[FieldInfo]
  PyObject* s_kwonly_init_fields; // list[FieldInfo]

  _coremodulestate* s_mod;
} CpStruct;

// Public API

static inline PyObject*
CpStruct_GetMethodResolutionOrder(CpStruct* self)
{
  // state is optional
  return PyObject_GetAttr((PyObject*)self->m_model, self->s_mod->str___mro__);
}

static PyObject*
CpStruct_GetReverseMRO(CpStruct* self)
{
  PyObject *mro = CpStruct_GetMethodResolutionOrder(self), *start = NULL,
           *stop = NULL, *step = NULL, *slice = NULL, *result = NULL;
  if (!mro) {
    return NULL;
  }

  start = PyLong_FromSsize_t(-1), stop = PyLong_FromSsize_t(0),
  step = PyLong_FromSsize_t(-1);
  if (!start || !stop || !step) {
    goto cleanup;
  }

  slice = PySlice_New(start, stop, step);
  if (!slice) {
    goto cleanup;
  }

  result = PyObject_GetItem(mro, slice);
cleanup:
  Py_XDECREF(start);
  Py_XDECREF(stop);
  Py_XDECREF(step);
  Py_XDECREF(slice);
  Py_XDECREF(mro);
  return result;
}

static int
CpStruct_AddFieldInfo(CpStruct* o, CpStructFieldInfo* info)
{
  if (!info) {
    PyErr_SetString(PyExc_TypeError, "info must be a set");
    return -1;
  }

  CpField* field = info->m_field;
  if (PyMapping_HasKey(o->m_members, field->m_name)) {
    PyErr_Format(
      PyExc_ValueError, "field with name %R already exists", field->m_name);
    return -1;
  }

  if (!info->s_excluded) {
    PyObject* list = Cp_IsInvalidDefault(field->m_default)
                       ? o->s_std_init_fields
                       : o->s_kwonly_init_fields;

    if (PyList_Append(list, (PyObject*)info) < 0) {
      return -1;
    }
  }
  return PyObject_SetItem(o->m_members, field->m_name, (PyObject*)info);
}

static int
CpStruct_AddField(CpStruct* o, CpField* field, int exclude)
{
  if (!field) {
    PyErr_SetString(PyExc_TypeError, "field must be a Field");
    return -1;
  }

  CpStructFieldInfo* info =
    (CpStructFieldInfo*)CpObject_Create(&CpStructFieldInfo_Type, "O", field);
  if (!info) {
    return -1;
  }
  info->s_excluded = exclude;
  int res = CpStruct_AddFieldInfo(o, info);
  Py_XDECREF(info);
  return res;
}

static inline int
CpStruct_ModelSetDefault(CpStruct* o, PyObject* name, PyObject* value)
{
  if (!name) {
    PyErr_SetString(PyExc_TypeError, "name must be a string");
    return -1;
  }

  return PyObject_SetAttr((PyObject*)o->m_model, name, value);
}

static PyObject*
CpStruct_GetAnnotations(CpStruct* o, int eval)
{
  PyObject* args = Py_BuildValue("(O)", o->m_model);
  if (!args) {
    return NULL;
  }

  PyObject* kwargs = Py_BuildValue("{s:i}", "eval_str", eval);
  if (!kwargs) {
    Py_DECREF(args);
    return NULL;
  }
  PyObject* result =
    PyObject_Call((PyObject*)o->s_mod->inspect_getannotations, args, kwargs);
  Py_XDECREF(args);
  Py_XDECREF(kwargs);
  return result;
}

static int
CpStruct_ReplaceType(CpStruct* o, PyObject* name, PyObject* type)
{
  if (!name) {
    PyErr_SetString(PyExc_TypeError, "name must be a string");
    return -1;
  }
  // We have to use direct attribute access here as inspect copies the
  // dictionary before returning.
  PyObject* annotations =
    PyObject_GetAttr((PyObject*)o->m_model, o->s_mod->str___annotations__);
  if (!annotations) {
    return -1;
  }

  if (PyDict_SetItem(annotations, name, type) < 0) {
    Py_DECREF(annotations);
    return -1;
  }
  Py_XDECREF(annotations);
  return 0;
}

static inline PyObject*
CpStruct_GetValue(CpStruct* o, PyObject* instance, PyObject* name)
{
  PyObject* value = PyObject_GetAttr(instance, name);
  if (!value) {
    PyErr_Clear();
    return Py_NewRef(Py_None);
  }
  return value;
}

static inline PyObject*
CpStruct_GetDefaultValue(CpStruct* o, PyObject* name)
{
  PyObject* value = PyObject_GetAttr((PyObject*)o->m_model, name);
  if (!value) {
    PyErr_Clear();
    return Py_NewRef(CP_INVALID_DEFAULT);
  }
  return value;
}

static inline PyObject*
CpStruct_New(PyObject* model)
{
  return CpObject_Create(&CpStruct_Type, "O", model);
}

static inline PyObject*
CpStruct_GetStruct(PyObject* model, _coremodulestate* state)
{
  if (!state) {
    return PyObject_GetAttrString(model, CpType_Struct);
  } else {
    return PyObject_GetAttr(model, state->str___struct__);
  }
}

static inline int
CpStruct_CheckModel(PyObject* model, _coremodulestate* state)
{
  return model && PyObject_HasAttr(model, state->str___struct__);
}

// end Public API

static PyObject*
cp_struct_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpStruct* self = (CpStruct*)type->tp_alloc(type, 0);
  if (!self) {
    return NULL;
  }
  self->m_model = NULL;
  self->m_options = NULL;
  self->m_members = NULL;
  self->s_union = false;
  self->s_kwonly = false;
  self->s_mod = get_global_core_state();
  self->m_endian = Py_NewRef(self->s_mod->cp_endian__native);
  self->m_arch = Py_NewRef(self->s_mod->cp_arch__host);
  self->m_field_options = PySet_New(NULL);
  if (!self->m_field_options) {
    return NULL;
  }
  self->s_kwonly_init_fields = PyList_New(0);
  if (!self->s_kwonly_init_fields) {
    return NULL;
  }
  self->s_std_init_fields = PyList_New(0);
  if (!self->s_std_init_fields) {
    return NULL;
  }
  return (PyObject*)self;
}

static void
cp_struct_dealloc(CpStruct* self)
{
  Py_XDECREF(self->m_model);
  Py_XDECREF(self->m_options);
  Py_XDECREF(self->m_members);
  Py_XDECREF(self->m_endian);
  Py_XDECREF(self->m_arch);
  Py_XDECREF(self->m_field_options);
  Py_XDECREF(self->s_kwonly_init_fields);
  Py_XDECREF(self->s_std_init_fields);
  self->s_kwonly = false;
  self->s_mod = NULL;
  self->s_union = false;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_struct_prepare(CpStruct* self);

static int
cp_struct_import_bases(CpStruct* self);

static int
cp_struct_process_annotation(CpStruct* self,
                             PyObject* name,
                             PyObject* annotation,
                             PyObject* default_value,
                             int exclude);

static int
cp_struct_create_type(CpStruct* self);

static int
cp_struct_init(CpStruct* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "model", "options",       "endian",
                            "arch",  "field_options", NULL };
  PyObject *model = NULL, *options = NULL, *endian = NULL, *arch = NULL,
           *field_options = NULL;
  if (!PyArg_ParseTupleAndKeywords(args,
                                   kw,
                                   "O|OOOO",
                                   kwlist,
                                   &model,
                                   &options,
                                   &endian,
                                   &arch,
                                   &field_options)) {
    return -1;
  }

  if (!model || !PyType_Check(model)) {
    PyErr_SetString(PyExc_TypeError, "model must be a type");
    return -1;
  }

  if (CpStruct_CheckModel(model, self->s_mod)) {
    PyErr_SetString(PyExc_TypeError, "model must not be a struct container");
    return -1;
  }

  Py_XSETREF(self->m_model, (PyTypeObject*)Py_NewRef(model));
  _Cp_SetObj(self->m_options, options) else
  {
    self->m_options = PySet_New(NULL);
    if (!self->m_options) {
      return -1;
    }
  }
  if (_PySet_Update(self->m_options,
                    self->s_mod->cp_option__global_struct_options) < 0) {
    return -1;
  };

  self->s_union =
    PySet_Contains(self->m_options, self->s_mod->cp_option__union);

  self->m_members = PyDict_New();
  if (!self->m_members) {
    return -1;
  }

  _Cp_SetObj(self->m_endian, endian);
  _Cp_SetObj(self->m_arch, arch);
  _Cp_SetObj(self->m_field_options, field_options);
  return cp_struct_prepare(self);
}

static int
cp_struct_prepare(CpStruct* self)
{
  // Generic struct implementation:
  // 1. Process all base classes and import fields from them. All fields
  //    means that that also "excluded" fields will be imported to this
  //    object.
  //
  // 2. Process all annotations from the given model. The annotations will
  //    be evaluated first by the *inspect* module and then copied to get
  //    converted to CpField instances.
  //
  // 3. The third and last step involves the tricky part about native type
  //    creation. It will add "__slots__" if desired and create a new class
  //    based on the current with the same fields and same base classes.
  _coremodulestate* state = self->s_mod;
  int res = 0, had_default = false;

  // First, create a set[str] that will store all field names that won't be
  // visible in the final class but are used in the struct representation.
  //
  // Fields of this category are: unnamed fields and constant fields (if
  // the according option allows to discard them).
  PyObject* discardable = PySet_New(NULL);
  if (!discardable) {
    return -1;
  }

  // As described in step (1), we first import fields from base classes that
  // themselfs store a struct instance (conforming to the StructContainer
  // protocol).
  res = cp_struct_import_bases(self);
  if (res < 0) {
    return -1;
  }

  // As described in step (2), we then import all annotations from the
  // model. Before that, we need to check whether to evaluate the
  // placed annotations.
  int eval = PySet_Contains(self->m_options, state->cp_option__eval);
  if (eval < 0) {
    return -1;
  }
  PyObject *model_annotations = CpStruct_GetAnnotations(self, eval),
           *name = NULL, *annotation = NULL;
  if (!model_annotations) {
    return -1;
  }

  // The structure of a class annotation may be as follows:
  //
  //  class Format:
  //    [ with <condition>: ]
  //        <name>: <type> [ = <default> ]
  //
  // Where <type> can be any object conforming to the Atom protocol, or a
  // special variant of:
  //
  //  - Any type conforming to the StructContainer protocol
  //  - Constants: str, bytes
  //  - Callables that conform to the ContextLambda protocol
  //  - Enum types
  //
  // More detailed information on how each annotation is processed can be
  // found in the cp_struct_process_annotation().
  Py_ssize_t pos = 0;
  while ((res = PyDict_Next(model_annotations, &pos, &name, &annotation))) {
    if (res < 0) {
      return -1;
    }
    PyObject *default_ = NULL, *atom = annotation;
    int excluded = false;

    default_ = CpStruct_GetDefaultValue(self, name);
    if (!default_) {
      Py_XDECREF(discardable);
      return -1;
    }
    // Constant values that are not in the form of fields. A special case are
    // definitions using the 'Const' class for example.
    if (CpField_Check(annotation)) {
      atom = annotation;
      // SPECIAL CASE: If the field has a condition linked to it, a default
      // value of None is inferred.
      if (CpField_HasCondition((CpField*)annotation) &&
          Cp_IsInvalidDefault(default_)) {
        _Cp_SetObj(default_, Py_None);
      }
    }

    // SPECIAL CASE: If this struct is a union, we will infer None as the
    // default value (if none has been set already)
    if (self->s_union && Cp_IsInvalidDefault(default_)) {
      _Cp_SetObj(default_, Py_None);
    }

    if (!Cp_IsInvalidDefault(default_)) {
      had_default = true;
    } else {
      if (had_default) {
        // By default, we allow definitions of classes with positional
        // arguments. That feature will be disabled if a non-default
        // field definition follows a field with a default value.
        self->s_kwonly = true;
      }
    }

    // Next, we check whether the field should be excluded from the
    // final model type.
    if ((res = PySet_Contains(self->m_options,
                              state->cp_option__discard_unnamed))) {
      if (res < 0) {
        Py_XDECREF(default_);
        Py_XDECREF(discardable);
        return -1;
      }
      // Definition 'unnamed fields':
      // Unnamed fields refer to fields in a struct or sequence which names
      // begin with an underscore followed by zero or more numeric digits.
      PyObject* match_ = PyObject_CallMethodObjArgs(
        state->cp_regex__unnamed, state->str_pattern_match, name, NULL);
      if (!match_) {
        Py_XDECREF(default_);
        Py_XDECREF(discardable);
        return -1;
      }
      if (!Py_IsNone(match_)) {
        excluded = true;
      }
      Py_XDECREF(match_);
    } else
      excluded = false;

    if (excluded) {
      PySet_Add(discardable, name);
    }

    res =
      cp_struct_process_annotation(self, name, annotation, default_, excluded);
    Py_XSETREF(default_, NULL);
    if (res < 0) {
      Py_XDECREF(discardable);
      return -1;
    }
  }

  // before we create the new type, discard all marked fields
  PyObject* annotations =
    PyObject_GetAttr((PyObject*)self->m_model, state->str___annotations__);
  if (!annotations) {
    Py_XDECREF(discardable);
    return -1;
  }

  PyObject* iter = PyObject_GetIter(discardable);
  if (!iter) {
    Py_XDECREF(discardable);
    Py_XDECREF(annotations);
    return -1;
  }

  PyObject* item = NULL;
  while ((item = PyIter_Next(iter))) {
    if (PyDict_DelItem(annotations, item)) {
      Py_XDECREF(discardable);
      Py_XDECREF(annotations);
      return -1;
    }
  }

  Py_DECREF(iter);
  Py_DECREF(discardable);
  Py_DECREF(annotations);
  return cp_struct_create_type(self);
}

static int
cp_struct_import_bases(CpStruct* self)
{
  // We will inspect all base classes in reverse order and selectively
  // utilize classes that store a struct instance.
  PyObject* bases = CpStruct_GetReverseMRO(self);
  if (!bases) {
    return -1;
  }

  // All object references here are borrowed.
  PyObject *base = NULL, *field = NULL, *name = NULL;
  CpStruct* struct_ = NULL;
  Py_ssize_t bases_length = PyTuple_GET_SIZE(bases);
  for (Py_ssize_t i = 0; i < bases_length; i++) {
    // For simplicity, we will discard all invalid base classes
    // that can't be displayed as types, e.g. partial template
    // types.
    base = PyTuple_GetItem(bases, i);
    if (!PyType_Check(base)) {
      continue;
    }

    if (!CpStruct_CheckModel(base, self->s_mod)) {
      continue;
    }

    // NOTE:
    // Importing all fields instead of the entire struct here. This
    // action will just add fields to this object using the order of
    // the given struct.
    struct_ = (CpStruct*)CpStruct_GetStruct(base, self->s_mod);
    if (!struct_) {
      return -1;
    }

    while (PyDict_Next(struct_->m_members, NULL, &name, &field)) {
      // The check for duplicates is done in the called function.
      if (CpStruct_AddFieldInfo(self, (CpStructFieldInfo*)field) < 0) {
        Py_XDECREF(struct_);
        return -1;
      }
    }
    Py_XDECREF(struct_);
  }
  return 0;
}

static int
cp_struct_process_annotation(CpStruct* self,
                             PyObject* name,
                             PyObject* annotation,
                             PyObject* default_value,
                             int exclude)
{
  // As described before in cp_struct_prepare, a field definition follows
  // the following schema:
  //
  //    <name>: <annotation> [ = <default> ]
  //
  // Where the name is a string, the annotation is an object conforming that
  // is convertible to a CpField object, and the default value can be any
  // object.
  // It is worthwhile to note that the default value specified here will be
  // assigned to the created field instance. There is no destinction between
  // class-level defaults and field-level defaults.
  CpField* field = NULL;
  _coremodulestate* state = self->s_mod;

  MATCH
  {
    // 1. Annotated field:
    // The annotation is already a CpField object, so we don't need to convert
    // it. Note thate we check against the *exact* type, which means that we
    // will not accept any subclass of CpField.
    CASE_EXACT(&CpField_Type, annotation)
    {
      field = (CpField*)Py_NewRef(annotation);
    }

    // 2. Atom object
    // The annotation is an instance of a subclass of the CpAtom class OR it
    // conforms to the Atom protocol (next branch).
    else CASE(&CpAtom_Type, annotation)
    {
      field = (CpField*)CpField_New(annotation);
      if (!field) {
        return -1;
      }
    }

    // 3. Atom protocol
    // The annotation conforms to the Atom protocol. Note that we check here
    // only against packing, unpacking and size calculation. The type function
    // is optional and won't be covered here.
    else CASE_COND(CpAtom_Check(annotation))
    {
      field = (CpField*)CpField_New(annotation);
      if (!field) {
        return -1;
      }
    }

    // 5. Type
    // Here, the annotation may be a custom struct type or an enum type.
    // Currently, only struct container are supported.
    else CASE_COND(PyType_Check(annotation))
    {
      if (CpStruct_CheckModel(annotation, state)) {
        PyObject* struct_ = CpStruct_GetStruct(annotation, state);
        if (!struct_) {
          return -1;
        }
        field = (CpField*)CpField_New(struct_);
        Py_XDECREF(struct_);
        if (!field) {
          return -1;
        }
      }
    }

    // 4. Callable
    // The annotation is a callable object and conforms to the ContextLambda
    // protocol. Note that we assume the right function signature.
    else CASE_COND(PyCallable_Check(annotation))
    {
      field = (CpField*)CpField_New(annotation);
      if (!field) {
        return -1;
      }
    }
  }

  // Currently, there is no extension support for other types. That is
  // a future feature.
  if (!field) {
    PyErr_Format(
      PyExc_ValueError,
      ("Field %R could not be created, because the placed annotation does not "
       "conform to any of the supported types.\n"
       "annotation: %R"),
      name,
      annotation);
    return -1;
  }

  _Cp_SetObj(field->m_arch, self->m_arch);
  _Cp_SetObj(field->m_endian, self->m_endian);
  _Cp_SetObj(field->m_default, default_value);
  _Cp_SetObj(field->m_name, name);
  if (_PySet_Update(field->m_options, self->m_field_options) < 0) {
    Py_XDECREF(field);
    return -1;
  }

  int res = CpStruct_AddField(self, field, exclude);
  if (res < 0) {
    Py_XDECREF(field);
    return -1;
  }

  // Lastly, we replace the field from the internal model type if it
  // is enabled.
  res = PySet_Contains(self->m_options, state->cp_option__replace_types);
  if (res < 0) {
    Py_XDECREF(field);
    return -1;
  }

  if (res) {
    PyObject* type = cp_typeof_field(field);
    if (!type) {
      Py_XDECREF(field);
      return -1;
    }

    if (CpStruct_ReplaceType(self, name, type) < 0) {
      Py_XDECREF(type);
      Py_XDECREF(field);
      return -1;
    }
    Py_XDECREF(type);
  }

  Py_XDECREF(field);
  return res;
}

static int
_cp_struct_model__init__(PyObject* self, PyObject* args, PyObject* kwnames)
{
  CpStruct* struct_ = (CpStruct*)CpStruct_GetStruct(self, NULL);
  if (!struct_) {
    return NULL;
  }

  CpStructFieldInfo* info = NULL;
  PyObject *key = NULL, *value = NULL;
  Py_ssize_t pos = 0, argc = PyTuple_Size(args),
             stdc = PyList_Size(struct_->s_std_init_fields),
             kwonlyc = PyList_Size(struct_->s_kwonly_init_fields);

  // First, we will iterate over all positional arguments.
  for (Py_ssize_t i = 0; i < stdc; i++) {
    // NOTE here: borrowed reference
    info = (CpStructFieldInfo*)PyList_GetItem(struct_->s_std_init_fields, i);
    if (!info) {
      return -1;
    }

    if (i >= argc) {
      // If the current positional field is defined as a keyword argument,
      // we should retrieve it from the keyword arguments.
      if (!kwnames || !PyDict_Contains(kwnames, info->m_field->m_name)) {
        Py_DECREF(struct_);
        PyErr_Format(PyExc_ValueError,
                     ("Missing argument for positional field %R"),
                     info->m_field->m_name);
        return -1;
      }

      value = PyDict_GetItem(kwnames, info->m_field->m_name);
    } else
      value = PyTuple_GetItem(args, i);

    if (!value) {
      Py_DECREF(struct_);
      return -1;
    }

    // as we store a borrowed reference in 'value', we don't need
    // to decref it.
    if (PyObject_SetAttr(self, info->m_field->m_name, value) < 0) {
      Py_DECREF(struct_);
      return -1;
    }
  }

  // If no keyword arguments were provided, we are still not done, because
  // default values have to be placed.
  for (Py_ssize_t i = 0; i < kwonlyc; i++) {
    // NOTE here: borrowed reference
    info = (CpStructFieldInfo*)PyList_GetItem(struct_->s_kwonly_init_fields, i);
    if (!info) {
      Py_DECREF(struct_);
      return -1;
    }

    // A custom value is only provided if it is in the given keyword
    // arguments.
    if (!kwnames || !PyDict_Contains(kwnames, info->m_field->m_name)) {
      value = info->m_field->m_default;
    } else {
      value = PyDict_GetItem(kwnames, info->m_field->m_name);
    }

    if (!value) {
      Py_DECREF(struct_);
      return -1;
    }

    // same as before, we don't need to decref the value
    if (PyObject_SetAttr(self, info->m_field->m_name, value) < 0) {
      Py_DECREF(struct_);
      return -1;
    }
  }

  Py_DECREF(struct_);
  return 0;
}

static int
cp_struct_create_type(CpStruct* self)
{
  // At this point, we've already processed all annotated elements
  // of our model. Only if S_SLOTS is enabled, we have to create
  // a new type. Otherwise, we simply create __match_args__
  // and replace the __init__ attribute.
  //
  // TODO: Add support for S_SLOTS
  _coremodulestate* state = self->s_mod;
  PyObject* dict = self->m_model->tp_dict;
  if (!dict) {
    return -1;
  }

  // Before modifying the actual type, make sure, the struct is
  // stored in the target model.
  if (PyDict_SetItem(dict, state->str___struct__, (PyObject*)self) < 0) {
    return -1;
  }

  self->m_model->tp_init = (initproc)_cp_struct_model__init__;
  return 0;
}

static PyObject*
cp_struct_repr(CpStruct* self)
{
  return PyUnicode_FromFormat("<CpStruct of '%s'>", self->m_model->tp_name);
}

static PyMemberDef CpStruct_Members[] = {
  { "model", T_OBJECT, offsetof(CpStruct, m_model), READONLY, NULL },
  { "members", T_OBJECT, offsetof(CpStruct, m_members), READONLY, NULL },
  { "options", T_OBJECT, offsetof(CpStruct, m_options), 0, NULL },
  { NULL } /* Sentinel */
};

static PyTypeObject CpStruct_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = _Cp_Name(_core.CpStruct),
  .tp_doc = "...",
  .tp_basicsize = sizeof(CpStruct),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = (newfunc)cp_struct_new,
  .tp_dealloc = (destructor)cp_struct_dealloc,
  .tp_init = (initproc)cp_struct_init,
  .tp_members = CpStruct_Members,
  .tp_repr = (reprfunc)cp_struct_repr,
};

// ------------------------------------------------------------------------------
// pack
// ------------------------------------------------------------------------------

static int
cp_pack_field(PyObject* op, CpField* field, CpState* state)
{
  // we can assert that all provided objects are of the correct type
  PyObject* path = PyUnicode_FromFormat("%s.%s", state->m_path, field->m_name);
  if (!path) {
    return -1;
  }
  Py_XSETREF(state->m_path, path);

  int res = CpField_IsEnabled(field, (PyObject*)state);
  if (!res) {
    // disabled fields are not packed
    return 0;
  }
  if (res < 0) {
    return -1;
  }

  PyObject *base_stream = NULL, *fallback = NULL;

  state->m_field = (PyObject*)field;
  state->s_sequential = field->s_sequential;

  Py_ssize_t offset = CpField_GetOffset(field, (PyObject*)state);
  if (offset < 0 && PyErr_Occurred()) {
    return -1;
  }

  if (offset == -1 || !field->s_keep_pos) {
    if (!(fallback = cp_state_io_tell(state))) {
      return -1;
    };
  }

  if (offset >= 0) {
    // We write the current field into a temporary memory buffer
    // and add it after all processing has finished.
    base_stream = Py_XNewRef(state->m_io);
    state->m_io = PyObject_CallNoArgs(state->mod->io_bytesio);
    if (!state->m_io) {
      return -1;
    }
  }

  if (!PyCallable_Check(field->m_atom)) {
    return cp_pack_internal(op, field->m_atom, state);
  } else {
    PyObject* res = CpContext_Call(field->m_atom, (PyObject*)state);
    if (!res) {
      return -1;
    }

    if (field->m_switch && field->m_switch != Py_None) {
      PyObject* atom = CpField_GetSwitchAtom(field, res, (PyObject*)state);
      Py_DECREF(res);
      if (!atom) {
        return -1;
      }
      if (cp_pack_internal(op, atom, state) < 0) {
        return -1;
      }
    } else
      Py_DECREF(res);
  }

  if (offset == -1 || !field->s_keep_pos) {
    if (!cp_state_io_seek(state, fallback, 0)) {
      return -1;
    }
  }

  if (offset >= 0) {
    if (PyObject_SetItem(
          state->m_offset_table, PyLong_FromSsize_t(offset), state->m_io) < 0)
      return -1;

    Py_XSETREF(state->m_io, base_stream);
  }
  return 0;
}

static int
cp_pack_common(PyObject* op, PyObject* atom, CpState* state)
{
  int success;
  if (!state->s_sequential) {
    return PyObject_CallMethod(atom, CpAtomType_Pack, "OO", op, state) ? 0 : -1;
  }

  if (PyObject_HasAttr(atom, state->mod->str___pack_many__)) {
    // class explicitly defines __pack_many__ -> use it
    PyObject* res = CpAtom_CallPack(
      atom, state->mod->str___pack_many__, op, (PyObject*)state);
    success = res ? 0 : -1;
    Py_DECREF(res);
    return success;
  }

  if (!PySequence_Check(op)) {
    PyErr_Format(PyExc_ValueError, "input object (%R) is not a sequence", op);
    return -1;
  }

  // TODO: explain why
  state->s_sequential = false;

  Py_ssize_t size = PySequence_Size(op);
  PyObject* length =
    CpField_GetLength((CpField*)state->m_field, (PyObject*)state);
  if (!length) {
    return -1;
  }

  if (length == &_Py_EllipsisObject) {
    // Greedy means we pack all elements
    state->s_greedy = true;
    state->m_length = size;
    Py_XDECREF(length);
  } else if (PySlice_Check(length)) {
    state->s_greedy = false;

    PyObject* start = PyObject_GetAttr(length, state->mod->str_start);
    Py_XDECREF(length);
    if (!start) {
      return -1;
    }
    if (Py_IsNone(start)) {
      PyErr_SetString(PyExc_ValueError, "start is None");
      return -1;
    }

    PyObject* sizeobj = PyLong_FromSsize_t(size);
    if (!sizeobj) {
      return -1;
    }
    success = cp_pack_internal(sizeobj, start, state);
    Py_DECREF(sizeobj);
    Py_DECREF(start);
    if (success < 0) {
      return success;
    }
    state->m_length = size;
  } else {
    if (!PyLong_Check(length)) {
      Py_XDECREF(length);
      PyErr_SetString(PyExc_ValueError, "length is not an integer");
      return -1;
    }

    state->s_greedy = false;
    state->m_length = PyLong_AsSsize_t(length);
    Py_XDECREF(length);
    if (state->m_length != size) {
      PyErr_Format(PyExc_ValueError,
                   "given length %d does not match sequence size %d",
                   state->m_length,
                   size);
      return -1;
    }
  }

  if (state->m_length <= 0) {
    // continue packing, here's nothing to store
    return 0;
  }
  PyObject* obj = NULL;
  PyObject* base_path = Py_NewRef(state->m_path);
  for (state->m_index = 0; state->m_index < state->m_length; state->m_index++) {
    obj = PySequence_GetItem(op, state->m_index);
    if (!obj) {
      Py_DECREF(base_path);
      return -1;
    }
    state->m_path = PyUnicode_FromFormat("%s.%d", base_path, state->m_index);
    if (!state->m_path) {
      Py_XDECREF(obj);
      Py_DECREF(base_path);
      return -1;
    }

    success = cp_pack_internal(obj, atom, state);
    Py_XSETREF(obj, NULL);
    if (success < 0) {
      Py_DECREF(base_path);
      return -1;
    }
  }
  return 0;
}

static int
cp_pack_internal(PyObject* op, PyObject* atom, CpState* state)
{
  // 1. the current context-sensitive variables must be stored
  // elsewhere.
  //
  // 2. the current context-sensitive variables must be restored
  // to their original values.
  int success;
  PyObject *obj = Py_XNewRef(state->m_obj), *field = Py_XNewRef(state->m_field),
           *value = Py_XNewRef(state->m_value),
           *path = Py_XNewRef(state->m_path),
           *sequence = Py_XNewRef(state->m_sequence);

  Py_ssize_t length = state->m_length, index = state->m_index;
  int8_t greedy = state->s_greedy, sequential = state->s_sequential;

  if (atom->ob_type == &CpField_Type) {
    success = cp_pack_field(op, (CpField*)atom, state);
  } else {
    success = cp_pack_common(op, atom, state);
  }

  Py_XSETREF(state->m_obj, obj);
  Py_XSETREF(state->m_field, field);
  Py_XSETREF(state->m_value, value);
  Py_XSETREF(state->m_sequence, sequence);
  Py_XSETREF(state->m_path, path);
  state->m_length = length;
  state->m_index = index;
  state->s_greedy = greedy;
  state->s_sequential = sequential;
  return success;
}

static int
cp_pack(PyObject* op, PyObject* atom, PyObject* io, PyObject* globals, int raw)
{
  CpState* state =
    (CpState*)PyObject_CallFunction((PyObject*)&CpState_Type, "O", io);
  if (!state) {
    return -1;
  }

  if (globals) {
    if (cp_state_set_globals(state, globals, NULL) < 0) {
      Py_DECREF(atom);
      return -1;
    }
  }

  int success = cp_pack_internal(op, atom, (CpState*)Py_NewRef(state));
  if (success < 0) {
    Py_DECREF(state);
    return success;
  }
  Py_DECREF(state);
  return success;
}

// ------------------------------------------------------------------------------
// typeof
// ------------------------------------------------------------------------------
static PyObject*
cp_typeof_common(PyObject* op)
{
  PyObject* type = NULL;
  if (!op) {
    PyErr_SetString(PyExc_ValueError, "input object is NULL!");
    return NULL;
  }
  _coremodulestate* state = get_global_core_state();
  PyObject* attr = PyObject_GetAttrString(op, CpAtomType_Type);
  MATCH
  {
    CASE_COND(!attr)
    {
      PyErr_Clear();
      type = Py_NewRef(state->typing_any);
    }

    else CASE_COND(!PyCallable_Check(attr))
    {
      type = Py_NewRef(state->typing_any);
    }

    else
    {
      type = PyObject_CallNoArgs(attr);
      if (!type) {
        return NULL;
      }
    }
  }

  if (type == Py_NotImplemented) {
    _Cp_SetObj(type, Py_NewRef(state->typing_any));
  }

  return type;
}

static PyObject*
cp_typeof_field(struct CpField* op)
{
  PyObject *type = NULL, *switch_types = NULL;
  if (!op) {
    PyErr_SetString(PyExc_ValueError, "input object is NULL!");
    return NULL;
  }

  _coremodulestate* state = get_global_core_state();
  if (!op->s_type) {
    return Py_NewRef(state->typing_any);
  }

  if (!op->m_switch || Py_IsNone(op->m_switch)) {
    // new ref
    type = cp_typeof(op->m_atom);
    if (!type) {
      goto err;
    }
  } else if (PyCallable_Check(op->m_switch)) {
    Py_XSETREF(type, Py_NewRef(state->typing_any));
  } else {
    PyObject* types = PyList_New(NULL);
    if (!types) {
      goto err;
    }

    PyObject* values = PyDict_Values(op->m_switch);
    if (!values) {
      goto err;
    }

    Py_ssize_t length = PyList_GET_SIZE(values);
    PyObject* switch_type = NULL;
    for (Py_ssize_t i = 0; i < length; i++) {
      PyObject* value = PyList_GetItem(values, i);
      if (!value) {
        Py_XDECREF(values);
        goto err;
      }

      switch_type = cp_typeof(value);
      if (!switch_type) {
        Py_XDECREF(values);
        goto err;
      }

      if (!PySequence_Contains(switch_types, switch_type)) {
        PyList_Append(types, switch_type);
      }
      Py_XDECREF(switch_type);
      switch_type = NULL;
    }

    Py_XDECREF(values);
    PyObject* tuple = PyList_AsTuple(switch_types);
    if (!tuple) {
      goto err;
    }

    type = PyObject_GetItem(state->typing_union, tuple);
    Py_XDECREF(tuple);
  }

  if (!type) {
    goto err;
  }

  if (op->s_sequential) {
    Py_XSETREF(type, PyObject_GetItem(state->typing_list, type));
    if (!type) {
      goto err;
    }
  }

  return type;
err:
  Py_XDECREF(type);
  Py_XDECREF(switch_types);
  return NULL;
}

inline static PyObject*
cp_typeof(PyObject* op)
{
  if (!op) {
    PyErr_SetString(PyExc_ValueError, "input object is NULL!");
    return NULL;
  }

  if (op->ob_type == &CpField_Type) {
    return cp_typeof_field((CpField*)op);
  } else if (op->ob_type == &CpStruct_Type) {
    return Py_NewRef(((CpStruct*)op)->m_model);
  }

  return cp_typeof_common(op);
}

// ------------------------------------------------------------------------------
// Module
// ------------------------------------------------------------------------------
static PyObject*
_coremodule_typeof(PyObject* m, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "obj", NULL };
  PyObject* op = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &op)) {
    return NULL;
  }
  return cp_typeof(op);
}

static PyObject*
_coremodule_pack_into(PyObject* m, PyObject* args, PyObject* kw)
{
  PyObject *op = NULL, *atom = NULL, *io = NULL, *globals = PyDict_New(),
           *key = NULL, *value = NULL;
  int res = 0;
  if (!globals) {
    return NULL;
  }
  if (!PyArg_ParseTuple(args, "OOO", &op, &atom, &io)) {
    goto finish;
  }
  if (kw && PyDict_Check(kw)) {
    Py_ssize_t pos = 0;
    while (PyDict_Next(kw, &pos, &key, &value)) {
      if (PyDict_SetItem(globals, key, value) < 0) {
        goto finish;
      }
    }
  }
  if (Py_IsNone(atom)) {
    PyErr_SetString(PyExc_ValueError, "atom not set!");
    goto finish;
  }

  if (Py_IsNone(io)) {
    PyErr_SetString(PyExc_ValueError, "output stream not set!");
    goto finish;
  }

  // TODO: describe why we don't need to decrease the reference
  // count on these variables in the end.
  PyObject *atomobj = Py_NewRef(atom), *obj = Py_NewRef(op),
           *ioobj = Py_NewRef(io);

  res = cp_pack(obj, atomobj, ioobj, globals, false);
finish:
  Py_XDECREF(globals);
  return res < 0 ? NULL : Py_None;
}

static PyObject*
_coremodule_pack(PyObject* m, PyObject* args, PyObject* kw)
{
  PyObject *op = NULL, *atom = NULL, *globals = PyDict_New(), *key = NULL,
           *value = NULL, *io = NULL;
  int res = 0;
  if (!globals) {
    return NULL;
  }
  _coremodulestate* state = get_core_state(m);
  io = PyObject_CallNoArgs(state->io_bytesio);
  if (!io) {
    return NULL;
  }

  if (!PyArg_ParseTuple(args, "OO", &op, &atom)) {
    goto finish;
  }
  if (kw && PyDict_Check(kw)) {
    Py_ssize_t pos = 0;
    while (PyDict_Next(kw, &pos, &key, &value)) {
      if (PyDict_SetItem(globals, key, value) < 0) {
        goto finish;
      }
    }
  }
  if (Py_IsNone(atom)) {
    PyErr_SetString(PyExc_ValueError, "atom not set!");
    goto finish;
  }

  PyObject *atomobj = Py_NewRef(atom), *obj = Py_NewRef(op);
  res = cp_pack(obj, atomobj, io, globals, true);
finish:
  Py_XDECREF(globals);
  if (res < 0) {
    return NULL;
  }

  PyObject* result = PyObject_CallMethodNoArgs(io, state->str_bytesio_getvalue);
  Py_XDECREF(io);
  return result;
}

static int
_coremodule_clear(PyObject* m)
{
  _coremodulestate* state = get_core_state(m);
  if (state) {
    Py_CLEAR(state->cp_option__dynamic);
    Py_CLEAR(state->cp_option__sequential);
    Py_CLEAR(state->cp_option__keep_position);
    Py_CLEAR(state->cp_option__global_field_options);
    Py_CLEAR(state->cp_option__global_struct_options);
    Py_CLEAR(state->cp_option__union);
    Py_CLEAR(state->cp_option__eval);
    Py_CLEAR(state->cp_option__replace_types);
    Py_CLEAR(state->cp_option__discard_unnamed);
    Py_CLEAR(state->cp_option__discard_const);
    Py_CLEAR(state->cp_option__slots);

    Py_CLEAR(state->cp_endian__native);
    Py_CLEAR(state->cp_arch__host);
    Py_CLEAR(state->cp_regex__unnamed);
    Py_CLEAR(state->typing_any);
    Py_CLEAR(state->typing_list);
    Py_CLEAR(state->typing_union);

    Py_CLEAR(state->str___pack__);
    Py_CLEAR(state->str___unpack__);
    Py_CLEAR(state->str___size__);
    Py_CLEAR(state->str___type__);
    Py_CLEAR(state->str_write);
    Py_CLEAR(state->str_close);
    Py_CLEAR(state->str_read);
    Py_CLEAR(state->str_seek);
    Py_CLEAR(state->str_tell);
    Py_CLEAR(state->str___unpack_many__);
    Py_CLEAR(state->str___pack_many__);
    Py_CLEAR(state->str_start);
    Py_CLEAR(state->str_ctx__root);
    Py_CLEAR(state->str_ctx__getattr);
    Py_CLEAR(state->str_bytesio_getvalue);
    Py_CLEAR(state->str___annotations__);
    Py_CLEAR(state->str_builder_process);
    Py_CLEAR(state->str___mro__);
    Py_CLEAR(state->str___struct__);
    Py_CLEAR(state->str_pattern_match);
    Py_CLEAR(state->str___match_args__);
    Py_CLEAR(state->str___slots__);

    Py_CLEAR(state->io_bytesio);

    Py_CLEAR(state->inspect_getannotations);
  }
  return 0;
}

static void
_coremodule_free(void* m)
{
  _coremodule_clear((PyObject*)m);
}

static const char _coremodule__doc__[] = ("...");

static PyMethodDef _coremodule_methods[] = {
  { "typeof",
    (PyCFunction)_coremodule_typeof,
    METH_VARARGS | METH_KEYWORDS,
    "Returns the type of an object." },
  { "pack_into",
    (PyCFunction)_coremodule_pack_into,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { "pack", (PyCFunction)_coremodule_pack, METH_VARARGS | METH_KEYWORDS, NULL },
  { NULL }
};

static struct PyModuleDef _coremodule = {
  PyModuleDef_HEAD_INIT,
  .m_name = _Cp_Name(_core),
  .m_doc = _coremodule__doc__,
  .m_size = sizeof(_coremodulestate),
  .m_methods = _coremodule_methods,
  .m_clear = _coremodule_clear,
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
  CpType_Ready(&CpEndian_Type);

  CpContext_Type.tp_base = &PyDict_Type;
  CpType_Ready(&CpContext_Type);
  CpType_Ready(&CpUnaryExpr_Type);
  CpType_Ready(&CpBinaryExpr_Type);
  CpType_Ready(&CpContextPath_Type);
  CpType_Ready(&CpAtom_Type);
  CpType_Ready(&CpField_Type);

  CpFieldAtom_Type.tp_base = &CpAtom_Type;
  CpType_Ready(&CpFieldAtom_Type);

  CpType_Ready(&CpInvalidDefault_Type);
  CpType_Ready(&CpDefaultSwitchOption_Type);
  CpType_Ready(&CpState_Type);

  CpType_Ready(&CpStructFieldInfo_Type);
  CpType_Ready(&CpStruct_Type);

  m = PyModule_Create(&_coremodule);
  if (!m) {
    return NULL;
  }
  CpModule_AddObject("CpOption", &CpOption_Type);
  CpModule_AddObject("CpInvalidDefault", &CpInvalidDefault_Type);
  CpModule_AddObject("CpDefaultSwitchOption", &CpDefaultSwitchOption_Type);

  CpModule_AddObject("DEFAULT_OPTION", CP_DEFAULT_OPTION);
  CpModule_AddObject("INVALID_DEFAULT", CP_INVALID_DEFAULT);

  CpModule_AddObject("CpArch", &CpArch_Type);
  CpModule_AddObject("CpEndian", &CpEndian_Type);
  CpModule_AddObject("CpContext", &CpContext_Type);
  CpModule_AddObject("CpUnaryExpr", &CpUnaryExpr_Type);
  CpModule_AddObject("CpBinaryExpr", &CpBinaryExpr_Type);
  CpModule_AddObject("CpContextPath", &CpContextPath_Type);
  CpModule_AddObject("CpAtom", &CpAtom_Type);
  CpModule_AddObject("CpField", &CpField_Type);
  CpModule_AddObject("CpFieldAtom", &CpFieldAtom_Type);
  CpModule_AddObject("CpState", &CpState_Type);

  CpModule_AddObject("CpStructFieldInfo", &CpStructFieldInfo_Type);
  CpModule_AddObject("CpStruct", &CpStruct_Type);

  // setup state
  _coremodulestate* state = get_core_state(m);

  CpModule_AddOption(cp_option__dynamic, "field:dynamic", "F_DYNAMIC");
  CpModule_AddOption(cp_option__sequential, "field:sequential", "F_SEQUENTIAL");
  CpModule_AddOption(
    cp_option__keep_position, "field:keep_position", "F_KEEP_POSITION");
  CpModule_AddOption(cp_option__union, "struct:union", "S_UNION");
  CpModule_AddOption(
    cp_option__eval, "struct:eval_annotations", "S_EVAL_ANNOTATIONS");
  CpModule_AddOption(
    cp_option__replace_types, "struct:replace_types", "S_REPLACE_TYPES");
  CpModule_AddOption(
    cp_option__discard_unnamed, "struct:discard_unnamed", "S_DISCARD_UNNAMED");
  CpModule_AddOption(
    cp_option__discard_const, "struct:discard_const", "S_DISCARD_CONST");
  CpModule_AddOption(cp_option__slots, "struct:slots", "S_SLOTS");

  CpModule_AddGlobalOptions(cp_option__global_field_options, "G_FIELD_OPTIONS");
  CpModule_AddGlobalOptions(cp_option__global_struct_options, "G_SEQ_OPTIONS");

  CpModule_AddArch(cp_arch__host, "<host>", sizeof(void*) * 8, "HOST_ARCH");

  _CpModuleState_Def(
    cp_endian__native,
    "NATIVE_ENDIAN",
    PyObject_CallFunction((PyObject*)&CpEndian_Type, "sb", "native", '='));

  // setup typing constants
  PyObject* typing = PyImport_ImportModule("typing");
  if (!typing) {
    PyErr_SetString(PyExc_ImportError, "failed to import typing");
    return NULL;
  }

  _CpModuleState_Set(typing_any, PyObject_GetAttrString(typing, "Any"));
  _CpModuleState_Set(typing_list, PyObject_GetAttrString(typing, "List"));
  _CpModuleState_Set(typing_union, PyObject_GetAttrString(typing, "Union"));
  Py_XDECREF(typing);

  PyObject* io = PyImport_ImportModule("io");
  if (!io) {
    PyErr_SetString(PyExc_ImportError, "failed to import io");
    return NULL;
  }

  _CpModuleState_Set(io_bytesio, PyObject_GetAttrString(io, "BytesIO"));
  Py_XDECREF(io);

  PyObject* inspect = PyImport_ImportModule("inspect");
  if (!inspect) {
    PyErr_SetString(PyExc_ImportError, "failed to import inspect");
    return NULL;
  }

  _CpModuleState_Set(inspect_getannotations,
                     PyObject_GetAttrString(inspect, "get_annotations"));
  Py_XDECREF(inspect);

// intern strings
#define CACHED_STRING(attr, str)                                               \
  if ((state->attr = PyUnicode_InternFromString(str)) == NULL)                 \
  return NULL

  CACHED_STRING(str___pack__, CpAtomType_Pack);
  CACHED_STRING(str___unpack__, CpAtomType_Unpack);
  CACHED_STRING(str___unpack_many__, CpAtomType_UnpackMany);
  CACHED_STRING(str___pack_many__, CpAtomType_PackMany);
  CACHED_STRING(str___size__, CpAtomType_Size);
  CACHED_STRING(str___type__, CpAtomType_Type);
  CACHED_STRING(str_close, "close");
  CACHED_STRING(str_read, "read");
  CACHED_STRING(str_write, "write");
  CACHED_STRING(str_seek, "seek");
  CACHED_STRING(str_tell, "tell");
  CACHED_STRING(str_start, "start");
  CACHED_STRING(str_ctx__root, "<root>");
  CACHED_STRING(str_ctx__getattr, CpContext_GetAttr);
  CACHED_STRING(str_bytesio_getvalue, "getvalue");
  CACHED_STRING(str___annotations__, "__annotations__");
  CACHED_STRING(str_builder_process, "process");
  CACHED_STRING(str___mro__, CpType_MRO);
  CACHED_STRING(str___struct__, CpType_Struct);
  CACHED_STRING(str_pattern_match, "match");
  CACHED_STRING(str___match_args__, "__match_args__");
  CACHED_STRING(str___slots__, "__slots__");

#undef CACHED_STRING

  PyObject* re = PyImport_ImportModule("re");
  if (!re) {
    return NULL;
  }

  PyObject* compile = PyObject_GetAttrString(re, "compile");
  if (!compile) {
    return NULL;
  }

  state->cp_regex__unnamed = PyObject_CallFunction(compile, "s", "_[0-9]*$");
  if (!state->cp_regex__unnamed) {
    return NULL;
  }

  return m;
}