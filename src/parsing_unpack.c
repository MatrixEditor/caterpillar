/* unpacking operations */

#include "caterpillar/context.h"
#include "caterpillar/module.h"
#include "caterpillar/parsing.h"
#include "caterpillar/state.h"
#include "caterpillar/struct.h"

// ------------------------------------------------------------------------------
// unpack:
// Unlike serializing objects, unpacking returns fully qualified objects as a
// result. In addition, the internal 'obj' within a struct layer will be a
// CpContext instance.
// ------------------------------------------------------------------------------

/*CpAPI*/
int
_CpUnpack_EvalLength(CpLayerObject* layer,
                     PyObject* length,
                     bool* seq_greedy,
                     Py_ssize_t* seq_length)
{
  *seq_greedy = false;
  *seq_length = 0;
  if (!length) {
    return -1;
  }

  // 1. Case: greedy length
  //    We have to set the context variables accordingly.
  if (Py_IS_TYPE(length, &PyEllipsis_Type)) {
    *seq_greedy = true;
    *seq_length = -1;
  }

  // 2. Case: length is a slice (prefixed type)
  //    As this is a special type, we have to first parse the length
  //    using the given start atom.
  else if (PySlice_Check(length)) {

    seq_greedy = false;
    PyObject* start = PyObject_GetAttr(length, layer->m_state->mod->str_start);
    if (!start) {
      return -1;
    }

    if (Py_IsNone(start)) {
      PyErr_SetString(PyExc_ValueError, "start is None");
      return -1;
    }
    layer->s_sequential = false;
    Py_XSETREF(length, _Cp_Unpack(start, layer));
    layer->s_sequential = true;
    Py_DECREF(start);
    if (!length) {
      return -1;
    }

    // Set the length
    *seq_length = PyLong_AsSsize_t(length);
    if (seq_length < 0) {
      PyErr_SetString(PyExc_ValueError, "invalid length");
      return -1;
    }
  }

  // 3. Case: constant number
  else if (PyNumber_Check(length)) {
    seq_greedy = false;
    *seq_length = PyLong_AsSsize_t(length);
    if (seq_length < 0) {
      PyErr_SetString(PyExc_ValueError, "invalid length");
      return -1;
    }
  }

  else {
    PyErr_Format(PyExc_ValueError, "invalid length type: %R", length->ob_type);
    return -1;
  }
  return 0;
}

/*CpAPI*/
PyObject*
CpUnpack_Common(PyObject* op, CpLayerObject* layer)
{
  if (!op || !layer) {
    PyErr_SetString(PyExc_ValueError, "input or layer object is NULL!");
    return NULL;
  }

  if (!layer->s_sequential) {
    return PyObject_CallMethodOneArg(
      op, layer->m_state->mod->str___unpack__, (PyObject*)layer);
  }

  _modulestate* mod = layer->m_state->mod;
  if (!layer->m_field) {
    PyErr_SetString(PyExc_ValueError, "state is invalid (field is NULL)!");
    return NULL;
  }

  if (PyObject_HasAttr(op, mod->str___unpack_many__)) {
    PyObject* res =
      PyObject_CallMethodOneArg(op, mod->str___unpack_many__, (PyObject*)layer);
    PyObject* exc = NULL;
    if ((exc = PyErr_GetRaisedException(),
         exc && PyErr_GivenExceptionMatches(exc, PyExc_NotImplementedError))) {
      // Make sure this method continues to unpack
      Py_XDECREF(exc);
      PyErr_Clear();
      Py_XDECREF(res);
    } else {
      Py_XDECREF(exc);
      return res;
    }
  }

  PyObject *obj = NULL, *length = NULL;
  // First, get the amount of elements we have to parse
  bool seq_greedy = false;
  Py_ssize_t seq_length = 0;
  length = CpField_GetLength((CpFieldObject*)layer->m_field, (PyObject*)layer);
  if (!length) {
    goto fail;
  }
  if (_CpUnpack_EvalLength(layer, length, &seq_greedy, &seq_length) < 0) {
    goto fail;
  }
  CpLayerObject* seq_layer = CpLayer_New(layer->m_state, layer);
  if (!layer) {
    goto fail;
  }

  PyObject* seq = PyList_New(0);
  if (!seq) {
    goto fail;
  }

  CpLayer_SetSequence(seq_layer, seq, seq_length, seq_greedy);
  while (seq_layer->s_greedy || (seq_layer->m_index < seq_layer->m_length)) {
    seq_layer->m_path = PyUnicode_FromFormat(
      "%s.%d", _PyUnicode_AsString(layer->m_path), seq_layer->m_index);
    if (!seq_layer->m_path) {
      goto fail;
    }

    Py_XSETREF(obj, _Cp_Unpack(op, seq_layer));
    if (!obj) {

      if (seq_layer->s_greedy) {
        PyErr_Clear();
        break;
      }
      goto fail;
    }

    if (PyList_Append(seq_layer->m_sequence, Py_NewRef(obj)) < 0) {
      goto fail;
    }
    seq_layer->m_index++;
  }

success:
  Py_XDECREF(obj);
  Py_XDECREF(length);
  CpLayer_Invalidate(seq_layer);
  seq_layer = NULL;
  return Py_NewRef(seq);

fail:
  Py_XDECREF(obj);
  Py_XDECREF(length);
  if (seq_layer) {
    CpLayer_Invalidate(seq_layer);
  }
  return NULL;
}

