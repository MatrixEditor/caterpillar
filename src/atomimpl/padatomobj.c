/* padding atom implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

static PyObject*
cp_paddingatom__type__(PyObject* self)
{
  return Py_XNewRef(&_PyNone_Type);
}

static PyObject*
cp_paddingatom__size__(PyObject* self, PyObject *ctx)
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
    CpFieldCAtom_CATOM(self).ob_pack = (packfunc)CpPaddingAtom_Pack;
    CpFieldCAtom_CATOM(self).ob_unpack = (unpackfunc)CpPaddingAtom_Unpack;
    CpFieldCAtom_CATOM(self).ob_pack_many =
      (packmanyfunc)CpPaddingAtom_PackMany;
    CpFieldCAtom_CATOM(self).ob_unpack_many =
      (unpackmanyfunc)CpPaddingAtom_UnpackMany;
    CpFieldCAtom_CATOM(self).ob_size = (sizefunc)cp_paddingatom__size__;
    CpFieldCAtom_CATOM(self).ob_type = (typefunc)cp_paddingatom__type__;
    CpFieldCAtom_CATOM(self).ob_bits = NULL;
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
                       CpLayerObject* layer)
{
#if 0
  /* value will be ignored here */
  PyObject *res = NULL, *bytes = NULL, *objSize = NULL, *objLengh = NULL;
  bool greedy = false;
  Py_ssize_t length = 0;

  if (!layer->m_field) {
    PyErr_SetString(PyExc_TypeError, "layer must have a field");
    return -1;
  }

  /* The following call will fail if the length is a prefixed statement
   * (slice)*/
  objLengh =
    CpField_GetLength((CpFieldObject*)layer->m_field, (PyObject*)layer);
  if (!objLengh) {
    return -1;
  }
  if (_CpPack_EvalLength(layer, objLengh, -1, &greedy, &length) < 0) {
    Py_XDECREF(objLengh);
    return -1;
  }
  Py_XDECREF(objLengh);

  if (length == 0) {
    return 0;
  } else if (length < 0) {
    PyErr_SetString(PyExc_ValueError, "length must be >= 0");
    return -1;
  } else if (greedy) {
    PyErr_SetString(PyExc_ValueError, "length must be >= 0 and not greedy!");
    return -1;
  }

  objSize = PyLong_FromSsize_t(length);
  if (!objSize) {
    return -1;
  }
  bytes = CpObject_CreateOneArg(&PyBytes_Type, objSize);
  if (!bytes) {
    Py_DECREF(objSize);
    return -1;
  }
  /* unsafe { */
  memset(PyBytes_AS_STRING(bytes), self->padding, length);
  /* } */
  res = CpState_Write(layer->m_state, bytes);
  Py_DECREF(bytes);
  Py_DECREF(objSize);
  if (!res) {
    return -1;
  }
  Py_XDECREF(res);
  return 0;
#endif
  return 0;
}

/*CpAPI*/
PyObject*
CpPaddingAtom_Unpack(CpPaddingAtomObject* self, CpLayerObject* layer)
{
  PyObject* res = CpState_Read(layer->m_state, 1);
  if (!res) {
    return NULL;
  }
  Py_XDECREF(res);
  return 0;
}

/*CpAPI*/
PyObject*
CpPaddingAtom_UnpackMany(CpPaddingAtomObject* self, CpLayerObject* layer)
{
#if 0
  PyObject *res = NULL, *bytes = NULL, *objLengh = NULL;
  bool greedy = false;
  Py_ssize_t length = 0, parsedLength = 0;

  objLengh =
    CpField_GetLength((CpFieldObject*)layer->m_field, (PyObject*)layer);
  if (!objLengh) {
    return NULL;
  }
  if (_CpPack_EvalLength(layer, objLengh, -1, &greedy, &length) < 0) {
    Py_DECREF(objLengh);
    return NULL;
  }
  Py_DECREF(objLengh);

  res = CpState_Read(layer->m_state, length);
  if (!res) {
    return NULL;
  }

  Py_XDECREF(res);
#endif
  Py_RETURN_NONE;
}

PyObject*
cp_paddingatom__repr__(CpPaddingAtomObject* self)
{
  return PyUnicode_FromFormat("padding(0x%02x)", self->padding);
}

/* type setup */
PyTypeObject CpPaddingAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpPaddingAtom_NAME),
  .tp_basicsize = sizeof(CpPaddingAtomObject),
  .tp_dealloc = (destructor)cp_paddingatom_dealloc,
  .tp_repr = (reprfunc)cp_paddingatom__repr__,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_doc = NULL,
  .tp_init = (initproc)cp_paddingatom_init,
  .tp_new = (newfunc)cp_paddingatom_new,
};