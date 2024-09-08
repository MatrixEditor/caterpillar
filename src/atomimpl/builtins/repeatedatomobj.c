/* repeated atom C implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

/* impl */

static PyObject*
cp_repeatedatomobj__type__(CpRepeatedAtomObject* self)
{
  PyObject* atom_type = CpTypeOf(self->m_atom);
  if (!atom_type)
    return NULL;

  _modulestate* state = get_global_module_state();
  Py_XSETREF(atom_type, PyObject_GetItem(state->List_Type, atom_type));
  return atom_type;
}

static PyObject*
cp_repeatedatomobj__size__(CpRepeatedAtomObject* self, CpLayerObject* layer)
{
  return _Cp_SizeOf(self->m_atom, layer);
}

static PyObject*
cp_repeatedatomobj__repr__(CpRepeatedAtomObject* self)
{
  return PyUnicode_FromFormat("<repeated %R>", self->m_atom);
}

static PyObject*
cp_repeatedatomobj_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpRepeatedAtomObject* self;
  self = (CpRepeatedAtomObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  CpBuiltinAtom_CATOM(self).ob_bits = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpRepeatedAtom_Pack;
  CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpRepeatedAtom_Unpack;
  CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_repeatedatomobj__size__;
  CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_repeatedatomobj__type__;
  return (PyObject*)self;
}

static void
cp_repeatedatomobj_dealloc(CpRepeatedAtomObject* self)
{
  CpBuiltinAtom_CATOM(self).ob_bits = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_size = NULL;
  CpBuiltinAtom_CATOM(self).ob_type = NULL;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_repeatedatomobj_init(CpRepeatedAtomObject* self,
                        PyObject* args,
                        PyObject* kw)
{
  static char* kwlist[] = { "atom", "length", NULL };
  PyObject *atom = NULL, *length = NULL;

  if (!PyArg_ParseTupleAndKeywords(args, kw, "OO", kwlist, &atom, &length)) {
    return -1;
  }
  _Cp_SetObj(self->m_atom, atom);
  _Cp_SetObj(self->m_length, length);
  return 0;
}

static PyObject*
cp_repeatedatomobj_set_byteorder(CpRepeatedAtomObject* self,
                                 PyObject* args,
                                 PyObject* kw)
{
  static char* kwlist[] = { "byteorder", NULL };
  PyObject* byteorder = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &byteorder)) {
    return NULL;
  }
  if (!CpEndian_Check(byteorder)) {
    PyErr_SetString(PyExc_TypeError, "byteorder must be an Endian object");
    return NULL;
  }

  return CpEndian_SetEndian(self->m_atom, (CpEndianObject*)byteorder) ? NULL
                                                                      : Py_None;
}

/* Public API */

/*CpAPI*/
PyObject*
CpRepeatedAtom_GetLength(CpRepeatedAtomObject* self, PyObject* context)
{
  if (PyCallable_Check(self->m_length)) {
    PyObject* result = PyObject_CallOneArg(self->m_length, context);
    if (!result)
      return NULL;
    return result;
  }
  return Py_NewRef(self->m_length);
}