/*CpAPI*/
PyObject*
CpUnpack_Field(CpFieldObject* field, CpLayerObject* layer)
{
  if (!field || !layer) {
    PyErr_SetString(PyExc_ValueError, "input or layer object is NULL!");
    return NULL;
  }

  CpLayer_AppendPath(layer, field->m_name);
  if (!layer->m_path) {
    return NULL;
  }

  int enabled = CpField_IsEnabled(field, (PyObject*)layer);
  if (enabled < 0) {
    return NULL;
  } else if (!enabled) {
    return Py_NewRef(Py_None);
  }

  PyObject *obj = NULL, *fallback = NULL;
  Py_ssize_t offset = -1;

  layer->s_sequential = field->s_sequential;
  Py_XSETREF(layer->m_field, Py_NewRef(field));
  if (PyCallable_Check(field->m_atom)) {
    obj = PyObject_CallOneArg(field->m_atom, (PyObject*)layer);
    if (!obj) {
      goto cleanup;
    }
  }
  // The underlying atom is not callable and therefore not a context lambda.
  // Using the internal unpack function we will try to parse the given data
  // stream.
  else {
    if (!field->s_keep_pos) {
      fallback = CpState_Tell(layer->m_state);
      if (!fallback) {
        goto cleanup;
      }
    }

    offset = CpField_GetOffset(field, (PyObject*)layer);
    if (offset < 0 && PyErr_Occurred()) {
      goto cleanup;
    }
    if (offset >= 0) {
      if (CpState_Seek(layer->m_state, PyLong_FromSsize_t(offset), 0) < 0) {
        goto cleanup;
      }
    }

    obj = _Cp_Unpack(field->m_atom, layer);

    if (!obj && PyErr_Occurred()) {
      if (!Cp_IsInvalidDefault(field->m_default)) {
        Py_XSETREF(obj, field->m_default);
      }
      if (!obj) {
        goto cleanup;
      }
      PyErr_Clear();
    }

    if (!field->s_keep_pos) {
      if (CpState_Seek(layer->m_state, fallback, 0) < 0) {
        goto cleanup;
      }
    }
  }

  if (field->m_switch && !Py_IsNone(field->m_switch)) {

    PyObject* atom = CpField_EvalSwitch(field, obj, (PyObject*)layer);
    if (!atom) {
      Py_XSETREF(obj, NULL);
      goto cleanup;
    }

    layer->m_value = Py_NewRef(obj);
    obj = _Cp_Unpack(atom, layer);
  }

cleanup:
  Py_XDECREF(fallback);
  return obj;
}

