/* sizeof implementation */
#include "caterpillar/module.h"
#include "caterpillar/parsing.h"

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

PyObject*
CpSizeOf_Field(CpFieldObject* field, CpLayerObject* layer)
{
  // Size calculation is done in a special way. The following situations have
  // to be considered:
  //
  //  1. Disabled field: return 0
  //  2. Dynamic field: raise an error
  //  3. Sequential field: multiply the size of the underlying atom by the
  //     number of elements
  //  4. Constant field: just return the size of the atom
  if (!field) {
    PyErr_SetString(PyExc_ValueError, "field is NULL!");
    return NULL;
  }
  if (!layer) {
    PyErr_SetString(PyExc_ValueError, "state is NULL!");
    return NULL;
  }

  // set path
  CpLayer_AppendPath(layer, field->m_name);
  if (!layer->m_path) {
    return NULL;
  }

  if (!CpField_IsEnabled(field, (PyObject*)layer)) {
    // see case 1.
    return PyLong_FromLong(0);
  }

  _modulestate* mod = layer->m_state->mod;
  PyObject *count = PyLong_FromLong(1), *size = NULL, *extraSize = NULL;
  if (!count) {
    return NULL;
  }

  if (PySet_Contains(field->m_options, mod->cp_option__dynamic)) {
    // see case 2.
    PyErr_SetString(PyExc_ValueError, "dynamic fields are not supported!");
    return NULL;
  }

  // prepare context
  Py_XSETREF(layer->m_field, Py_NewRef(field));
  if (field->s_sequential) {
    count = CpField_GetLength(field, (PyObject*)layer);
    if (!count) {
      return NULL;
    }

    if (!PyLong_Check(count)) {
      Py_XDECREF(count);
      PyErr_SetString(PyExc_ValueError, "length is not an integer!");
      return NULL;
    }
  }

  PyObject* atom = Py_NewRef(field->m_atom);
  size = _Cp_SizeOf(atom, layer);
  if (!size) {
    goto fail;
  }

  if (field->m_switch) {
    // Static switch structures are supported only if the predecessor
    // is a context lambda.
    if (!PyCallable_Check(field->m_switch)) {
      PyErr_SetString(
        PyExc_ValueError,
        "Switch statement without ContextLambda is danymic sized!");
      goto fail;
    }

    PyObject* value = PyObject_CallOneArg(field->m_switch, (PyObject*)layer);
    if (!value) {
      goto fail;
    }
    Py_XSETREF(extraSize, size);
    size = _Cp_SizeOf(value, layer);
    if (!size) {
      goto fail;
    }
    Py_XDECREF(value);
  }

  PyObject* result = PyNumber_Multiply(size, count);
  if (!result) {
    goto fail;
  }
  if (extraSize) {
    Py_XSETREF(result, PyNumber_Add(result, extraSize));
    if (!result) {
      goto fail;
    }
  }

  Py_XDECREF(size);
  Py_XDECREF(count);
  Py_XDECREF(atom);
  Py_XDECREF(extraSize);
  return result;

fail:
  Py_XDECREF(atom);
  Py_XDECREF(count);
  Py_XDECREF(size);
  Py_XDECREF(extraSize);
  return NULL;
}

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

  if (CpField_CheckExact(op)) {
    result = CpSizeOf_Field((CpFieldObject*)op, layer);
  } else if (CpStruct_CheckExact(op)) {
    result = CpSizeOf_Struct((CpStructObject*)op, layer);
  } else {
    result = CpSizeOf_Common(op, layer);
  }
  return result;
}

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