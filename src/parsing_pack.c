/* packing operations */
#include "caterpillar/caterpillar.h"

// ------------------------------------------------------------------------------
// pack: (OUTDATED)
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
    success = _Cp_Pack(sizeobj, start, layer);
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
CpPack_CAtom(PyObject* op, CpCAtomObject* catom, CpLayerObject* layer)
{
  if (catom->ob_pack == NULL) {
    PyErr_Format(PyExc_NotImplementedError,
                 "The atom of type '%s' cannot be packed (missing __pack__)",
                 Py_TYPE(catom)->tp_name);
    return -1;
  }
  return catom->ob_pack((PyObject*)catom, op, (PyObject*)layer);
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