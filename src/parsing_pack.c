/* packing operations */
#include "caterpillar/caterpillar.h"

// ------------------------------------------------------------------------------
// pack:
// Serializing objects follows specific rules when it comes to CpLayerObject
// creation. The first layer (root layer) will be assigned with the path
// '<root>'. By default, cp_pack will automatically create a new layer object
// when called. Therefore, it is recommended to utilize cp_pack_internal for
// C calls to avoid unnecessary layer creation.
//
// Currently, the following conditions allow the creation of a new layer:
//    - Start packing an object
//    - Serializing a sequence object that requires to iterate over all
//      elements individually. Note that atoms that support '__unpack_many__'
//      won't be called with the newly created sequence layer.
//    - Struct object or named sequences of fields in general will always
//      introduce a new layer object.
//      REVISIT: HOw should we store context variables of the current packing
//      layer and where do we get the object from?
//
// There are some built-in types that are designed to fasten calls by providing
// a native C implementation. It is recommended to implement new classes in C
// to leverage its speed rather than define new Python atom classes.
//
// A full workflow of cp_pack with all layers displayed would be the following:
//    1. cp_pack: create new state and root layer         | l: <root>
//    2. cp_pack_internal: measure atom type and call     |         <--+-+-+
//       according C method                               | l: <root>  | | |
//    3. One of the following methods will be called:                  | | |
//      a. cp_pack_catom: calls native C method           | l: <root>  | | |
//      b. cp_pack_atom: call python pack method          | l: <root>  | | |
//      c. cp_pack_field: inserts the field instance into              | | |
//         the current layer and calls cp_pack_internal                | | |
//         again.                                         | l: <root> -+ | |
//      d. cp_pack_struct: creates a new object layer                    | |
//         that addresses only the current struct's                      | |
//         values. Calls cp_pack_internal on each field   | l: <obj>  ---+ |
//      e. cp_pack_common: createsa a new layer if                         |
//         multiple objects should be packed AND                           |
//         __[un]pack_many__ is not implemented.          | l: <seq|root> -+
// ------------------------------------------------------------------------------

/*CpAPI*/
int
_CpPack_EvalLength(CpLayerObject* layer,
                   PyObject* length,
                   Py_ssize_t size,
                   bool* greedy,
                   Py_ssize_t* dstLength)
{
  int success = 0;
  *greedy = false;
  *dstLength = 0;
  if (length == &_Py_EllipsisObject) {
    // Greedy means we pack all elements
    *greedy = true;
    *dstLength = size;
    Py_XDECREF(length);
    return 0;
  }
  if (PySlice_Check(length)) {
    greedy = false;

    PyObject* start = PyObject_GetAttr(length, layer->m_state->mod->str_start);
    Py_XDECREF(length);
    if (!start) {
      return -1;
    }
    if (Py_IsNone(start)) {
      PyErr_SetString(PyExc_ValueError, "start is None");
      return -1;
    }

    if (size < 0) {
      PyErr_SetString(PyExc_ValueError,
                      "Prefixed length is not supported for this atom!");
      return -1;
    }

    PyObject* sizeobj = PyLong_FromSsize_t(size);
    if (!sizeobj) {
      return -1;
    }
    // TODO: explain why
    layer->s_sequential = false;
    success = _Cp_Pack(sizeobj, start, layer);
    layer->s_sequential = true;
    Py_DECREF(sizeobj);
    Py_DECREF(start);
    if (success < 0) {
      return success;
    }
    *dstLength = size;
  } else {
    if (!PyLong_Check(length)) {
      Py_XDECREF(length);
      PyErr_SetString(PyExc_ValueError, "length is not an integer");
      return -1;
    }

    greedy = false;
    *dstLength = PyLong_AsSsize_t(length);
    Py_XDECREF(length);
    if (*dstLength != size && size > 0) {
      PyErr_Format(PyExc_ValueError,
                   "given length %d does not match sequence size %d",
                   *dstLength,
                   size);
      return -1;
    }
  }
  return 0;
}

