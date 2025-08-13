#include "../../private.h"
#include "caterpillar/caterpillar.h"

#include <structmember.h>

static PyObject*
_Cp_EvalSwitchCases(PyObject* pValue, PyObject* pCases, PyObject* pContext);

static PyObject*
cp_switchatom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpSwitchAtomObject* self = NULL;
  _Cp_AssignCheck(self, (CpSwitchAtomObject*)type->tp_alloc(type, 0), error);

  CpBuiltinAtom_ATOM(self).ob_bits = NULL;
  CpBuiltinAtom_ATOM(self).ob_pack = CpSwitchAtom_Pack;
  CpBuiltinAtom_ATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_ATOM(self).ob_unpack = CpSwitchAtom_Unpack;
  CpBuiltinAtom_ATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_ATOM(self).ob_type = CpSwitchAtom_TypeOf;
  CpBuiltinAtom_ATOM(self).ob_size = NULL;
  self->m_atom = NULL;
  self->m_cases = NULL;
  self->s_callable = false;
  return _Cp_CAST(PyObject*, self);
error:
  return NULL;
}

static void
cp_switchatom_dealloc(CpSwitchAtomObject* self)
{
  Py_CLEAR(self->m_atom);
  Py_CLEAR(self->m_cases);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_switchatom_init(CpSwitchAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "atom", "cases", NULL };
  PyObject *atom = NULL, *cases = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "OO", kwlist, &atom, &cases)) {
    return -1;
  }
  _Cp_SetObj(self->m_atom, atom);
  _Cp_SetObj(self->m_cases, cases);
  self->s_callable = PyCallable_Check(atom);
  return 0;
}

_CpEndian_ImplSetByteorder(CpSwitchAtomObject, switchatom, self->m_atom);

static PyObject*
cp_switchatom_repr(CpSwitchAtomObject* self)
{
  return PyUnicode_FromFormat("<switch %R >> %R>", self->m_atom, self->m_cases);
}

static PyObject*
cp_switchatom_eval_with_context(CpSwitchAtomObject* self,
                                PyObject* args,
                                PyObject* kw)
{
  static char* kwlist[] = { "value", "context", NULL };
  PyObject *value = NULL, *context = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "OO", kwlist, &value, &context)) {
    return NULL;
  }
  return _Cp_EvalSwitchCases(value, self->m_cases, context);
}

/*Private API*/
static inline PyObject*
_Cp_EvalSwitchCases(PyObject* pValue, PyObject* pCases, PyObject* pContext)
{
  PyObject* nResult = NULL;

  if (PyCallable_Check(pCases)) {
    _Cp_AssignCheck(
      nResult,
      PyObject_CallFunctionObjArgs(pCases, pValue, pContext, NULL),
      error);
  } else {
    nResult = PyObject_GetItem(pCases, pValue);
    if (!nResult) {
      PyErr_Clear();
      // try and search for default case
      if ((nResult = PyObject_GetItem(pCases, Cp_DefaultOption), !nResult)) {
        PyErr_Clear();
        PyErr_Format(
          PyExc_ValueError,
          "No case matching the given value %R and no default case defined",
          pValue);
        goto error;
      }
    }
  }

  Py_XSETREF(nResult, Cp_GetStruct(nResult));
  return nResult;

error:
  return NULL;
}

/*Public API*/

/*CpAPI*/
PyObject*
CpSwitchAtom_EvalWithContext(PyObject* pAtom,
                             PyObject* pValue,
                             PyObject* pContext)
{
  CpSwitchAtomObject* self = _Cp_CAST(CpSwitchAtomObject*, pAtom);
  return _Cp_EvalSwitchCases(pValue, self->m_cases, pContext);
}

/*CpAPI*/
PyObject*
CpSwitchAtom_Unpack(PyObject* pAtom, PyObject* pContext)
{
  PyObject *nResult = NULL, *nValue = NULL, *nTargetAtom = NULL;
  CpSwitchAtomObject* self = _Cp_CAST(CpSwitchAtomObject*, pAtom);

  if (self->s_callable) {
    _Cp_AssignCheck(nValue, PyObject_CallOneArg(self->m_atom, pContext), error);
  } else {
    _Cp_AssignCheck(nValue, CpAtom_Unpack(self->m_atom, pContext), error);
  }

  _Cp_AssignCheck(
    nTargetAtom, _Cp_EvalSwitchCases(nValue, self->m_cases, pContext), error);

  Py_XSETREF(nResult, CpAtom_Unpack(nTargetAtom, pContext));
  goto success;

error:
  Py_XSETREF(nResult, NULL);

success:
  Py_XDECREF(nValue);
  Py_XDECREF(nTargetAtom);
  return nResult;
}

