/* unpacking operations */

#include "caterpillar/caterpillar.h"

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
    Py_XSETREF(length, _Cp_Unpack(start, layer));
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
CpUnpack_CAtom(CpCAtomObject* catom, CpLayerObject* layer)
{
  if (catom->ob_unpack == NULL) {
    PyErr_Format(
      PyExc_NotImplementedError,
      "The atom of type '%s' cannot be unpacked (missing __unpack__)",
      Py_TYPE(catom)->tp_name);
    return NULL;
  }
  return catom->ob_unpack((PyObject*)catom, (PyObject*)layer);
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

  Py_DECREF(state);
  CpLayer_Invalidate(root);
  return obj;
}