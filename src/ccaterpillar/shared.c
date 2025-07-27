#include "caterpillar/caterpillar.h"
#include "private.h"

#include <structmember.h>

// Factory types
PyObject* Cp_ContextFactory = NULL;
PyObject* Cp_ArrayFactory = NULL;
PyObject* Cp_DefaultOption = NULL;

PyObject* CpBytesIO_Type = NULL;

// Exceptions
PyObject* CpExc_Stop = NULL;

/*CpAPI*/
PyObject*
Cp_FactoryNew(PyObject* pFactoryReference)
{
  _modulestate* state = get_global_module_state();
  PyObject *nResult = NULL,
           *nFactory = PyObject_GetAttr(pFactoryReference, state->str__value);
  if (!nFactory) {
    PyErr_Clear();
    nResult = CpObject_CreateNoArgs(&CpContext_Type);
  } else {
    nResult = PyObject_CallNoArgs(nFactory);
  }
  return nResult;
}

/*CpAPI*/
int
Cp_HasStruct(PyObject* pObj)
{
  // native implementation
  PyObject* nType = NULL;
  int result = 0;
  _modulestate* state = get_global_module_state();

  if (PyType_Check(pObj)) {
    nType = Py_NewRef(pObj);
  } else {
    _Cp_AssignCheck(nType, PyObject_Type(pObj), error);
  }

  result = PyObject_HasAttr(nType, state->str__struct);
  goto success;

error:
  result = -1;

success:
  Py_XDECREF(nType);
  return result;
}

/*CpAPI*/
PyObject*
Cp_GetStructNoCheck(PyObject* pObj)
{
  // native implementation
  PyObject *nType = NULL, *nResult = NULL;
  _modulestate* state = get_global_module_state();

  if (PyType_Check(pObj)) {
    nType = Py_NewRef(pObj);
  } else {
    _Cp_AssignCheck(nType, PyObject_Type(pObj), error);
  }

  _Cp_AssignCheck(nResult, PyObject_GetAttr(nType, state->str__struct), error);
  goto success;

error:
  Py_XSETREF(nResult, NULL);

success:
  Py_XDECREF(nType);
  return nResult;
}

/*CpAPI*/
PyObject*
Cp_GetStruct(PyObject* pObj)
{
  // native implementation
  PyObject* nResult = NULL;

  nResult = Cp_GetStructNoCheck(pObj);
  if (!nResult) {
    PyErr_Clear();
    nResult = Py_NewRef(pObj);
  }

  return nResult;
}

/*CpAPI*/
PyObject*
Cp_EvalObject(PyObject* pObj, PyObject* pContext)
{
  PyObject* nResult = NULL;
  if (!pObj) {
    PyErr_SetString(PyExc_ValueError, "Input object cannot be null");
    goto error;
  }

  if (PyCallable_Check(pObj) && pContext) {
    _Cp_AssignCheck(nResult, PyObject_CallOneArg(pObj, pContext), error);
  } else {
    nResult = Py_NewRef(pObj);
  }
  return nResult;

error:
  // nResult won't be set when this code is reached
  return NULL;
}

/*init*/
void
shared__mod_clear(PyObject* m, _modulestate* state)
{
  Py_CLEAR(CpExc_Stop);
  Py_CLEAR(Cp_ArrayFactory);
  Py_CLEAR(Cp_ContextFactory);
  Py_CLEAR(Cp_DefaultOption);
}

int
shared__mod_init(PyObject* m, _modulestate* state)
{
#define _IMPORT_ATTR(ext_mod, attr, target)                                    \
  if ((target = PyObject_GetAttrString((ext_mod), (attr)), !target)) {         \
    goto err;                                                                  \
  }

  PyObject* nTmpMod = NULL;

  _Cp_AssignCheck(nTmpMod, PyImport_ImportModule("caterpillar.exception"), err);
  _IMPORT_ATTR(nTmpMod, "Stop", CpExc_Stop);
  Py_CLEAR(nTmpMod);

  // import shared options
  _Cp_AssignCheck(nTmpMod, PyImport_ImportModule("caterpillar.options"), err);
  _IMPORT_ATTR(nTmpMod, "O_ARRAY_FACTORY", Cp_ArrayFactory);
  Py_CLEAR(nTmpMod);

  _Cp_AssignCheck(nTmpMod, PyImport_ImportModule("caterpillar.context"), err);
  _IMPORT_ATTR(nTmpMod, "O_CONTEXT_FACTORY", Cp_ContextFactory);
  Py_CLEAR(nTmpMod);

  _Cp_AssignCheck(
    nTmpMod, PyImport_ImportModule("caterpillar.fields._base"), err);
  _IMPORT_ATTR(nTmpMod, "DEFAULT_OPTION", Cp_DefaultOption);
  Py_CLEAR(nTmpMod);

  _Cp_AssignCheck(nTmpMod, PyImport_ImportModule("io"), err);
  _IMPORT_ATTR(nTmpMod, "BytesIO", CpBytesIO_Type);
  Py_CLEAR(nTmpMod);

  return 0;

err:
  return -1;

#undef _IMPORT_ATTR
}