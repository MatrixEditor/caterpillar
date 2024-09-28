/* context and context path implementation */
#include "caterpillar/context.h"
#include "structmember.h"

/* impl */
static int
cp_context_init(CpContextObject* self, PyObject* args, PyObject* kw)
{
  return PyDict_Type.tp_init((PyObject*)self, args, kw) < 0;
}

static int
cp_context__setattr__(CpContextObject* self, char* name, PyObject* value)
{
  return PyDict_SetItemString((PyObject*)&self->m_dict, name, value);
}

static inline PyObject*
_cp_context__context_getattr__(CpContextObject* self, PyObject* name)
{
  _modulestate* state = get_global_module_state();
  PyObject *tmp = NULL, *lineValue = name, *lastKey = NULL, *key = NULL,
           *obj = NULL;

  PyObject* values = PyUnicode_Split(lineValue, state->str_path_delim, -1);
  if (!values) {
    return NULL;
  }

  size_t length = PyList_Size(values);
  if (length == 0) {
    Py_XDECREF(values);
    PyErr_SetString(PyExc_ValueError, "Empty path");
    return NULL;
  }

  key = PyList_GetItem(values, 0);
  if (!key) {
    Py_XDECREF(values);
    return NULL;
  }

  tmp = Py_XNewRef(PyDict_GetItem((PyObject*)&self->m_dict, key));
  if (!tmp) {
    PyErr_Clear();
    PyErr_Format(
      PyExc_AttributeError, "Context has no attribute '%s'", Py_XNewRef(key));
    Py_XDECREF(values);
    return NULL;
  }

  obj = tmp;
  Py_XSETREF(lastKey, Py_XNewRef(key));
  for (size_t i = 1; i < length; i++) {
    key = PyList_GetItem(values, i);
    if (!key) {
      Py_XDECREF(values);
      return NULL;
    }

    tmp = PyObject_GetAttr(obj, key);
    if (!tmp) {
      PyErr_Clear();
      PyErr_Format(PyExc_AttributeError,
                   "'%s' has no attribute '%s'",
                   lastKey,
                   Py_XNewRef(key));
      Py_XDECREF(values);
      return NULL;
    }

    Py_XSETREF(obj, tmp);
    Py_XSETREF(lastKey, Py_XNewRef(key));
  }
  Py_XDECREF(values);
  return obj;
}

static PyObject*
cp_context__context_getattr__(CpContextObject* self, PyObject* args)
{
  PyObject* name = NULL;
  if (!PyArg_ParseTuple(args, "O", &name)) {
    return NULL;
  }
  return _cp_context__context_getattr__(self, name);
}

static PyObject*
cp_context__getattro__(CpContextObject* self, PyObject* name)
{
  PyObject* result = PyObject_GenericGetAttr((PyObject*)&self->m_dict, name);
  if (result) {
    return result;
  }

  PyErr_Clear();
  return _cp_context__context_getattr__(self, name);
}

/* public API */

/*CpAPI*/
CpContextObject*
CpContext_New(void)
{
  return (CpContextObject*)CpObject_CreateNoArgs(&CpContext_Type);
}

/* docs */

PyDoc_STRVAR(cp_context__doc__, "\
CpContext(**kwargs)\n\
--\n\
Represents a context object with attribute-style access.\n\
\n\
:param kwargs: The name and value of each keyword argument are used to \
initialize the context.\n\
:type kwargs: dict\n\
");

/* type setup */
static PyMethodDef CpContext_Methods[] = {
  { "__context_getattr__",
    (PyCFunction)cp_context__context_getattr__,
    METH_VARARGS,
    "Gets an attribute from the context" },
  { NULL } /* Sentinel */
};

PyTypeObject CpContext_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(Context),
  .tp_basicsize = sizeof(CpContextObject),
  .tp_setattr = (setattrfunc)cp_context__setattr__,
  .tp_getattro = (getattrofunc)cp_context__getattro__,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = cp_context__doc__,
  .tp_methods = CpContext_Methods,
  .tp_init = (initproc)cp_context_init,
};

//------------------------------------------------------------------------------
// unary expression
static PyObject*
cp_unaryexpr_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpUnaryExprObject* self;
  self = (CpUnaryExprObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  Py_INCREF(Py_None);
  self->m_value = Py_None;
  self->m_expr = -1;
  return (PyObject*)self;
}

