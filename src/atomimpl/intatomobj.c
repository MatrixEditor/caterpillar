/* intatom C implementation */
#include <stdbool.h>

#include "caterpillar/caterpillar.h"

#include <structmember.h>

static PyObject*
cp_intatom__type__(CpIntAtomObject* self)
{
  return Py_XNewRef(&PyLong_Type);
}

static PyObject*
cp_intatom__size__(CpIntAtomObject* self, PyObject* ctx)
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

    CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpIntAtom_Pack;
    CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpIntAtom_Unpack;
    CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_intatom__size__;
    CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_intatom__type__;
    CpBuiltinAtom_CATOM(self).ob_bits = NULL;
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
  unsigned int bits = 0;
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

static PyObject*
cp_intatom_repr(CpIntAtomObject* self)
{
  char sign = 'i';
  if (!self->_m_signed) {
    sign = 'u';
  }
  char endian = 'l';
  if (!self->_m_little_endian) {
    endian = 'b';
  }
  return PyUnicode_FromFormat("<%ce %cint%d>", endian, sign, self->_m_bits);
}

static PyObject*
cp_intatom_set_byteorder(CpIntAtomObject* self, PyObject* args, PyObject* kw)
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

  return CpObject_Create(&CpIntAtom_Type,
                         "Iii",
                         (unsigned int)self->_m_bits,
                         self->_m_signed,
                         CpEndian_IsLittleEndian((CpEndianObject*)byteorder,
                                                 get_global_module_state()));
}

/* Public API */
/*CpAPI*/
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
  int res = _PyLong_AsByteArray((PyLongObject*)op,
                                (unsigned char*)PyBytes_AS_STRING(bytes),
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

/*CpAPI*/
PyObject*
CpIntAtom_Unpack(CpIntAtomObject* self, CpLayerObject* layer)
{
  PyObject* bytes = CpState_ReadSsize_t(layer->m_state, self->_m_byte_count);
  if (!bytes) {
    return NULL;
  }

  int little_endian = self->_m_little_endian;
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
  { "little_endian", T_BOOL, offsetof(CpIntAtomObject, _m_little_endian) },
  { NULL } /* Sentinel */
};

static PyMethodDef CpIntAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(intatom, NULL),
  { NULL } /* Sentinel */
};

PyTypeObject CpIntAtom_Type = { PyVarObject_HEAD_INIT(NULL, 0)
                                  _Cp_NameStr(CpIntAtom_NAME),
                                .tp_basicsize = sizeof(CpIntAtomObject),
                                .tp_dealloc = (destructor)cp_intatom_dealloc,
                                .tp_flags = Py_TPFLAGS_DEFAULT,
                                .tp_doc = NULL,
                                .tp_members = CpIntAtom_Members,
                                .tp_new = (newfunc)cp_intatom_new,
                                .tp_init = (initproc)cp_intatom_init,
                                .tp_repr = (reprfunc)cp_intatom_repr,
                                .tp_methods = CpIntAtom_Methods };
