/* boolatom C implementation */
#include "caterpillar/caterpillar.h"

#include <structmember.h>

static PyObject*
cp_boolatom__type__(CpBoolAtomObject* self)
{
  return Py_XNewRef(&PyBool_Type);
}

static PyObject*
cp_boolatom__size__(CpBoolAtomObject* self, PyObject* ctx)
{
  return PyLong_FromSize_t(1);
}

static PyObject*
cp_boolatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpBoolAtomObject* self = (CpBoolAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpBoolAtom_Pack;
    CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpBoolAtom_Unpack;
    CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_boolatom__size__;
    CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_boolatom__type__;
    CpBuiltinAtom_CATOM(self).ob_bits = NULL;
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
  _Cp_InitNoArgs(boolatom, args, kwds);
}

/* Public API */
/*CpAPI*/
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

/*CpAPI*/
PyObject*
CpBoolAtom_Unpack(CpBoolAtomObject* self, CpLayerObject* layer)
{
  PyObject* res;
  PyObject* value = CpState_ReadSsize_t(layer->m_state, 1);
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
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpBoolAtom_NAME),
  .tp_basicsize = sizeof(CpBoolAtomObject),
  .tp_dealloc = (destructor)cp_boolatom_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_doc = NULL,
  .tp_init = (initproc)cp_boolatom_init,
  .tp_new = (newfunc)cp_boolatom_new,
};