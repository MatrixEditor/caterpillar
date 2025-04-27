/* immortal objects */

#include "caterpillar/caterpillar.h"

#if PY_3_13_PLUS
#define _Py_IMMORTAL_REFCNT _Py_IMMORTAL_INITIAL_REFCNT
#endif

static PyObject*
cp_invaliddefault_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  if (PyTuple_GET_SIZE(args) || PyDict_GET_SIZE(kw)) {
    PyErr_SetString(PyExc_TypeError,
                    "InvalidDefaultType does not accept arguments");
    return NULL;
  }

  Py_INCREF(CpInvalidDefault);
  return CpInvalidDefault;
}

static PyObject*
cp_invaliddefault_repr(PyObject* self)
{
  return PyUnicode_FromString("<invalid-default>");
}

PyTypeObject CpInvalidDefault_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(InvalidDefaultType),
  .tp_repr = (reprfunc)cp_invaliddefault_repr,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = (newfunc)cp_invaliddefault_new,
};

PyObject _CpInvalidDefault_Object = { _PyObject_EXTRA_INIT{
                                        _Py_IMMORTAL_REFCNT /* ob_refcnt */ },
                                      &CpInvalidDefault_Type /* ob_type */ };

static PyObject*
cp_defaultoption_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  if (PyTuple_GET_SIZE(args) || PyDict_GET_SIZE(kw)) {
    PyErr_SetString(PyExc_TypeError,
                    "InvalidDefaultType does not accept arguments");
    return NULL;
  }

  Py_INCREF(CpDefaultOption);
  return CpDefaultOption;
}

static PyObject*
cp_defaultoption_repr(PyObject* self)
{
  return PyUnicode_FromString("<switch-default>");
}

PyTypeObject CpDefaultOption_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(DefaultOptionType),
  .tp_repr = (reprfunc)cp_defaultoption_repr,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = (newfunc)cp_defaultoption_new,
};

PyObject _CpDefaultOption_Object = { _PyObject_EXTRA_INIT{
                                       _Py_IMMORTAL_REFCNT /* ob_refcnt */ },
                                     &CpDefaultOption_Type /* ob_type */ };
