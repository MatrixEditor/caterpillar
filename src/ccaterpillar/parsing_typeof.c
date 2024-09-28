/* typeof implementation */
#include "caterpillar/caterpillar.h"

/*CpAPI*/
PyObject*
CpTypeOf_Common(PyObject* op)
{
  PyObject* type = NULL;
  if (!op) {
    PyErr_SetString(PyExc_ValueError, "input object is NULL!");
    return NULL;
  }
  _modulestate* state = get_global_module_state();
  PyObject* attr = PyObject_GetAttr(op, state->str___type__);
  if (!attr) {
    PyErr_Clear();
    type = Py_NewRef(state->Any_Type);
  } else if (!PyCallable_Check(attr) || PyType_Check(attr)) {
    type = Py_NewRef(attr); // Py_NewRef(state->Any_Type);
  } else {
    type = PyObject_CallNoArgs(attr);
    if (!type) {
      return NULL;
    }
  }

  if (type == Py_NotImplemented) {
    _Cp_SetObj(type, Py_NewRef(state->Any_Type));
  }
  return type;
}

/*CpAPI*/
PyObject *
CpTypeOf_CAtom(CpCAtomObject* op)
{
  if (op->ob_type == NULL) {
    Py_RETURN_NOTIMPLEMENTED;
  }
  return op->ob_type((PyObject*)op);
}

/*CpAPI*/
PyObject*
CpTypeOf(PyObject* op)
{
  if (!op) {
    PyErr_SetString(PyExc_ValueError, "input object is NULL!");
    return NULL;
  }

  if (CpStruct_CheckExact(op)) {
    return Py_NewRef(((CpStructObject*)op)->m_model);
  } else if (CpCAtom_CheckExact(op)) {
    return CpTypeOf_CAtom((CpCAtomObject*)op);
  }
  return CpTypeOf_Common(op);
}