/*CpAPI*/
int
CpSwitchAtom_Pack(PyObject* pAtom, PyObject* pObj, PyObject* pContext)
{
  PyObject *nValue = NULL, *nTargetAtom = NULL;
  int result = 0;
  CpSwitchAtomObject* self = _Cp_CAST(CpSwitchAtomObject*, pAtom);

  if (!self->s_callable) {
    PyErr_SetString(
      PyExc_TypeError,
      ("Switch atom currently supports only callable atoms when used as a "
       "condition to select the final atom to be used to pack the given "
       "value."));
    return -1;
  }

  _Cp_AssignCheck(nValue, PyObject_CallOneArg(self->m_atom, pContext), error);
  _Cp_AssignCheck(
    nTargetAtom, _Cp_EvalSwitchCases(nValue, self->m_cases, pContext), error);
  result = CpAtom_Pack(nTargetAtom, pObj, pContext);
  goto success;

error:
  result = -1;

success:
  Py_XDECREF(nValue);
  Py_XDECREF(nTargetAtom);
  return result;
}

/*CpAPI*/
PyObject*
CpSwitchAtom_TypeOf(PyObject* pAtom)
{
  PyObject *nResult = NULL, *nAtomType = NULL, *nCasesValues = NULL,
           *bTmpObj = NULL, *nTmpAtomType = NULL, *nTmpAtom = NULL;
  Py_ssize_t numCases = 0;
  _modulestate* state = get_global_module_state();
  CpSwitchAtomObject* self = _Cp_CAST(CpSwitchAtomObject*, pAtom);

  // we don't know the type of dynamic switch atoms
  if (!PyDict_Check(self->m_cases)) {
    return Py_NewRef(&PyBaseObject_Type);
  }

  _Cp_AssignCheck(nResult, CpAtom_TypeOf(self->m_atom), error);
  _Cp_AssignCheck(nCasesValues, PyDict_Values(self->m_cases), error);
  numCases = PyList_Size(nCasesValues);
  for (Py_ssize_t i = 0; i < numCases; i++) {
    _Cp_AssignCheck(bTmpObj, PyList_GetItem(nCasesValues, i), error);
    Py_XSETREF(nTmpAtom, Cp_GetStruct(bTmpObj));
    if (!nTmpAtom) {
      goto error;
    }

    Py_XSETREF(nTmpAtomType, CpAtom_TypeOf(nTmpAtom));
    if (!nTmpAtomType) {
      goto error;
    }

    Py_XSETREF(nResult, PyNumber_Or(nResult, nTmpAtomType));
  }
  goto success;

error:
  Py_XSETREF(nResult, NULL);

success:
  Py_XDECREF(nAtomType);
  Py_XDECREF(nCasesValues);
  return nResult;
}

/*type*/

/* members */
static PyMemberDef CpSwitchAtom_Members[] = {
  { "cases", T_OBJECT, offsetof(CpSwitchAtomObject, m_cases), READONLY },
  { "atom", T_OBJECT, offsetof(CpSwitchAtomObject, m_atom), READONLY },
  { NULL }
};

static PyMethodDef CpSwitchAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(switchatom, NULL),
  { "eval_with_context",
    (PyCFunction)cp_switchatom_eval_with_context,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { NULL }
};

PyTypeObject CpSwitchAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpSwitchAtom_NAME),
  .tp_basicsize = sizeof(CpSwitchAtomObject),
  .tp_dealloc = (destructor)cp_switchatom_dealloc,
  .tp_init = (initproc)cp_switchatom_init,
  .tp_members = CpSwitchAtom_Members,
  .tp_methods = CpSwitchAtom_Methods,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_new = (newfunc)cp_switchatom_new,
  .tp_repr = (reprfunc)cp_switchatom_repr,
};

/*init*/
int
cp_switch__mod_types()
{
  CpSwitchAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpModule_SetupType(&CpSwitchAtom_Type, -1);
  return 0;
}

void
cp_switch__mod_clear(PyObject* m, _modulestate* state)
{
}

int
cp_switch__mod_init(PyObject* m, _modulestate* state)
{
  CpModule_AddObject(CpSwitchAtom_NAME, &CpSwitchAtom_Type, -1);
  return 0;
}