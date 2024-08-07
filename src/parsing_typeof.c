/* typeof implementation */
#include "caterpillar/module.h"
#include "caterpillar/parsing.h"
#include "caterpillar/struct.h"

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
PyObject*
CpTypeOf_Field(CpFieldObject* op)
{
  PyObject *type = NULL, *switch_types = NULL;
  if (!op) {
    PyErr_SetString(PyExc_ValueError, "input object is NULL!");
    return NULL;
  }

  _modulestate* state = get_global_module_state();
  if (!op->s_type) {
    return Py_NewRef(state->Any_Type);
  }

  if (!op->m_switch || Py_IsNone(op->m_switch)) {
    // new ref
    type = CpTypeOf(op->m_atom);
    if (!type) {
      goto err;
    }
  } else if (PyCallable_Check(op->m_switch)) {
    Py_XSETREF(type, Py_NewRef(state->Any_Type));
  } else {
    PyObject* types = PyList_New(0);
    if (!types) {
      goto err;
    }
    PyObject *atomType = CpTypeOf(op->m_atom);
    if (!atomType) {
      Py_XDECREF(types);
      goto err;
    }
    if (PyList_Append(types, atomType) < 0) {
      Py_XDECREF(types);
      goto err;
    }

    PyObject* values = PyDict_Values(op->m_switch);
    if (!values) {
      Py_XDECREF(types);
      goto err;
    }

    Py_ssize_t length = PyList_GET_SIZE(values);
    PyObject* switch_type = NULL;
    for (Py_ssize_t i = 0; i < length; i++) {
      PyObject* value = PyList_GetItem(values, i);
      if (!value) {
        Py_XDECREF(values);
        Py_XDECREF(types);
        goto err;
      }

      switch_type = CpTypeOf(value);
      if (!switch_type) {
        Py_XDECREF(values);
        Py_XDECREF(types);
        goto err;
      }

      if (!PySequence_Contains(types, switch_type)) {
        PyList_Append(types, switch_type);
      }
      Py_XDECREF(switch_type);
      switch_type = NULL;
    }

    Py_XDECREF(values);
    PyObject* tuple = PyList_AsTuple(types);
    Py_XDECREF(types);
    if (!tuple) {
      goto err;
    }

    type = PyObject_GetItem(state->Union_Type, tuple);
    Py_XDECREF(tuple);
  }

  if (!type) {
    goto err;
  }

  if (op->s_sequential) {
    Py_XSETREF(type, PyObject_GetItem(state->List_Type, type));
    if (!type) {
      goto err;
    }
  }

  return type;
err:
  Py_XDECREF(type);
  return NULL;
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

  if (CpField_CheckExact(op)) {
    return CpTypeOf_Field((CpFieldObject*)op);
  } else if (CpStruct_CheckExact(op)) {
    return Py_NewRef(((CpStructObject*)op)->m_model);
  } else if (CpCAtom_CheckExact(op)) {
    return CpTypeOf_CAtom((CpCAtomObject*)op);
  }
  return CpTypeOf_Common(op);
}