/*CpAPI*/
int
CpPack_Field(PyObject* op, CpFieldObject* field, CpLayerObject* layer)
{
  // we can assert that all provided objects are of the correct type
  // REVISIT: really?
  if (!op) {
    PyErr_SetString(PyExc_ValueError, "object is NULL");
    return -1;
  }

  CpLayer_AppendPath(layer, field->m_name);
  if (!layer->m_path) {
    return -1;
  }

  int res = CpField_IsEnabled(field, (PyObject*)layer);
  if (!res) {
    // disabled fields are not packed
    return 0;
  }
  if (res < 0) {
    return -1;
  }

  PyObject *base_stream = NULL, *fallback = NULL;
  CpStateObject* state = layer->m_state;

  Py_XSETREF(layer->m_field, Py_NewRef((PyObject*)field));
  layer->s_sequential = field->s_sequential;

  Py_ssize_t offset = CpField_GetOffset(field, (PyObject*)layer);
  if (offset < 0 && PyErr_Occurred()) {
    return -1;
  }

  if (offset == -1 || !field->s_keep_pos) {
    if (!(fallback = CpState_Tell(layer->m_state))) {
      return -1;
    };
  }

  if (offset >= 0) {
    // We write the current field into a temporary memory buffer
    // and add it after all processing has finished.
    base_stream = Py_XNewRef(layer->m_state->m_io);
    layer->m_state->m_io = PyObject_CallNoArgs(state->mod->BytesIO_Type);
    if (!state->m_io) {
      return -1;
    }
  }

  if (!PyCallable_Check(field->m_atom)) {
    return _Cp_Pack(op, field->m_atom, layer);
  } else {
    PyObject* res = PyObject_CallOneArg(field->m_atom, (PyObject*)layer);
    if (!res) {
      return -1;
    }

    if (field->m_switch && field->m_switch != Py_None) {
      PyObject* atom = CpField_EvalSwitch(field, res, (PyObject*)layer);
      Py_DECREF(res);
      if (!atom) {
        return -1;
      }
      if (_Cp_Pack(op, atom, layer) < 0) {
        return -1;
      }
    } else
      Py_DECREF(res);
  }

  if (offset == -1 || !field->s_keep_pos) {
    if (!CpState_Seek(state, fallback, 0)) {
      return -1;
    }
  }

  if (offset >= 0) {
    if (PyObject_SetItem(
          state->m_offset_table, PyLong_FromSsize_t(offset), state->m_io) < 0)
      return -1;

    Py_XSETREF(state->m_io, base_stream);
  }
  return 0;
}

/*CpAPI*/
int
CpPack_Common(PyObject* op, PyObject* atom, CpLayerObject* layer)
{

  int success;
  if (!layer->s_sequential) {
    return PyObject_CallMethod(atom, "__pack__", "OO", op, layer) ? 0 : -1;
  }

  CpStateObject* state = layer->m_state;
  if (PyObject_HasAttr(atom, state->mod->str___pack_many__)) {
    // class explicitly defines __pack_many__ -> use it
    PyObject* res =
      CpAtom_Pack(atom, state->mod->str___pack_many__, op, (PyObject*)layer);
    PyObject* exc = NULL;
    if ((exc = PyErr_GetRaisedException(),
         exc && PyErr_GivenExceptionMatches(exc, PyExc_NotImplementedError))) {
      // Make sure this method continues to pack the given object
      Py_XDECREF(exc);
      PyErr_Clear();
      Py_XDECREF(res);
    } else {
      success = res ? 0 : -1;
      Py_XDECREF(res);
      Py_XDECREF(exc);
      return success;
    }
  }

  if (!PySequence_Check(op)) {
    PyErr_Format(PyExc_ValueError, "input object (%R) is not a sequence", op);
    return -1;
  }

  // TODO: explain why
  CpLayerObject* seq_layer = CpLayer_New(state, layer);
  if (!seq_layer) {
    return -1;
  }
  seq_layer->s_sequential = false;

  Py_ssize_t size = PySequence_Size(op);
  bool greedy = false;
  Py_ssize_t layer_length = 0;
  PyObject* length =
    CpField_GetLength((CpFieldObject*)layer->m_field, (PyObject*)layer);
  if (!length) {
    return -1;
  }
  if (_CpPack_EvalLength(layer, length, size, &greedy, &layer_length) < 0) {
    Py_XDECREF(length);
    return -1;
  }
  Py_XDECREF(length);

  if (layer_length <= 0) {
    // continue packing, here's nothing to store
    Py_XDECREF(seq_layer);
    return 0;
  }
  CpLayer_SetSequence(seq_layer, op, layer_length, greedy);

  PyObject* obj = NULL;
  for (seq_layer->m_index = 0; seq_layer->m_index < seq_layer->m_length;
       seq_layer->m_index++) {
    obj = PySequence_GetItem(op, seq_layer->m_index);
    if (!obj) {
      return -1;
    }
    seq_layer->m_path = PyUnicode_FromFormat(
      "%s.%d", _PyUnicode_AsString(layer->m_path), seq_layer->m_index);
    if (!seq_layer->m_path) {
      Py_XDECREF(obj);
      return -1;
    }
    success = _Cp_Pack(obj, atom, seq_layer);
    Py_XSETREF(obj, NULL);
    if (success < 0) {
      return -1;
    }
  }
  CpLayer_Invalidate(seq_layer);
  return 0;

fail:
  if (seq_layer) {
    CpLayer_Invalidate(seq_layer);
  }
  return -1;
}

