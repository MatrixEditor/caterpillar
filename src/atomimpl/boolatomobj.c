/* boolatom C implementation */
#include "caterpillar/atoms/primitive.h"
#include <structmember.h>

static PyObject*
cp_boolatom__type__(CpBoolAtomObject* self)
{
  return Py_XNewRef(&PyBool_Type);
}

static PyObject*
cp_boolatom__size__(CpBoolAtomObject* self)
{
  return PyLong_FromSize_t(1);
}

static PyObject*
cp_boolatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpBoolAtomObject* self = (CpBoolAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    CpFieldCAtom_CATOM(self).ob_pack = (packfunc)CpBoolAtom_Pack;
    CpFieldCAtom_CATOM(self).ob_unpack = (unpackfunc)CpBoolAtom_Unpack;
    CpFieldCAtom_CATOM(self).ob_pack_many = NULL;
    CpFieldCAtom_CATOM(self).ob_unpack_many = NULL;
    CpFieldCAtom_CATOM(self).ob_size = (sizefunc)cp_boolatom__size__;
    CpFieldCAtom_CATOM(self).ob_type = (typefunc)cp_boolatom__type__;
    CpFieldCAtom_CATOM(self).ob_bits = NULL;
  }
  return (PyObject*)self;
}

static void
cp_boolatom_dealloc(CpBoolAtomObject* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_boolatom_init(CpBoolAtomObject* self, PyObject* args, PyObject* kwds)
{
  return 0;
}

/* Public API */

int
CpBoolAtom_Pack(CpBoolAtomObject* self, PyObject* value, CpLayerObject* layer)
{
  PyObject* res;
  if (value == Py_True) {
    res = CpState_Write(layer->m_state, layer->m_state->mod->cp_bytes__true);
  } else {
    res = CpState_Write(layer->m_state, layer->m_state->mod->cp_bytes__false);
  }

  if (!res) {
    return -1;
  }
  Py_XDECREF(res);
  return 0;
}

PyObject*
CpBoolAtom_Unpack(CpBoolAtomObject* self, CpLayerObject* layer)
{
  PyObject* res;
  PyObject* value = CpState_Read(layer->m_state, 1);
  if (!value) {
    return NULL;
  }

  if (*PyBytes_AS_STRING(value)) {
    res = Py_XNewRef(Py_True);
  } else {
    res = Py_XNewRef(Py_False);
  }

  Py_XDECREF(value);
  return res;
}

/* type setup */
PyTypeObject CpBoolAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(boolatom),
  sizeof(CpBoolAtomObject),        /* tp_basicsize */
  0,                               /* tp_itemsize */
  (destructor)cp_boolatom_dealloc, /* tp_dealloc */
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
  (initproc)cp_boolatom_init,      /* tp_init */
  0,                               /* tp_alloc */
  (newfunc)cp_boolatom_new,        /* tp_new */
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