static void
cp_unaryexpr_dealloc(CpUnaryExprObject* self)
{
  Py_XDECREF(self->m_value);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_unaryexpr_init(CpUnaryExprObject* self, PyObject* args, PyObject* kw)
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
cp_unaryexpr_repr(CpUnaryExprObject* self)
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
cp_unaryexpr_hash(CpUnaryExprObject* self)
{
  PyObject* expr = PyLong_FromSize_t(self->m_expr);
  Py_hash_t hash = PyObject_Hash(expr);
  Py_XDECREF(expr);
  return hash;
}

static PyObject*
cp_unaryexpr__call__(CpUnaryExprObject* self, PyObject* args, PyObject* kw)
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

/*CpAPI*/
CpUnaryExprObject*
CpUnaryExpr_New(int op, PyObject* value)
{
  return (CpUnaryExprObject*)CpObject_Create(
    &CpUnaryExpr_Type, "iO", op, value);
}

/* docs */

PyDoc_STRVAR(cp_unaryexpr_doc, "UnaryExpr(expr, value)");

/* type setup */
static PyMemberDef CpUnaryExpr_Members[] = {
  { "expr",
    T_INT,
    offsetof(CpUnaryExprObject, m_expr),
    READONLY,
    "The expression type." },
  { "value", T_OBJECT, offsetof(CpUnaryExprObject, m_value), 0, "The value." },
  { NULL } /* Sentinel */
};

PyTypeObject CpUnaryExpr_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(UnaryExpr),
  .tp_basicsize = sizeof(CpUnaryExprObject),
  .tp_dealloc = (destructor)cp_unaryexpr_dealloc,
  .tp_repr = (reprfunc)cp_unaryexpr_repr,
  .tp_hash = (hashfunc)cp_unaryexpr_hash,
  .tp_call = (ternaryfunc)cp_unaryexpr__call__,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_doc = cp_unaryexpr_doc,
  .tp_members = CpUnaryExpr_Members,
  .tp_init = (initproc)cp_unaryexpr_init,
  .tp_new = (newfunc)cp_unaryexpr_new,
};

//------------------------------------------------------------------------------
// binary expression
static PyObject*
cp_binaryexpr_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpBinaryExprObject* self;
  self = (CpBinaryExprObject*)type->tp_alloc(type, 0);
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
cp_binaryexpr_dealloc(CpBinaryExprObject* self)
{
  Py_XDECREF(self->m_left);
  Py_XDECREF(self->m_right);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_binaryexpr_init(CpBinaryExprObject* self, PyObject* args, PyObject* kw)
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
cp_binaryexpr_repr(CpBinaryExprObject* self)
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
cp_binaryexpr__call__(CpBinaryExprObject* self, PyObject* args, PyObject* kw)
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

/* operations */
#define _CpBinaryExpr_BinaryNumberMethod(name, op)                            \
  static PyObject* cp_binaryexpr_as_number_##name(PyObject* self,             \
                                                   PyObject* other)            \
  {                                                                            \
    return (PyObject*)CpBinaryExpr_New(op, self, other);                       \
  }

_CpBinaryExpr_BinaryNumberMethod(add, CpBinaryExpr_OpAdd);
_CpBinaryExpr_BinaryNumberMethod(sub, CpBinaryExpr_OpSub);
_CpBinaryExpr_BinaryNumberMethod(mul, CpBinaryExpr_OpMul);
_CpBinaryExpr_BinaryNumberMethod(div, CpBinaryExpr_OpTrueDiv);
_CpBinaryExpr_BinaryNumberMethod(truediv, CpBinaryExpr_OpTrueDiv);
_CpBinaryExpr_BinaryNumberMethod(floordiv, CpBinaryExpr_OpFloorDiv);
_CpBinaryExpr_BinaryNumberMethod(mod, CpBinaryExpr_OpMod);
_CpBinaryExpr_BinaryNumberMethod(lshift, CpBinaryExpr_OpLShift);
_CpBinaryExpr_BinaryNumberMethod(rshift, CpBinaryExpr_OpRShift);
_CpBinaryExpr_BinaryNumberMethod(and, CpBinaryExpr_OpBitAnd);
_CpBinaryExpr_BinaryNumberMethod(xor, CpBinaryExpr_OpBitXor);
_CpBinaryExpr_BinaryNumberMethod(or, CpBinaryExpr_OpBitOr);
_CpBinaryExpr_BinaryNumberMethod(pow, CpBinaryExpr_OpPow);
_CpBinaryExpr_BinaryNumberMethod(matmul, CpBinaryExpr_OpMatMul);

#undef _CpContextPath_BinaryNumberMethod

/*CpAPI*/
CpBinaryExprObject*
CpBinaryExpr_New(int op, PyObject* left, PyObject* right)
{
  return (CpBinaryExprObject*)CpObject_Create(
    &CpBinaryExpr_Type, "iOO", op, left, right);
}

/* docs */
PyDoc_STRVAR(cp_binaryexpr_doc, "CpBinaryExpr(expr, left, right)");

/* type setup */
static PyMemberDef CpBinaryExpr_Members[] = {
  { "expr",
    T_INT,
    offsetof(CpBinaryExprObject, m_expr),
    READONLY,
    "expression type" },
  { "lhs",
    T_OBJECT,
    offsetof(CpBinaryExprObject, m_left),
    0,
    "left hand side" },
  { "rhs",
    T_OBJECT,
    offsetof(CpBinaryExprObject, m_left),
    0,
    "right hand side" },
  { NULL } /* Sentinel */
};

