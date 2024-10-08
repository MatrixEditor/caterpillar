/* floatatom C implementation */
#include "caterpillar/caterpillar.h"
#include <structmember.h>

static PyObject*
cp_floatatom__type__(CpFloatAtomObject* self)
{
  return Py_XNewRef(&PyFloat_Type);
}

static PyObject*
cp_floatatom__size__(CpFloatAtomObject* self, PyObject* ctx)
{
  return Py_XNewRef(self->m_byte_count);
}

static PyObject*
cp_floatatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpFloatAtomObject* self = (CpFloatAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    self->m_byte_count = NULL;
    self->_m_bits = 0;
    self->_m_little_endian = true;

    CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpFloatAtom_Pack;
    CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpFloatAtom_Unpack;
    CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_floatatom__size__;
    CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_floatatom__type__;
    CpBuiltinAtom_CATOM(self).ob_bits = NULL;
  }
  return (PyObject*)self;
}

static void
cp_floatatom_dealloc(CpFloatAtomObject* self)
{
  Py_XDECREF(self->m_byte_count);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_floatatom_init(CpFloatAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "nbits", "little_endian", NULL };
  size_t bits = 0;
  int little_endian = true;
  if (!PyArg_ParseTupleAndKeywords(
        args, kwds, "I|p", kwlist, &bits, &little_endian)) {
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
  self->_m_little_endian = little_endian;
  self->m_byte_count = PyLong_FromUnsignedLong(self->_m_byte_count);
  if (!self->m_byte_count) {
    return -1;
  }
  return 0;
}

static PyObject*
cp_floatatom_set_byteorder(CpFloatAtomObject* self, PyObject* args, PyObject* kw)
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
                         "Ii",
                         self->_m_bits,
                         CpEndian_IsLittleEndian((CpEndianObject*)byteorder,
                                                 get_global_module_state()));
}

/* Public API */
/*CpAPI*/
int
CpFloatAtom_Pack(CpFloatAtomObject* self, PyObject* value, CpLayerObject* layer)
{
  if (!PyFloat_Check(value)) {
    PyErr_SetString(PyExc_TypeError, "value must be a float");
    return -1;
  }

  PyObject* bytes = CpObject_CreateOneArg(&PyBytes_Type, self->m_byte_count);
  if (!bytes) {
    return -1;
  }

  int little_endian = self->_m_little_endian;
  int res = 0;
  switch (self->_m_byte_count) {
    case 2: {
      res = PyFloat_Pack2(
        PyFloat_AS_DOUBLE(value), PyBytes_AS_STRING(bytes), little_endian);
      break;
    }
    case 4: {
      res = PyFloat_Pack4(
        PyFloat_AS_DOUBLE(value), PyBytes_AS_STRING(bytes), little_endian);
      break;
    }
    case 8: {
      res = PyFloat_Pack8(
        PyFloat_AS_DOUBLE(value), PyBytes_AS_STRING(bytes), little_endian);
      break;
    }
    default: {
      PyErr_SetString(PyExc_ValueError, "byte count must be 2, 4, or 8");
      res = -1;
      break;
    }
  }
  if (res == -1) {
    Py_XDECREF(bytes);
    return -1;
  }

  PyObject* result = CpState_Write(layer->m_state, bytes);
  Py_XDECREF(bytes);
  if (!result) {
    return -1;
  }
  Py_DECREF(result);
  return 0;
}

/*CpAPI*/
PyObject*
CpFloatAtom_Unpack(CpFloatAtomObject* self, CpLayerObject* layer)
{
  PyObject* bytes = CpState_ReadSsize_t(layer->m_state, self->_m_byte_count);
  if (!bytes) {
    return NULL;
  }

  int little_endian = self->_m_little_endian;
  double res;
  switch (self->_m_byte_count) {
    case 2: {
      res = PyFloat_Unpack2(((PyBytesObject*)bytes)->ob_sval, little_endian);
      break;
    }
    case 4: {
      res = PyFloat_Unpack4(((PyBytesObject*)bytes)->ob_sval, little_endian);
      break;
    }
    case 8: {
      res = PyFloat_Unpack8(((PyBytesObject*)bytes)->ob_sval, little_endian);
      break;
    }
    default: {
      PyErr_SetString(PyExc_ValueError, "byte count must be 2, 4, or 8");
      Py_DECREF(bytes);
      return NULL;
    }
  }

  PyObject* floatobj = PyFloat_FromDouble(res);
  Py_DECREF(bytes);
  return floatobj;
}

/* type */
static PyMemberDef CpFloatAtom_Members[] = {
  { "nbytes",
    T_PYSSIZET,
    offsetof(CpFloatAtomObject, _m_byte_count),
    READONLY,
    NULL },
  { "bits", T_PYSSIZET, offsetof(CpFloatAtomObject, _m_bits), READONLY, NULL },
  { "little_endian", T_BOOL, offsetof(CpFloatAtomObject, _m_little_endian) },
  { NULL } /* Sentinel */
};

static PyMethodDef CpFloatAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(floatatom, NULL),
  { NULL } /* Sentinel */
};

PyTypeObject CpFloatAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpFloatAtom_NAME),
  .tp_basicsize = sizeof(CpFloatAtomObject),
  .tp_dealloc = (destructor)cp_floatatom_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_members = CpFloatAtom_Members,
  .tp_methods = CpFloatAtom_Methods,
  .tp_init = (initproc)cp_floatatom_init,
  .tp_new = (newfunc)cp_floatatom_new,
};