/* varint implementation for Little Endian and Big Endian */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

// Inspired by https://github.com/google/cityhash/blob/master/src/city.cc
#ifdef _MSC_VER
#include <stdint.h>
#define CP_BSWAP_U32(x) _byteswap_ulong(x)
#define CP_BSWAP_U64(x) _byteswap_uint64(x)

#elif defined(__APPLE__)
#include <libkern/OSByteOrder.h>
#define CP_BSWAP_U32(x) OSSwapInt32(x)
#define CP_BSWAP_U64(x) OSSwapInt64(x)

#elif defined(sun) || defined(__sun)
#include <sys/byteorder.h>
#define CP_BSWAP_U32(x) BSWAP_32(x)
#define CP_BSWAP_U64(x) BSWAP_64(x)

#elif defined(__FreeBSD__)
#include <sys/endian.h>
#define CP_BSWAP_U32(x) bswap32(x)
#define CP_BSWAP_U64(x) bswap64(x)

#elif defined(__OpenBSD__)
#include <sys/types.h>
#define CP_BSWAP_U32(x) swap32(x)
#define CP_BSWAP_U64(x) swap64(x)

#else
#include <byteswap.h>
#define CP_BSWAP_U32(x) bswap_32(x)
#define CP_BSWAP_U64(x) bswap_64(x)
#endif

/* impl */
static PyObject*
cp_varintatom_type(PyObject* self)
{
  return Py_XNewRef(&PyLong_Type);
}

static PyObject*
cp_varintatom_size(CpVarIntAtomObject* self, PyObject* ctx)
{
  PyErr_SetString(PyExc_TypeError, "VarInts do not have a static size!");
  return NULL;
}

static PyObject*
cp_varintatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpVarIntAtomObject* self = (CpVarIntAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    self->_m_little_endian = true;
    self->_m_lsb = false;

    CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpVarIntAtom_Pack;
    CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpVarIntAtom_Unpack;
    CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_varintatom_size;
    CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_varintatom_type;
    CpBuiltinAtom_CATOM(self).ob_bits = NULL;
  }
  return (PyObject*)self;
}

static void
cp_varintatom_dealloc(CpVarIntAtomObject* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_varintatom_init(CpVarIntAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "little_endian", "lsb", NULL };
  int little_endian = true;
  int lsb = false;
  if (!PyArg_ParseTupleAndKeywords(
        args, kwds, "|pp", kwlist, &little_endian, &lsb)) {
    return -1;
  }
  self->_m_little_endian = little_endian;
  self->_m_lsb = lsb;
  return 0;
}

static PyObject*
cp_varintatom_repr(CpVarIntAtomObject* self)
{
  char endian = 'l';
  if (!self->_m_little_endian) {
    endian = 'b';
  }
  if (self->_m_lsb) {
    return PyUnicode_FromFormat("<%ce varint [lsb]>", endian);
  }
  return PyUnicode_FromFormat("<%ce varint>", endian);
}

static PyObject*
cp_varintatom_set_byteorder(CpVarIntAtomObject* self,
                            PyObject* args,
                            PyObject* kw)
{
  _CpEndian_KwArgsGetByteorder(NULL);

  _modulestate* mod = get_global_module_state();
  int little_endian = CpEndian_IsLittleEndian((CpEndianObject*)byteorder, mod);
  PyObject* new_varint =
    (PyObject*)CpVarIntAtom_New(little_endian, self->_m_lsb);

  Py_DECREF(byteorder);
  return new_varint;
}

/* Public API */

#define _CP_VARINT_BSWAP_IMPL(name, type)                                      \
  PyObject* result_int = PyLong_From##name(number);                            \
  if (!result_int) {                                                           \
    return 0;                                                                  \
  }                                                                            \
  PyObject* result = CpVarIntAtom_BSwap(result_int, little_endian);            \
  Py_DECREF(result_int);                                                       \
  if (!result) {                                                               \
    return 0;                                                                  \
  }                                                                            \
  type res = PyLong_As##name(result);                                          \
  Py_DECREF(result);                                                           \
  return res;

/*CpAPI*/
unsigned long long
CpVarIntAtom_BSwapUnsignedLongLong(unsigned long long number,
                                   bool little_endian)
{
  _CP_VARINT_BSWAP_IMPL(UnsignedLongLong, unsigned long long);
}

/*CpAPI*/
long long
CpVarIntAtom_BSwapLongLong(long long number, bool little_endian)
{
  _CP_VARINT_BSWAP_IMPL(LongLong, long long);
}

/*CpAPI*/
Py_ssize_t
CpVarIntAtom_BSwapSsize_t(Py_ssize_t number, bool little_endian)
{
  _CP_VARINT_BSWAP_IMPL(Ssize_t, Py_ssize_t);
}

#undef _CP_VARINT_BSWAP_IMPL