PyTypeObject CpBinaryExpr_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(BinaryExpr),
  .tp_basicsize = sizeof(CpBinaryExprObject),
  .tp_dealloc = (destructor)cp_binaryexpr_dealloc,
  .tp_repr = (reprfunc)cp_binaryexpr_repr,
  .tp_call = (ternaryfunc)cp_binaryexpr__call__,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_doc = cp_unaryexpr_doc,
  .tp_members = CpBinaryExpr_Members,
  .tp_init = (initproc)cp_binaryexpr_init,
  .tp_new = (newfunc)cp_binaryexpr_new,
};

//------------------------------------------------------------------------------
// context path
static PyObject*
cp_contextpath_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpContextPathObject* self;
  self = (CpContextPathObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->m_path = PyUnicode_FromString("");
  if (!self->m_path) {
    Py_DECREF(self->m_path);
    return NULL;
  }
  self->m_state = get_global_module_state();
  return (PyObject*)self;
}

static void
cp_contextpath_dealloc(CpContextPathObject* self)
{
  Py_XDECREF(self->m_path);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_contextpath_init(CpContextPathObject* self, PyObject* args, PyObject* kw)
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
cp_contextpath_repr(CpContextPathObject* self)
{
  return PyUnicode_FromFormat("CpPath(%R)", self->m_path);
}

static Py_hash_t
cp_contextpath_hash(CpContextPathObject* self)
{
  return PyObject_Hash(self->m_path);
}

static PyObject*
cp_contextpath__type__(CpContextPathObject* self)
{
  PyObject* type = get_global_module_state()->Any_Type;
  Py_INCREF(type);
  return type;
}

static PyObject*
cp_contextpath__size__(CpContextPathObject* self, PyObject* args)
{
  return PyLong_FromSize_t(0);
}

static PyObject*
cp_contextpath__getattr__(CpContextPathObject* self, char* name)
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
cp_contextpath__call__(CpContextPathObject* self,
                       PyObject* args,
                       PyObject* kwargs)
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
cp_contextpath_as_number_neg(PyObject* self)
{
  return (PyObject*)CpUnaryExpr_New(CpUnaryExpr_OpNeg, self);
}

static PyObject*
cp_contextpath_as_number_pos(PyObject* self)
{
  return (PyObject*)CpUnaryExpr_New(CpUnaryExpr_OpPos, self);
}

static PyObject*
cp_contextpath_as_number_not(PyObject* self)
{
  return (PyObject*)CpUnaryExpr_New(CpUnaryExpr_OpNot, self);
}

#define _CpContextPath_BinaryNumberMethod(name, op)                            \
  static PyObject* cp_contextpath_as_number_##name(PyObject* self,             \
                                                   PyObject* other)            \
  {                                                                            \
    return (PyObject*)CpBinaryExpr_New(op, self, other);                       \
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

#undef _CpContextPath_BinaryNumberMethod

static PyObject*
cp_contextpath_richcmp(PyObject* self, PyObject* other, int op)
{
  return (PyObject*)CpBinaryExpr_New(op, self, other);
}

/*CpAPI*/
CpContextPathObject*
CpContextPath_New(PyObject* path)
{
  return (CpContextPathObject*)CpObject_Create(&CpContextPath_Type, "O", path);
}

/*CpAPI*/
CpContextPathObject*
CpContextPath_FromString(const char* path)
{
  return (CpContextPathObject*)CpObject_Create(&CpContextPath_Type, "s", path);
}


/* docs */
PyDoc_STRVAR(cp_contextpath__doc__, "\
ContextPath(path)\n\
--\n\
Represents a lambda function for retrieving a value from a Context \
based on a specified path.\n\
");

/* members */
static PyMemberDef CpContextPath_Members[] = { { "path",
                                                 T_OBJECT,
                                                 offsetof(CpContextPathObject,
                                                          m_path),
                                                 READONLY,
                                                 "the path" },
                                               { NULL } };

static PyMethodDef CpContextPath_Methods[] = {
  { "__type__", (PyCFunction)cp_contextpath__type__, METH_NOARGS },
  { "__size__", (PyCFunction)cp_contextpath__size__, METH_VARARGS },
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

/* type */
PyTypeObject CpContextPath_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(ContextPath),
  .tp_basicsize =sizeof(CpContextPathObject),
  .tp_dealloc =(destructor)cp_contextpath_dealloc,
  .tp_getattr =(getattrfunc)cp_contextpath__getattr__,
  .tp_repr =(reprfunc)cp_contextpath_repr,
  .tp_as_number =&CpContextPath_NumberMethods,
  .tp_hash =(hashfunc)cp_contextpath_hash,
  .tp_call =(ternaryfunc)cp_contextpath__call__,
  .tp_flags =Py_TPFLAGS_DEFAULT,
  .tp_doc =cp_contextpath__doc__,
  .tp_richcompare =(richcmpfunc)cp_contextpath_richcmp,
  .tp_methods =CpContextPath_Methods,
  .tp_members =CpContextPath_Members,
  .tp_init =(initproc)cp_contextpath_init,
  .tp_new =(newfunc)cp_contextpath_new,
};