/*CpAPI*/
int
CpRepeatedAtom_Pack(CpRepeatedAtomObject* self,
                    PyObject* op,
                    CpLayerObject* layer)
{
  CpStateObject* state = layer->m_state;
  if (PyObject_HasAttr(self->m_atom, state->mod->str___pack_many__)) {
    // class explicitly defines __pack_many__ -> use it
    PyObject* res = CpAtom_Pack(
      self->m_atom, state->mod->str___pack_many__, op, (PyObject*)layer);
    PyObject* exc = NULL;
    if ((exc = PyErr_GetRaisedException(),
         exc && PyErr_GivenExceptionMatches(exc, PyExc_NotImplementedError))) {
      // Make sure this method continues to pack the given object
      Py_XDECREF(exc);
      PyErr_Clear();
      Py_XDECREF(res);
    } else {
      int success = res ? 0 : -1;
      Py_XDECREF(res);
      Py_XDECREF(exc);
      return success;
    }
  }

  if (!PySequence_Check(op)) {
    PyErr_Format(PyExc_TypeError, "input object (%R) is not a sequence", op);
    return -1;
  }

  CpSeqLayerObject* seq_layer = CpSeqLayer_New(state, layer);
  if (!seq_layer) {
    return -1;
  }

  Py_ssize_t size = PySequence_Size(op);
  bool greedy = false;
  Py_ssize_t layer_length = 0;
  PyObject* length = CpRepeatedAtom_GetLength(self, (PyObject*)layer);
  if (!length) {
    goto failure;
  }
  if (_CpPack_EvalLength(layer, length, size, &greedy, &layer_length) < 0) {
    Py_XDECREF(length);
    goto failure;
  }
  Py_XDECREF(length);

  if (layer_length <= 0) {
    // continue packing, here's nothing to store
    Py_XDECREF(seq_layer);
    return 0;
  }

  CpSeqLayer_SetSequence(seq_layer, op, layer_length, greedy);

  PyObject* obj = NULL;
  int success = 0;
  for (seq_layer->m_index = 0; seq_layer->m_index < seq_layer->m_length;
       seq_layer->m_index++) {
    obj = PySequence_GetItem(op, seq_layer->m_index);
    if (!obj) {
      goto failure;
    }
    seq_layer->ob_base.m_path = PyUnicode_FromFormat(
      "%s.%d", _PyUnicode_AsString(layer->m_path), seq_layer->m_index);
    if (!seq_layer->ob_base.m_path) {
      Py_XDECREF(obj);
      goto failure;
    }
    success = _Cp_Pack(obj, self->m_atom, (CpLayerObject*)seq_layer);
    Py_XSETREF(obj, NULL);
    if (success < 0) {
      goto failure;
    }
  }
  CpLayer_Invalidate((CpLayerObject*)seq_layer);
  return 0;
failure:
  CpLayer_Invalidate((CpLayerObject*)seq_layer);
  return -1;
}

/*CpAPI*/
PyObject*
CpRepeatedAtom_Unpack(CpRepeatedAtomObject* self, CpLayerObject* layer)
{
  _modulestate* mod = layer->m_state->mod;
  if (PyObject_HasAttr(self->m_atom, mod->str___unpack_many__)) {
    PyObject* res = PyObject_CallMethodOneArg(
      self->m_atom, mod->str___unpack_many__, (PyObject*)layer);
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
  length = CpRepeatedAtom_GetLength(self, (PyObject*)layer);
  if (!length) {
    goto fail;
  }
  if (_CpUnpack_EvalLength(layer, length, &seq_greedy, &seq_length) < 0) {
    goto fail;
  }
  CpSeqLayerObject* seq_layer = CpSeqLayer_New(layer->m_state, layer);
  if (!layer) {
    goto fail;
  }

  // REVISIT: add sequence factory here
  PyObject* seq = PyList_New(0);
  if (!seq) {
    goto fail;
  }

  CpSeqLayer_SetSequence(seq_layer, seq, seq_length, seq_greedy);
  while (seq_layer->s_greedy || (seq_layer->m_index < seq_layer->m_length)) {
    seq_layer->ob_base.m_path = PyUnicode_FromFormat(
      "%s.%d", _PyUnicode_AsString(layer->m_path), seq_layer->m_index);
    if (!seq_layer->ob_base.m_path) {
      goto fail;
    }

    Py_XSETREF(obj, _Cp_Unpack(self->m_atom, (CpLayerObject*)seq_layer));
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
  CpLayer_Invalidate((CpLayerObject*)seq_layer);
  seq_layer = NULL;
  return Py_NewRef(seq);

fail:
  Py_XDECREF(obj);
  Py_XDECREF(length);
  if (seq_layer) {
    CpLayer_Invalidate((CpLayerObject*)seq_layer);
  }
  return NULL;
}

/* type setup */
static PyMemberDef CpRepeatedAtom_Members[] = {
  { "length", T_OBJECT, offsetof(CpRepeatedAtomObject, m_length), READONLY },
  { "atom", T_OBJECT, offsetof(CpRepeatedAtomObject, m_atom), READONLY },
  { NULL }
};

static PyMethodDef CpRepeatedAtom_Methods[] = {
  { "__set_byteorder__",
    (PyCFunction)cp_repeatedatomobj_set_byteorder,
    METH_VARARGS,
    NULL },
  {
    NULL,
  }
};

PyTypeObject CpRepeatedAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpRepeatedAtom_NAME),
  .tp_basicsize = sizeof(CpRepeatedAtomObject),
  .tp_dealloc = (destructor)cp_repeatedatomobj_dealloc,
  .tp_repr = (reprfunc)cp_repeatedatomobj__repr__,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_new = (newfunc)cp_repeatedatomobj_new,
  .tp_init = (initproc)cp_repeatedatomobj_init,
  .tp_members = CpRepeatedAtom_Members,
  .tp_methods = CpRepeatedAtom_Methods,
};