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
struct CpContext;
struct CpContextPath;
struct CpUnaryExpr;
struct CpBinaryExpr;
struct CpAtom;
struct CpField;

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

static PyObject _InvalidDefault_Object;
#define CP_INVALID_DEFAULT &_InvalidDefault_Object

static PyObject _DefaultSwitchOption_Object;
#define CP_DEFAULT_OPTION &_DefaultSwitchOption_Object

static struct PyModuleDef _coremodule;

// ------------------------------------------------------------------------------
// function defs
// ------------------------------------------------------------------------------
typedef int (*packfunc)(PyObject*, PyObject*,
                        PyObject*); // (self, obj, ctx)
typedef PyObject* (*unpackfunc)(PyObject*, PyObject*, PyObject*); // (self, ctx)
typedef PyObject* (*sizefunc)(PyObject*, PyObject*, PyObject*);   // (self, ctx)
typedef PyObject* (*typefunc)(PyObject*);                         // (self)
typedef PyObject* (*bitsfunc)(PyObject*);                         // (self)

// ------------------------------------------------------------------------------
// special attribute names
// ------------------------------------------------------------------------------
#define CpType_Template "__template__"
#define CpType_Struct "__struct__"

#define CpAtomType_Pack "__pack__"
#define CpAtomType_Unpack "__unpack__"
#define CpAtomType_Size "__size__"
#define CpAtomType_Type "__type__"

#define CpUnionHook_Init "__model_init__"
#define CpUnionHook_SetAttr "__model_setattr__"

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

  // default endian object
  PyObject* cp_endian__native;

  // typing constants
  PyObject* typing_any;
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
    T_OBJECT_EX,
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
  Py_XSETREF(result, NULL);

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
    PyErr_Format(PyExc_AttributeError, "CpContext has no attribute '%s'", name);
    return NULL;
  }
  return Py_NewRef(result);
}

const char cp_context__doc__[] =
  ("CpContext(**kwargs)\n"
   "\n"
   "Represents a context object with attribute-style access.\n"
   "\n"
   ":param kwargs: The name and value of each keyword argument are used to "
   "initialize the context.\n"
   ":type kwargs: dict\n");

static PyTypeObject CpContext_Type = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = _Cp_Name(_core.CpContext),
  .tp_doc = cp_context__doc__,
  .tp_basicsize = sizeof(CpContext),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_init = (initproc)cp_context_init,
  .tp_setattr = (setattrfunc)cp_context__setattr__,
  .tp_getattr = (getattrfunc)cp_context__getattr__,
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
  { "value", T_OBJECT_EX, offsetof(CpUnaryExpr, m_value), 0 },
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
  { "lhs", T_OBJECT_EX, offsetof(CpBinaryExpr, m_left), 0 },
  { "rhs", T_OBJECT_EX, offsetof(CpBinaryExpr, m_left), 0 },
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

  if (!PyObject_IsInstance(context, (PyObject*)&CpContext_Type)) {
    PyErr_SetString(PyExc_TypeError,
                    "context must be an instance of CpContext");
    return NULL;
  }

  Py_ssize_t length;
  const char* path = PyUnicode_AsUTF8AndSize(self->m_path, &length);
  return PyObject_GetAttrString(context, path);
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
  { "path", T_OBJECT_EX, offsetof(CpContextPath, m_path), READONLY },
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
CpAtomType_CanPack(PyObject* op)
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
CpAtomType_CanUnpack(PyObject* op)
{
  PyObject* attr = PyObject_GetAttrString(op, CpAtomType_Unpack);
  if (attr) {
    Py_DECREF(attr);
    return true;
  }
  PyErr_Clear();
  return false;
}

static inline bool
CpAtomType_HasType(PyObject* op)
{
  PyObject* attr = PyObject_GetAttrString(op, CpAtomType_Type);
  if (attr) {
    Py_DECREF(attr);
    return true;
  }
  PyErr_Clear();
  return false;
}

static inline bool
CpAtomType_HasSize(PyObject* op)
{
  PyObject* attr = PyObject_GetAttrString(op, CpAtomType_Size);
  if (attr) {
    Py_DECREF(attr);
    return true;
  }
  PyErr_Clear();
  return false;
}

