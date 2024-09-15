/* offset atom implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

/* impl */
static PyObject*
cp_offsetatom_type(CpOffsetAtomObject* self)
{
  return CpTypeOf(self->m_atom);
}

static PyObject*
cp_offsetatom_size(CpOffsetAtomObject* self, CpLayerObject* layer)
{
  return _Cp_SizeOf(self->m_atom, layer);
}

static PyObject*
cp_offsetatom_repr(CpOffsetAtomObject* self)
{
  return PyUnicode_FromFormat(
    "<atoffset [<%s>] %R>", Py_TYPE(self->m_offset)->tp_name, self->m_atom);
}

static PyObject*
cp_offsetatom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpOffsetAtomObject* self = (CpOffsetAtomObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  CpBuiltinAtom_CATOM(self).ob_bits = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpOffsetAtom_Pack;
  CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpOffsetAtom_Unpack;
  CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_offsetatom_size;
  CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_offsetatom_type;
  self->m_offset = 0;
  self->m_atom = NULL;
  return (PyObject*)self;
}

static void
cp_offsetatom_dealloc(CpOffsetAtomObject* self)
{
  CpBuiltinAtom_CATOM(self).ob_bits = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_size = NULL;
  CpBuiltinAtom_CATOM(self).ob_type = NULL;
  Py_CLEAR(self->m_atom);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_offsetatom_init(CpOffsetAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "offset", "atom", "whence", NULL };
  PyObject *offset = NULL, *atom = NULL;
  int whence = 0;
  if (!PyArg_ParseTupleAndKeywords(
        args, kw, "OO|i", kwlist, &atom, &offset, &whence))
    return -1;

  _Cp_SetObj(self->m_atom, atom);
  _Cp_SetObj(self->m_offset, offset);
  self->m_whence = PyLong_FromLong(whence);
  if (!self->m_whence) {
    return -1;
  }
  self->s_is_number = PyNumber_Check(self->m_offset);
  return 0;
}

_CpEndian_ImplSetByteorder(CpOffsetAtomObject, offsetatom, self->m_atom);

static PyObject*
cp_offsetatom_get_offset(CpOffsetAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "layer", NULL };
  PyObject* layer = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &layer))
    return NULL;
  return CpOffsetAtom_GetOffset(self, layer);
}

/* Public API */

/*CpAPI*/
PyObject*
CpOffsetAtom_GetOffset(CpOffsetAtomObject* self, PyObject* layer)
{
  if (self->s_is_number) {
    return Py_NewRef(self->m_offset);
  }

  // asset offset is callable
  return PyObject_CallOneArg(self->m_offset, layer);
}

/*CpAPI*/
int
CpOffsetAtom_Pack(CpOffsetAtomObject* self, PyObject* obj, CpLayerObject* layer)
{
  // TODO: implement offset table
  PyObject* fallback = CpState_Tell(layer->m_state);
  if (!fallback) {
    return -1;
  }

  PyObject* res = CpState_Seek(layer->m_state, self->m_offset, self->m_whence);
  if (!res) {
    return -1;
  }
  Py_DECREF(res);

  if (_Cp_Pack(obj, self->m_atom, layer) < 0) {
    return -1;
  }

  res = CpState_Seek(layer->m_state, fallback, PyLong_FromLong(0));
  if (!res) {
    return -1;
  }
  Py_DECREF(res);
  return 0;
}

/*CpAPI*/
PyObject*
CpOffsetAtom_Unpack(CpOffsetAtomObject* self, CpLayerObject* layer)
{
  PyObject* fallback = CpState_Tell(layer->m_state);
  if (!fallback) {
    return NULL;
  }

  PyObject* res = CpState_Seek(layer->m_state, self->m_offset, self->m_whence);
  if (!res) {
    return NULL;
  }
  Py_DECREF(res);

  PyObject* result = _Cp_Unpack(self->m_atom, layer);
  if (!result) {
    return NULL;
  }

  res = CpState_Seek(layer->m_state, fallback, PyLong_FromLong(0));
  if (!res) {
    return NULL;
  }
  Py_DECREF(res);
  return result;
}

/* docs */

/* members */

static PyMemberDef CpOffsetAtom_Members[] = {
  { "offset", T_OBJECT_EX, offsetof(CpOffsetAtomObject, m_offset), READONLY },
  { "whence", T_OBJECT_EX, offsetof(CpOffsetAtomObject, m_whence), READONLY },
  { NULL } /* Sentinel */
};

static PyMethodDef CpOffsetAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(offsetatom, NULL),
  { "get_offset",
    (PyCFunction)cp_offsetatom_get_offset,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { NULL } /* Sentinel */
};

PyTypeObject CpOffsetAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpOffsetAtom_NAME),
  .tp_basicsize = sizeof(CpOffsetAtomObject),
  .tp_members = CpOffsetAtom_Members,
  .tp_methods = CpOffsetAtom_Methods,
  .tp_init = (initproc)cp_offsetatom_init,
  .tp_dealloc = (destructor)cp_offsetatom_dealloc,
  .tp_repr = (reprfunc)cp_offsetatom_repr,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_new = (newfunc)cp_offsetatom_new,
};