/*CpAPI*/
PyObject*
CpUnpack_Struct(CpStructObject* struct_, CpLayerObject* layer)
{
  if (layer->s_sequential) {
    // TODO: explain why
    return CpUnpack_Common((PyObject*)struct_, layer);
  }

  PyObject* obj = NULL;
  CpLayerObject* obj_layer = CpLayer_New(layer->m_state, layer);
  if (!obj_layer) {
    return NULL;
  }
  obj_layer->m_obj = CpObject_CreateNoArgs(&CpContext_Type);
  if (!obj_layer->m_obj) {
    goto cleanup;
  }

  CpStructFieldInfoObject *info = NULL, *union_field = NULL;
  Py_ssize_t pos = 0;
  PyObject *name = NULL, *value = NULL, *start = CpState_Tell(layer->m_state),
           *max_size = NULL, *stream_pos = NULL,
           *init_data = CpObject_CreateNoArgs(&CpContext_Type);

  if (!start || !init_data) {
    goto cleanup;
  }
  while (PyDict_Next(struct_->m_members, &pos, &name, (PyObject**)&info)) {
    if (struct_->s_union) {
      Py_XSETREF(stream_pos, CpState_Tell(layer->m_state));
      if (!stream_pos) {
        goto cleanup;
      }
    }

    value = _Cp_Unpack((PyObject*)info->m_field, obj_layer);
    if (!value || PyObject_SetItem(obj_layer->m_obj, name, value) < 0) {
      goto cleanup;
    }

    if (struct_->s_union) {
      PyObject* pos = CpState_Tell(obj_layer->m_state);
      if (!pos) {
        goto cleanup;
      }
      PyObject* sub_result = PyNumber_Subtract(pos, stream_pos);
      if (!sub_result) {
        Py_XDECREF(pos);
        goto cleanup;
      }
      if (PyObject_RichCompareBool(max_size, sub_result, Py_LT)) {
        Py_XSETREF(max_size, Py_NewRef(sub_result));
      }
      Py_XDECREF(sub_result);
      Py_XDECREF(pos);
      if (CpState_Seek(obj_layer->m_state, start, 0) < 0) {
        goto cleanup;
      }
    }
  }

  if (struct_->s_union) {
    PyObject* pos = PyNumber_Add(start, max_size);
    if (!pos) {
      goto cleanup;
    }
    if (CpState_Seek(layer->m_state, pos, 0) < 0) {
      Py_XDECREF(pos);
      goto cleanup;
    }
    Py_XDECREF(pos);
  }

  PyObject* args = PyTuple_New(0);
  obj = PyObject_Call((PyObject*)struct_->m_model, args, obj_layer->m_obj);
  Py_XDECREF(args);

cleanup:
  Py_XDECREF(value);
  Py_XDECREF(start);
  Py_XDECREF(init_data);
  Py_XDECREF(stream_pos);
  if (obj_layer) {
    CpLayer_Invalidate(obj_layer);
  }
  return obj;
}

/*CpAPI*/
PyObject*
_Cp_Unpack(PyObject* atom, CpLayerObject* layer)
{
  if (CpField_CheckExact(atom)) {
    return CpUnpack_Field((CpFieldObject*)atom, layer);
  } else if (CpStruct_CheckExact(atom)) {
    return CpUnpack_Struct((CpStructObject*)atom, layer);
  } else if (CpCAtom_Check(atom)) {
    return CpUnpack_CAtom((CpCAtomObject*)atom, layer);
  } else {
    return CpUnpack_Common(atom, layer);
  }
}

/*CpAPI*/
PyObject*
CpUnpack_CAtom(CpCAtomObject* catom, CpLayerObject* layer)
{
  PyObject* result = NULL;
  if (!layer->s_sequential) {
    if (catom->ob_unpack == NULL) {
      PyErr_Format(
        PyExc_NotImplementedError,
        "The atom of type '%s' cannot be unpacked (missing __unpack__)",
        Py_TYPE(catom)->tp_name);
      return NULL;
    }
    result = catom->ob_unpack((PyObject *)catom, (PyObject *)layer);
  }
  else {
    if (!catom->ob_unpack_many) {
      // REVISIT: use flag to enable strict parsing
      // PyErr_Format(
      //   PyExc_NotImplementedError,
      //   "The atom of type '%s' cannot be unpacked (missing __unpack_many__)",
      //   Py_TYPE(catom)->tp_name);
      return CpUnpack_Common((PyObject *)catom, layer);
    }
    result = catom->ob_unpack_many((PyObject *)catom, (PyObject *)layer);
  }
  return result;
}

/*CpAPI*/
PyObject*
CpUnpack(PyObject* atom, PyObject* io, PyObject* globals)
{
  CpStateObject* state = CpState_New(io);
  PyObject* obj = NULL;
  if (!state) {
    return NULL;
  }

  if (globals) {
    if (CpState_SetGlobals(state, globals) < 0) {
      Py_DECREF(state);
      return NULL;
    }
  }

  CpLayerObject* root = CpLayer_New(state, NULL);
  if (!root) {
    Py_DECREF(state);
    return NULL;
  }

  Py_XSETREF(root->m_path, Py_NewRef(state->mod->str_ctx__root));
  obj = _Cp_Unpack(atom, root);

  if (!obj) {
    if (!PyErr_Occurred()) {
      PyErr_SetString(PyExc_RuntimeError, "Unpack failed");
    }
  }
  Py_DECREF(state);
  CpLayer_Invalidate(root);
  return obj;
}