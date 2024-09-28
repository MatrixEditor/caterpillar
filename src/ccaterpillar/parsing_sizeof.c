/* sizeof implementation */
#include "caterpillar/caterpillar.h"

/*CpAPI*/
PyObject*
CpSizeOf_Common(PyObject* op, CpLayerObject* layer)
{
  _modulestate* state = layer->m_state->mod;
  if (!PyObject_HasAttr(op, state->str___size__)) {
    PyErr_Format(
      PyExc_TypeError, "object %R of type %R has no __size__", op, op->ob_type);
    return NULL;
  }

  return PyObject_CallMethodOneArg(op, state->str___size__, (PyObject*)layer);
}

/*CpAPI*/
PyObject*
CpSizeOf_Struct(CpStructObject* struct_, CpLayerObject* layer)
{
  if (!struct_) {
    PyErr_SetString(PyExc_ValueError, "struct is NULL!");
    return NULL;
  }
  if (!layer) {
    PyErr_SetString(PyExc_ValueError, "state is NULL!");
    return NULL;
  }

  PyObject *max_size = PyLong_FromSize_t(0), *size = PyLong_FromLong(0),
           *tmp = NULL;
  CpStructFieldInfoObject* info = NULL;
  Py_ssize_t pos = 0;

  CpLayerObject* obj_layer = CpLayer_New(layer->m_state, layer);
  if (!obj_layer) {
    return NULL;
  }

  if (!max_size || !size) {
    goto fail;
  }

  while (PyDict_Next(struct_->m_members, &pos, NULL, (PyObject**)&info)) {
    tmp = _Cp_SizeOf((PyObject*)info->m_field, obj_layer);
    if (!tmp) {
      goto fail;
    }

    if (PyObject_RichCompareBool(max_size, tmp, Py_LT)) {
      Py_XSETREF(max_size, Py_NewRef(tmp));
    }

    Py_XSETREF(tmp, PyNumber_Add(size, tmp));
    if (!tmp) {
      goto fail;
    }
    Py_XSETREF(size, tmp);
  }
  CpLayer_Invalidate(obj_layer);
  return struct_->s_union ? max_size : size;

fail:
  Py_XDECREF(tmp);
  Py_XDECREF(max_size);
  Py_XDECREF(size);
  if (obj_layer) {
    CpLayer_Invalidate(obj_layer);
  }
  return NULL;
}

/*CpAPI*/
PyObject*
CpSizeOf_CAtom(CpCAtomObject* catom, CpLayerObject* layer)
{
  if (!catom->ob_size) {
    PyErr_Format(PyExc_NotImplementedError,
                 "The atom of type '%s' has no size (missing __size__)",
                 Py_TYPE(catom)->tp_name);
    return NULL;
  }
  return catom->ob_size((PyObject *)catom, (PyObject *)layer);
}

/*CpAPI*/
PyObject*
_Cp_SizeOf(PyObject* op, CpLayerObject* layer)
{
  PyObject* result = NULL;

  if (!op) {
    PyErr_SetString(PyExc_ValueError, "input object is NULL!");
    return NULL;
  }
  if (!layer) {
    PyErr_SetString(PyExc_ValueError, "state is NULL!");
    return NULL;
  }

  if (CpCAtom_Check(op)) {
    result = CpSizeOf_CAtom((CpCAtomObject*)op, layer);
  } else if (CpStruct_CheckExact(op)) {
    result = CpSizeOf_Struct((CpStructObject*)op, layer);
  } else {
    result = CpSizeOf_Common(op, layer);
  }
  return result;
}

/*CpAPI*/
PyObject*
CpSizeOf(PyObject* op, PyObject* globals)
{
  PyObject *result = NULL, *atom = NULL;
  CpStateObject* state = (CpStateObject*)CpObject_CreateNoArgs(&CpState_Type);
  if (!state) {
    return NULL;
  }

  if (globals) {
    if (CpState_SetGlobals(state, globals) < 0) {
      Py_DECREF(state);
      return NULL;
    }
  }

  if (!op) {
    PyErr_SetString(PyExc_ValueError, "input object is NULL!");
    Py_DECREF(state);
    return NULL;
  }

  CpLayerObject* layer = CpLayer_New(state, NULL);
  if (!layer) {
    return NULL;
  }
  Py_XSETREF(layer->m_path, state->mod->str_ctx__root);

  if (CpStructModel_Check(op, state->mod)) {
    atom = CpStructModel_GetStruct(op, state->mod);
    if (!atom) {
      Py_DECREF(state);
      return NULL;
    }
  } else {
    atom = Py_NewRef(op);
  }

  result = _Cp_SizeOf(atom, layer);
  Py_XDECREF(state);
  CpLayer_Invalidate(layer);
  return result;
}