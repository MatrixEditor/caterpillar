/* padding atom implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

static PyObject*
cp_paddingatom_type(PyObject* self)
{
  return Py_XNewRef(&_PyNone_Type);
}

static PyObject*
cp_paddingatom_size(PyObject* self, PyObject* ctx)
{
  /* NOTE:
  We are using the size of one byte here to allow padding atoms to be
  statically sized. It helps size calculation as well as defines the
  default size for padding atoms.
  */
  return PyLong_FromSize_t(1);
}

static PyObject*
cp_paddingatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpPaddingAtomObject* self = (CpPaddingAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpPaddingAtom_Pack;
    CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpPaddingAtom_Unpack;
    CpBuiltinAtom_CATOM(self).ob_pack_many =
      (packmanyfunc)CpPaddingAtom_PackMany;
    CpBuiltinAtom_CATOM(self).ob_unpack_many =
      (unpackmanyfunc)CpPaddingAtom_UnpackMany;
    CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_paddingatom_size;
    CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_paddingatom_type;
    CpBuiltinAtom_CATOM(self).ob_bits = NULL;
  }
  return (PyObject*)self;
}

static void
cp_paddingatom_dealloc(CpPaddingAtomObject* self)
{
  self->padding = 0;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_paddingatom_init(CpPaddingAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "pad", NULL };
  char value = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|b", kwlist, &value))
    return -1;

  self->padding = value;
  return 0;
}

/* Public API */
/*CpAPI*/
int
CpPaddingAtom_Pack(CpPaddingAtomObject* self,
                   PyObject* value,
                   CpLayerObject* layer)
{
  /* value will be ignored here */
  PyObject* res;
  if (!self->padding) {
    res = CpState_Write(layer->m_state, layer->m_state->mod->cp_bytes__false);
  } else {
    PyObject* bytes = PyBytes_FromStringAndSize((char*)&self->padding, 1);
    if (!bytes) {
      return -1;
    }
    res = CpState_Write(layer->m_state, bytes);
    Py_DECREF(bytes);
  }

  if (!res) {
    return -1;
  }
  Py_XDECREF(res);
  return 0;
}

/*CpAPI*/
int
CpPaddingAtom_PackMany(CpPaddingAtomObject* self,
                       PyObject* value,
                       CpLayerObject* layer,
                       CpLengthInfoObject* lengthinfo)
{
  PyObject* objSize = PyLong_FromSsize_t(lengthinfo->m_length);
  if (!objSize) {
    return -1;
  }

  PyObject* bytes = CpObject_CreateOneArg(&PyBytes_Type, objSize);
  if (!bytes) {
    Py_DECREF(objSize);
    return -1;
  }
  /* unsafe { */
  memset(PyBytes_AS_STRING(bytes), self->padding, lengthinfo->m_length);
  /* } */
  PyObject* res = CpState_Write(layer->m_state, bytes);
  Py_DECREF(bytes);
  Py_DECREF(objSize);
  if (!res) {
    return -1;
  }
  Py_XDECREF(res);
  return 0;
}

/*CpAPI*/
PyObject*
CpPaddingAtom_Unpack(CpPaddingAtomObject* self, CpLayerObject* layer)
{
  PyObject* res = CpState_ReadSsize_t(layer->m_state, 1);
  if (!res) {
    return NULL;
  }
  Py_XDECREF(res);
  Py_RETURN_NONE;
}

/*CpAPI*/
PyObject*
CpPaddingAtom_UnpackMany(CpPaddingAtomObject* self,
                         CpLayerObject* layer,
                         CpLengthInfoObject* lengthinfo)
{
  PyObject* res = NULL;

  if (lengthinfo->m_greedy) {
    res = CpState_ReadFully(layer->m_state);
  } else {
    res = CpState_ReadSsize_t(layer->m_state, lengthinfo->m_length);
  }

  if (!res) {
    return NULL;
  }

  Py_ssize_t length = PyBytes_GET_SIZE(res);
  Py_ssize_t offset = 0;
  const char* ptr = PyBytes_AS_STRING(res);
  while (offset < length && *(ptr + offset) == self->padding) {
    offset++;
  }
  if (offset != length) {
    PyErr_Format(PyExc_ValueError,
                 ("The parsed padding contains invalid padding characters "
                  "(possible padding overflow?). "
                  "Expected %ld bytes of 0x%02x but parsed only %ld bytes."),
                 length,
                 self->padding,
                 offset);
    Py_XDECREF(res);
    return NULL;
  }

  Py_XDECREF(res);
  Py_RETURN_NONE;
}

PyObject*
cp_paddingatom_repr(CpPaddingAtomObject* self)
{
  if (self->padding == 0) {
    return PyUnicode_FromFormat("<padding>");
  }
  return PyUnicode_FromFormat("<padding [0x%02x]>", self->padding);
}

/* type setup */
PyTypeObject CpPaddingAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpPaddingAtom_NAME),
  .tp_basicsize = sizeof(CpPaddingAtomObject),
  .tp_dealloc = (destructor)cp_paddingatom_dealloc,
  .tp_repr = (reprfunc)cp_paddingatom_repr,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_doc = NULL,
  .tp_init = (initproc)cp_paddingatom_init,
  .tp_new = (newfunc)cp_paddingatom_new,
};