/*CpAPI*/
PyObject*
CpVarIntAtom_BSwap(PyObject* number, bool little_endian)
{
  size_t nbytes = _PyLong_NumBits(number) / 8;
  PyObject* bytesSize = PyLong_FromSize_t(nbytes);
  if (!bytesSize) {
    return NULL;
  }

  PyObject* bytes = CpObject_CreateOneArg(&PyBytes_Type, bytesSize);
  if (!bytes) {
    Py_DECREF(bytesSize);
    return NULL;
  }

  int res = _PyLong_AsByteArray((PyLongObject*)number,
                                (unsigned char*)PyBytes_AS_STRING(bytes),
                                nbytes,
                                little_endian,
                                false);
  if (res == -1) {
    Py_DECREF(bytesSize);
    Py_DECREF(bytes);
    return NULL;
  }

  PyObject* result = _PyLong_FromByteArray(
    (unsigned char*)PyBytes_AS_STRING(bytes), nbytes, !little_endian, false);

  Py_DECREF(bytesSize);
  Py_DECREF(bytes);
  return result;
}

PyObject*
_CpVarIntAtom_Length(unsigned long long number)
{
  if (number == 0) {
    return PyLong_FromLong(1);
  }
  int length = 1;
  while ((number >> 7) != 0) {
    number >>= 7;
    length++;
  }
  return PyLong_FromLong(length);
}

/*CpAPI*/
int
CpVarIntAtom_Pack(CpVarIntAtomObject* self,
                  PyObject* value,
                  CpLayerObject* layer)
{
  unsigned long long raw_value = PyLong_AsUnsignedLongLongMask(value);
  if (PyErr_Occurred()) {
    return -1;
  }

  int little_endian = self->_m_little_endian;
  int lsb = self->_m_lsb;

  PyObject* length = _CpVarIntAtom_Length(raw_value);
  if (!length) {
    return -1;
  }

  PyObject* bytes = CpObject_CreateOneArg(&PyBytes_Type, length);
  Py_DECREF(length);
  if (!bytes) {
    return -1;
  }

  int raw_length = PyBytes_GET_SIZE(bytes);
  for (int i = 0; i < raw_length; i++) {
    unsigned char byte = 0;
    if (little_endian) {
      byte = (raw_value >> (i * 7)) & 0x7f;
    } else {
      byte = (raw_value >> ((raw_length - 1 - i) * 7)) & 0x7f;
    }
    if (!lsb && i != raw_length - 1) {
      byte |= 0x80;
    } else if (lsb && (i == raw_length - 1)) {
      byte |= 0x80;
    }

    PyBytes_AS_STRING(bytes)[i] = byte;
  }

  PyObject* result = CpState_Write(layer->m_state, bytes);
  Py_DECREF(bytes);
  if (!result) {
    return -1;
  }
  Py_DECREF(result);
  return 0;
}

/*CpAPI*/
PyObject*
CpVarIntAtom_Unpack(CpVarIntAtomObject* self, CpLayerObject* layer)
{
  PyObject* tmp_val = NULL;
  unsigned long long result = 0, tmp = 0;
  int shift = 0;
  int little_endian = self->_m_little_endian;
  int lsb = self->_m_lsb;
  int nbytes = 0;

  while (true) {
    tmp_val = CpState_ReadSsize_t(layer->m_state, 1);
    if (!tmp_val) {
      return NULL;
    }
    // only one byte
    tmp = *(PyBytes_AS_STRING(tmp_val));
    Py_DECREF(tmp_val);

    result |= (tmp & 0x7f) << shift;
    shift += 7;
    nbytes++;
    if ((lsb && (tmp & 0x80) == 1) || (!lsb && (tmp & 0x80) == 0)) {
      break;
    }
  }

  if (!little_endian) {
    if (nbytes == 1) {
      // no swap needed
    } else if (nbytes == 2) {
      // manually swap
      // TODO: explain why we use 7 bits here
      result = ((result >> 7) & 0xff) | ((result << 7) & 0xff00);
    } else if (nbytes <= 4) {
      // swap using compiler directive
      result = CP_BSWAP_U32(result);
    } else if (nbytes <= 8) {
      // compiler directive
      result = CP_BSWAP_U64(result);
    } else {
      // use Python methods
      result = CpVarIntAtom_BSwapUnsignedLongLong(result, true);
      if (PyErr_Occurred()) {
        return NULL;
      }
    }
  }

  return PyLong_FromUnsignedLongLong(result);
}

/* docs */

/* type setup */
static PyMemberDef CpVarIntAtom_Members[] = {
  { "little_endian",
    T_BOOL,
    offsetof(CpVarIntAtomObject, _m_little_endian),
    READONLY },
  { "lsb", T_BOOL, offsetof(CpVarIntAtomObject, _m_lsb), READONLY },
  { NULL }
};

static PyMethodDef CpVarIntAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(varintatom, NULL),
  { NULL } /* Sentinel */
};

PyTypeObject CpVarIntAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpVarIntAtom_NAME),
  .tp_basicsize = sizeof(CpVarIntAtomObject),
  .tp_dealloc = (destructor)cp_varintatom_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_members = CpVarIntAtom_Members,
  .tp_methods = CpVarIntAtom_Methods,
  .tp_init = (initproc)cp_varintatom_init,
  .tp_new = (newfunc)cp_varintatom_new,
  .tp_repr = (reprfunc)cp_varintatom_repr,
};