typedef struct CpAtom
{
  PyObject_HEAD
} CpAtom;

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
  PyErr_SetString(PyExc_NotImplementedError, "type");
  return NULL;
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
  CpAtom _base;
  PyObject* m_atom;
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
  int8_t s_unpack;
  int8_t s_pack;
  int8_t s_size;
  int8_t s_type;
  int8_t s_sequential;
  int8_t s_keep_pos;
} CpField;

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
  self->m_condition = NULL;

  // internal state
  self->s_unpack = false;
  self->s_pack = false;
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

  self->s_pack = CpAtomType_CanPack(self->m_atom);
  self->s_unpack = CpAtomType_CanUnpack(self->m_atom);
  self->s_size = CpAtomType_HasSize(self->m_atom);
  self->s_type = CpAtomType_HasType(self->m_atom);
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
  if (self->m_length) {
    PyObject* result =
      PyObject_CallFunction((PyObject*)&CpField_Type, "O", self);
    if (!result) {
      return NULL;
    }
    if (cp_field_set_length((CpField*)result, key, NULL) < 0) {
      Py_XDECREF(result);
      return NULL;
    }
    return result;
  }

  if (cp_field_set_length(self, key, NULL) < 0) {
    return NULL;
  }
  return Py_NewRef((PyObject*)self);
}

static PyMemberDef CpField_Members[] = {
  { "name", T_OBJECT_EX, offsetof(CpField, m_name), 0 },
  { "default", T_OBJECT_EX, offsetof(CpField, m_default), 0 },
  { "options", T_OBJECT_EX, offsetof(CpField, m_options), 0 },
  { "atom", T_OBJECT_EX, offsetof(CpField, m_atom), READONLY },
  { "endian", T_OBJECT_EX, offsetof(CpField, m_endian), 0 },
  { "arch", T_OBJECT_EX, offsetof(CpField, m_arch), 0 },
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
};

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
    Py_CLEAR(state->cp_endian__native);
    Py_CLEAR(state->cp_arch__host);
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
  CpType_Ready(&CpEndian_Type);

  CpContext_Type.tp_base = &PyDict_Type;
  CpType_Ready(&CpContext_Type);
  CpType_Ready(&CpUnaryExpr_Type);
  CpType_Ready(&CpBinaryExpr_Type);
  CpType_Ready(&CpContextPath_Type);
  CpType_Ready(&CpAtom_Type);

  CpField_Type.tp_base = &CpAtom_Type;
  CpType_Ready(&CpField_Type);

  CpType_Ready(&CpInvalidDefault_Type);
  CpType_Ready(&CpDefaultSwitchOption_Type);

  m = PyModule_Create(&_coremodule);
  if (!m) {
    return NULL;
  }
  CpModule_AddObject("CpOption", &CpOption_Type);
  CpModule_AddObject("CpArch", &CpArch_Type);
  CpModule_AddObject("CpEndian", &CpEndian_Type);
  CpModule_AddObject("CpContext", &CpContext_Type);
  CpModule_AddObject("CpUnaryExpr", &CpUnaryExpr_Type);
  CpModule_AddObject("CpBinaryExpr", &CpBinaryExpr_Type);
  CpModule_AddObject("CpContextPath", &CpContextPath_Type);
  CpModule_AddObject("CpAtom", &CpAtom_Type);
  CpModule_AddObject("CpField", &CpField_Type);

  CpModule_AddObject("CpInvalidDefault", &CpInvalidDefault_Type);
  CpModule_AddObject("CpDefaultSwitchOption", &CpDefaultSwitchOption_Type);

  CpModule_AddObject("DEFAULT_OPTION", CP_DEFAULT_OPTION);
  CpModule_AddObject("INVALID_DEFAULT", CP_INVALID_DEFAULT);

  // setup state
  _coremodulestate* state = get_core_state(m);

  CpModule_AddOption(cp_option__dynamic, "field:dynamic", "F_DYNAMIC");
  CpModule_AddOption(cp_option__sequential, "field:sequential", "F_SEQUENTIAL");
  CpModule_AddOption(
    cp_option__keep_position, "field:keep_position", "F_KEEP_POSITION");

  CpModule_AddGlobalOptions(cp_option__global_field_options, "G_FIELD_OPTIONS");
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
  state->typing_any = PyObject_GetAttrString(typing, "Any");
  Py_XDECREF(typing);
  if (!state->typing_any) {
    PyErr_SetString(PyExc_ImportError, "failed to get typing.Any");
    return NULL;
  }
  return m;
}