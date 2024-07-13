/* intatom C implementation */
#include "caterpillar/atoms/int.h"
#include "caterpillar/arch.h"
#include <structmember.h>

static PyObject*
cp_intatom__type__(CpIntAtomObject* self)
{
  return Py_XNewRef(&PyLong_Type);
}

static PyObject *
cp_intatom__size__(CpIntAtomObject* self, PyObject *ctx)
{
  return Py_XNewRef(self->m_byte_count);
}

static PyObject*
cp_intatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpIntAtomObject* self = (CpIntAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    self->m_byte_count = NULL;
    self->_m_bits = 0;
    self->_m_signed = true;
    self->_m_little_endian = true;

    CpFieldCAtom_CATOM(self).ob_pack = (packfunc)CpIntAtom_Pack;
    CpFieldCAtom_CATOM(self).ob_unpack = (unpackfunc)CpIntAtom_Unpack;
    CpFieldCAtom_CATOM(self).ob_pack_many = NULL;
    CpFieldCAtom_CATOM(self).ob_unpack_many = NULL;
    CpFieldCAtom_CATOM(self).ob_size = (sizefunc)cp_intatom__size__;
    CpFieldCAtom_CATOM(self).ob_type = (typefunc)cp_intatom__type__;
    CpFieldCAtom_CATOM(self).ob_bits = NULL;
  }
  return (PyObject*)self;
}

static void
cp_intatom_dealloc(CpIntAtomObject* self)
{
  Py_XDECREF(self->m_byte_count);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_intatom_init(CpIntAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "nbits", "signed", "little_endian", NULL };
  int _signed = true, little_endian = true;
  size_t bits = 0;
  if (!PyArg_ParseTupleAndKeywords(
        args, kwds, "I|pp", kwlist, &bits, &_signed, &little_endian)) {
    return -1;
  }
  if (bits == 0) {
    PyErr_SetString(PyExc_ValueError, "bytes cannot be zero");
    return -1;
  }
  if (bits % 8) {
    PyErr_SetString(PyExc_ValueError, "nbits must be a multiple of 8");
    return -1;
  }

  self->_m_bits = bits;
  self->_m_byte_count = bits / 8;
  self->_m_signed = _signed;
  self->_m_little_endian = little_endian;
  self->m_byte_count = PyLong_FromUnsignedLong(self->_m_byte_count);
  if (!self->m_byte_count) {
    return -1;
  }
  return 0;
}



/* Public API */
int
CpIntAtom_Pack(CpIntAtomObject* self, PyObject* op, CpLayerObject* layer)
{
  PyObject* bytes = CpObject_CreateOneArg(&PyBytes_Type, self->m_byte_count);
  if (!bytes) {
    return -1;
  }

  if (!PyLong_Check(op)) {
    PyErr_Format(PyExc_TypeError, "op must be an int, got %R", op);
    Py_DECREF(bytes);
  }

  int little_endian = self->_m_little_endian;
  if (layer->m_field) {
    _modulestate *mod = layer->m_state->mod;
    PyObject *endian = ((CpFieldObject *)layer->m_field)->m_endian;

    if (CpEndian_Check(endian))
    /* If the field has an endian specified, use that. */
    little_endian = CpEndian_IsLittleEndian((CpEndianObject *)endian, mod);
  }

  int res = _PyLong_AsByteArray((PyLongObject*)op,
                                (unsigned char*)PyBytes_AS_STRING(op),
                                self->_m_byte_count,
                                little_endian,
                                self->_m_signed);
  if (res == -1) {
    return -1;
  }

  PyObject* result = CpState_Write(layer->m_state, bytes);
  if (!result) {
    return -1;
  }
  Py_DECREF(result);
  return 0;
}

PyObject*
CpIntAtom_Unpack(CpIntAtomObject* self, CpLayerObject* layer)
{
  PyObject* bytes = CpState_Read(layer->m_state, self->_m_byte_count);
  if (!bytes) {
    return NULL;
  }

  int little_endian = self->_m_little_endian;
  if (layer->m_field) {
    _modulestate *mod = layer->m_state->mod;
    PyObject *endian = ((CpFieldObject *)layer->m_field)->m_endian;

    if (CpEndian_Check(endian))
    /* If the field has an endian specified, use that. */
    little_endian = CpEndian_IsLittleEndian((CpEndianObject *)endian, mod);
  }

  PyObject* obj =
    _PyLong_FromByteArray((unsigned char*)PyBytes_AS_STRING(bytes),
                          self->_m_byte_count,
                          little_endian,
                          self->_m_signed);
  Py_DECREF(bytes);
  return obj;
}

/* docs */

/* type */
static PyMemberDef CpIntAtom_Members[] = {
  { "nbytes",
    T_PYSSIZET,
    offsetof(CpIntAtomObject, _m_byte_count),
    READONLY,
    NULL },
  { "nbits", T_PYSSIZET, offsetof(CpIntAtomObject, _m_bits), READONLY, NULL },
  { "signed", T_BOOL, offsetof(CpIntAtomObject, _m_signed), READONLY, NULL },
  { "little_endian",
    T_BOOL,
    offsetof(CpIntAtomObject, _m_little_endian),
    NULL,
    NULL },
  { NULL } /* Sentinel */
};

PyTypeObject CpIntAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(intatom),
  sizeof(CpIntAtomObject),        /* tp_basicsize */
  0,                              /* tp_itemsize */
  (destructor)cp_intatom_dealloc, /* tp_dealloc */
  0,                              /* tp_vectorcall_offset */
  0,                              /* tp_getattr */
  0,                              /* tp_setattr */
  0,                              /* tp_as_async */
  0,                              /* tp_repr */
  0,                              /* tp_as_number */
  0,                              /* tp_as_sequence */
  0,                              /* tp_as_mapping */
  0,                              /* tp_hash */
  0,                              /* tp_call */
  0,                              /* tp_str */
  0,                              /* tp_getattro */
  0,                              /* tp_setattro */
  0,                              /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,             /* tp_flags */
  NULL,                           /* tp_doc */
  0,                              /* tp_traverse */
  0,                              /* tp_clear */
  0,                              /* tp_richcompare */
  0,                              /* tp_weaklistoffset */
  0,                              /* tp_iter */
  0,                              /* tp_iternext */
  0,                              /* tp_methods */
  CpIntAtom_Members,              /* tp_members */
  0,                              /* tp_getset */
  0,                              /* tp_base */
  0,                              /* tp_dict */
  0,                              /* tp_descr_get */
  0,                              /* tp_descr_set */
  0,                              /* tp_dictoffset */
  (initproc)cp_intatom_init,      /* tp_init */
  0,                              /* tp_alloc */
  (newfunc)cp_intatom_new,        /* tp_new */
  0,                              /* tp_free */
  0,                              /* tp_is_gc */
  0,                              /* tp_bases */
  0,                              /* tp_mro */
  0,                              /* tp_cache */
  0,                              /* tp_subclasses */
  0,                              /* tp_weaklist */
  0,                              /* tp_del */
  0,                              /* tp_version_tag */
  0,                              /* tp_finalize */
  0,                              /* tp_vectorcall */
  0,                              /* tp_watched */
};