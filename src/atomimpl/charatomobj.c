/* charatom C implementation */
#include "caterpillar/atoms/primitive.h"
#include <structmember.h>

static PyObject*
cp_charatom__type__(CpCharAtomObject* self)
{
  return Py_XNewRef(&PyBytes_Type);
}

static PyObject*
cp_charatom__size__(CpCharAtomObject* self)
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
  sizeof(CpCharAtomObject),        /* tp_basicsize */
  0,                               /* tp_itemsize */
  (destructor)cp_charatom_dealloc, /* tp_dealloc */
  0,                               /* tp_vectorcall_offset */
  0,                               /* tp_getattr */
  0,                               /* tp_setattr */
  0,                               /* tp_as_async */
  0,                               /* tp_repr */
  0,                               /* tp_as_number */
  0,                               /* tp_as_sequence */
  0,                               /* tp_as_mapping */
  0,                               /* tp_hash */
  0,                               /* tp_call */
  0,                               /* tp_str */
  0,                               /* tp_getattro */
  0,                               /* tp_setattro */
  0,                               /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,              /* tp_flags */
  NULL,                            /* tp_doc */
  0,                               /* tp_traverse */
  0,                               /* tp_clear */
  0,                               /* tp_richcompare */
  0,                               /* tp_weaklistoffset */
  0,                               /* tp_iter */
  0,                               /* tp_iternext */
  0,                               /* tp_methods */
  0,                               /* tp_members */
  0,                               /* tp_getset */
  0,                               /* tp_base */
  0,                               /* tp_dict */
  0,                               /* tp_descr_get */
  0,                               /* tp_descr_set */
  0,                               /* tp_dictoffset */
  (initproc)cp_charatom_init,      /* tp_init */
  0,                               /* tp_alloc */
  (newfunc)cp_charatom_new,        /* tp_new */
  0,                               /* tp_free */
  0,                               /* tp_is_gc */
  0,                               /* tp_bases */
  0,                               /* tp_mro */
  0,                               /* tp_cache */
  0,                               /* tp_subclasses */
  0,                               /* tp_weaklist */
  0,                               /* tp_del */
  0,                               /* tp_version_tag */
  0,                               /* tp_finalize */
  0,                               /* tp_vectorcall */
  0,                               /* tp_watched */
};