#include "../../private.h"
#include "caterpillar/caterpillar.h"

#include <structmember.h>

static PyObject*
cp_conditionalatom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpConditionalAtomObject* self = NULL;
  _Cp_AssignCheck(
    self, (CpConditionalAtomObject*)type->tp_alloc(type, 0), error);

  CpBuiltinAtom_ATOM(self).ob_bits = NULL;
  CpBuiltinAtom_ATOM(self).ob_pack = CpConditionalAtom_Pack;
  CpBuiltinAtom_ATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_ATOM(self).ob_unpack = CpConditionalAtom_Unpack;
  CpBuiltinAtom_ATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_ATOM(self).ob_type = CpConditionalAtom_TypeOf;
  CpBuiltinAtom_ATOM(self).ob_size = CpConditionalAtom_Size;
  self->m_atom = NULL;
  self->m_condition = NULL;

  return _Cp_CAST(PyObject*, self);
error:
  return NULL;
}

static void
cp_conditionalatom_dealloc(CpConditionalAtomObject* self)
{
  Py_CLEAR(self->m_atom);
  Py_CLEAR(self->m_condition);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_conditionalatom_init(CpConditionalAtomObject* self,
                        PyObject* args,
                        PyObject* kw)
{
  static char* kwlist[] = { "atom", "condition", NULL };
  PyObject *atom = NULL, *condition = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "OO", kwlist, &atom, &condition)) {
    return -1;
  }
  _Cp_SetObj(self->m_atom, atom);
  _Cp_SetObj(self->m_condition, condition);
  return 0;
}

_CpEndian_ImplSetByteorder(CpConditionalAtomObject,
                           conditionalatom,
                           self->m_atom);

static PyObject*
cp_conditionalatom_repr(CpConditionalAtomObject* self)
{
  return PyUnicode_FromFormat("%R if (%R)", self->m_atom, self->m_condition);
}

static PyObject*
cp_conditionalatom_eval_with_context(PyObject* self,
                                     PyObject* args,
                                     PyObject* kw)
{
  static char* kwlist[] = { "context", NULL };
  PyObject* context = NULL;
  int result = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &context)) {
    return NULL;
  }

  if ((result = CpConditionalAtom_Enabled(self, context), result < 0)) {
    return NULL;
  }

  return result ? Py_True : Py_False;
}

/*Public API*/

/*CpAPI*/
int
CpConditionalAtom_Enabled(PyObject* pAtom, PyObject* pContext)
{
  PyObject* nContextLambdaResult = NULL;
  int enabled = false;
  CpConditionalAtomObject* self = _Cp_CAST(CpConditionalAtomObject*, pAtom);

  if (!self->m_condition) {
    enabled = true;
  } else if (PyCallable_Check(self->m_condition)) {
    _Cp_AssignCheck(nContextLambdaResult,
                    PyObject_CallOneArg(self->m_condition, pContext),
                    error);

    enabled = PyObject_IsTrue(nContextLambdaResult);
  } else {
    enabled = PyObject_IsTrue(self->m_condition);
  }
  goto success;

error:
  enabled = -1;

success:
  Py_XDECREF(nContextLambdaResult);
  return enabled;
}

/*CpAPI*/
int
CpConditionalAtom_Pack(PyObject* pAtom, PyObject* pObj, PyObject* pContext)
{
  int enabled = 0;
  if ((enabled = CpConditionalAtom_Enabled(pAtom, pContext)) < 0) {
    return -1;
  }

  return enabled
           ? CpAtom_Pack(_Cp_CAST(CpConditionalAtomObject*, pAtom)->m_atom,
                         pObj,
                         pContext)
           : 0;
}

/*CpAPI*/
PyObject*
CpConditionalAtom_Unpack(PyObject* pAtom, PyObject* pContext)
{
  int enabled = 0;
  if ((enabled = CpConditionalAtom_Enabled(pAtom, pContext)) < 0) {
    return NULL;
  }

  return enabled
           ? CpAtom_Unpack(_Cp_CAST(CpConditionalAtomObject*, pAtom)->m_atom,
                           pContext)
           : Py_None;
}

/*CpAPI*/
PyObject*
CpConditionalAtom_TypeOf(PyObject* pAtom)
{
  PyObject *nResult = NULL, *nAtomType = NULL;
  CpConditionalAtomObject* self = _Cp_CAST(CpConditionalAtomObject*, pAtom);

  _Cp_AssignCheck(nAtomType, CpAtom_TypeOf(self->m_atom), error);
  _Cp_AssignCheck(nResult, PyNumber_Or(nAtomType, Py_None), error);
  goto success;

error:
  Py_CLEAR(nResult);

success:
  Py_XDECREF(nAtomType);
  return nResult;
}

/*CpAPI*/
PyObject*
CpConditionalAtom_Size(PyObject* pAtom, PyObject* pContext)
{
  PyObject* nResult = NULL;
  int enabled = 0;

  if ((enabled = CpConditionalAtom_Enabled(pAtom, pContext)) >= 0) {
    nResult = enabled
                ? CpAtom_Size(_Cp_CAST(CpConditionalAtomObject*, pAtom)->m_atom,
                              pContext)
                : PyLong_FromLong(0);
  }

  return nResult;
}

/*type*/
static PyMemberDef CpConditionAtom_Members[] = {
  { "condition",
    T_OBJECT,
    offsetof(CpConditionalAtomObject, m_condition),
    READONLY },
  { "atom", T_OBJECT, offsetof(CpConditionalAtomObject, m_atom), READONLY },
  { NULL }
};

static PyMethodDef CpConditionAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(conditionalatom, NULL),
  {
    "is_enabled",
    (PyCFunction)cp_conditionalatom_eval_with_context,
    METH_VARARGS | METH_KEYWORDS,
  },
  { NULL }
};

PyTypeObject CpConditionalAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpConditionalAtom_NAME),
  .tp_basicsize = sizeof(CpConditionalAtomObject),
  .tp_dealloc = (destructor)cp_conditionalatom_dealloc,
  .tp_init = (initproc)cp_conditionalatom_init,
  .tp_members = CpConditionAtom_Members,
  .tp_methods = CpConditionAtom_Methods,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_new = (newfunc)cp_conditionalatom_new,
  .tp_repr = (reprfunc)cp_conditionalatom_repr,
};

/*init*/
int
cp_conditional__mod_types()
{
  CpConditionalAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpModule_SetupType(&CpConditionalAtom_Type, -1);
  return 0;
}

void
cp_conditional__mod_clear(PyObject* m, _modulestate* state)
{
}

int
cp_conditional__mod_init(PyObject* m, _modulestate* state)
{
  CpModule_AddObject(CpConditionalAtom_NAME, &CpConditionalAtom_Type, -1);
  return 0;
}