/*CpAPI*/
int
CpPack_Struct(PyObject* op, CpStructObject* struct_, CpLayerObject* layer)
{

  if (layer->s_sequential) {
    // TODO: explain why
    return CpPack_Common(op, (PyObject*)struct_, layer);
  }

  if (PySequence_Check(op)) {
    PyErr_SetString(
      PyExc_ValueError,
      ("Expected a valid CpAtom definition, got a single "
       "struct for sequential packing. Did you forget to add '[]' "
       "at the end of your field definiton?"));
    return -1;
  }

  CpLayerObject* obj_layer = CpLayer_New(layer->m_state, layer);
  if (!obj_layer) {
    return -1;
  }
  obj_layer->m_obj = Py_NewRef(op);
  obj_layer->m_path = Py_NewRef(layer->m_path);

  CpStructFieldInfoObject *info = NULL, *union_field = NULL;
  // all borrowed references
  PyObject* name = NULL;
  // new references
  PyObject *max_size = NULL, *size = NULL, *cmp_result = NULL, *value = NULL;
  int res = 0;
  Py_ssize_t pos = 0;

  while (PyDict_Next(struct_->m_members, &pos, &name, (PyObject**)&info)) {

    if (struct_->s_union) {
      size = NULL; // cp_sizeof_field(info->m_field, state);
      if (!size) {
        goto fail;
      }
      cmp_result = PyObject_RichCompare(max_size, size, Py_LT);
      if (!cmp_result) {
        goto fail;
      }
      if (Py_IsTrue(cmp_result)) {
        max_size = Py_XNewRef(size);
        union_field = info;
      }
      Py_XSETREF(cmp_result, NULL);
      Py_XSETREF(size, NULL);
    }

    else {
      value = PyObject_GetAttr(op, name);
      if (!value) {
        goto fail;
      }

      res = _Cp_Pack(value, (PyObject*)info->m_field, obj_layer);
      if (res < 0) {
        goto fail;
      }
      Py_XDECREF(value);
      value = NULL;
    }
  }

  if (struct_->s_union) {
    if (!union_field) {
      goto success;
    }
    value = PyObject_GetAttr(op, union_field->m_field->m_name);
    if (!value) {
      goto fail;
    }
    res = _Cp_Pack(value, (PyObject*)union_field->m_field, obj_layer);
    if (res < 0) {
      goto fail;
    }
    goto cleanup;
  }

  goto success;

fail:
  res = -1;
  goto cleanup;

success:
  res = 0;

cleanup:
  Py_XDECREF(size);
  Py_XDECREF(max_size);
  Py_XDECREF(cmp_result);

  if (obj_layer) {
    CpLayer_Invalidate(obj_layer);
  }
  return res;
}

/*CpAPI*/
int
CpPack_CAtom(PyObject* op, CpCAtomObject* catom, CpLayerObject* layer)
{

  if (!layer->s_sequential) {
    if (catom->ob_pack == NULL) {
      PyErr_Format(PyExc_NotImplementedError,
                   "The atom of type '%s' cannot be packed (missing __pack__)",
                   Py_TYPE(catom)->tp_name);
      return -1;
    }
    return catom->ob_pack((PyObject*)catom, op, (PyObject*)layer);
  }

  if (catom->ob_pack_many == NULL) {
    // PyErr_Format(
    //   PyExc_NotImplementedError,
    //   "The atom of type '%s' cannot be packed (missing __pack_many__)",
    //   Py_TYPE(catom)->tp_name);
    // return -1;
    return CpPack_Common(op, (PyObject *)catom, layer);
  }
  return catom->ob_pack_many((PyObject*)catom, op, (PyObject*)layer);
}

/*CpAPI*/
int
_Cp_Pack(PyObject* op, PyObject* atom, CpLayerObject* layer)
{
  // 1. the current context-sensitive variables must be stored
  // elsewhere.
  //
  // 2. the current context-sensitive variables must be restored
  // to their original values.
  int success;
  if (CpField_CheckExact(atom)) {
    success = CpPack_Field(op, (CpFieldObject*)atom, layer);
  } else if (CpStruct_CheckExact(atom)) {
    success = CpPack_Struct(op, (CpStructObject*)atom, layer);
  } else if (CpCAtom_Check(atom)) {
    return CpPack_CAtom(op, (CpCAtomObject*)atom, layer);
  // else CASE(&CpCAtom_Type, atom) {
  //   success = cp_pack_catom
  // }
  } else {
    success = CpPack_Common(op, atom, layer);
  }
  return success;
}

/*CpAPI*/
int
CpPack(PyObject* op, PyObject* atom, PyObject* io, PyObject* globals)
{
  CpStateObject* state =
    (CpStateObject*)PyObject_CallFunction((PyObject*)&CpState_Type, "O", io);
  if (!state) {
    return -1;
  }

  if (globals) {
    if (CpState_SetGlobals(state, globals) < 0) {
      Py_DECREF(state);
      return -1;
    }
  }
  CpLayerObject* root = CpLayer_New(state, NULL);
  if (!root) {
    return -1;
  }
  Py_XSETREF(root->m_path, Py_NewRef(state->mod->str_ctx__root));
  int success = _Cp_Pack(op, atom, root);

  Py_XDECREF(state);
  CpLayer_Invalidate(root);
  return success;
}