/* charatom C implementation */
#include "caterpillar/atoms/primitive.h"
#include "caterpillar/state.h"
#include <structmember.h>

static PyObject*
cp_charatom__type__(CpCharAtomObject* self)
{
  return Py_XNewRef(&PyBytes_Type);
}

static PyObject*
cp_charatom__size__(CpCharAtomObject* self, PyObject *ctx)
{
  return PyLong_FromSize_t(1);
}

static PyObject*
cp_charatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpCharAtomObject* self = (CpCharAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    CpFieldCAtom_CATOM(self).ob_pack = (packfunc)CpCharAtom_Pack;
    CpFieldCAtom_CATOM(self).ob_unpack = (unpackfunc)CpCharAtom_Unpack;
    CpFieldCAtom_CATOM(self).ob_pack_many = NULL;
    CpFieldCAtom_CATOM(self).ob_unpack_many = NULL;
    CpFieldCAtom_CATOM(self).ob_size = (sizefunc)cp_charatom__size__;
    CpFieldCAtom_CATOM(self).ob_type = (typefunc)cp_charatom__type__;
    CpFieldCAtom_CATOM(self).ob_bits = NULL;
  }
  return (PyObject*)self;
}

static void
cp_charatom_dealloc(CpCharAtomObject* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_charatom_init(CpCharAtomObject* self, PyObject* args, PyObject* kwds)
{
  _Cp_InitNoArgs(charatom, args, kwds);
}

/* Public API */

int
CpCharAtom_Pack(CpCharAtomObject* self, PyObject* value, CpLayerObject* layer)
{
  if (PyBytes_Check(value)) {
    PyErr_SetString(PyExc_TypeError, "can only pack bytes objects");
    return -1;
  }

  if (PyBytes_Size(value) != 1) {
    PyErr_SetString(PyExc_TypeError, "can only pack one-sized bytes");
    return -1;
  }

  PyObject* res = CpState_Write(layer->m_state, value);
  if (!res) {
    return -1;
  }
  Py_XDECREF(res);
  return 0;
}

PyObject*
CpCharAtom_Unpack(CpCharAtomObject* self, CpLayerObject* layer)
{
  PyObject* res = CpState_Read(layer->m_state, 1);
  if (!res) {
    return NULL;
  }
  return res;
}

/* type setup */
PyTypeObject CpCharAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(charatom),
  .tp_basicsize = sizeof(CpCharAtomObject),
  .tp_dealloc = (destructor)cp_charatom_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_doc = NULL,
  .tp_init = (initproc)cp_charatom_init,
  .tp_new = (newfunc)cp_charatom_new,
};