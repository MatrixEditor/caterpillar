/* constatom C implementation */
#include "caterpillar/caterpillar.h"

#include <structmember.h>

static PyObject*
cp_constatom__type__(CpConstAtomObject* self)
{
  return CpTypeOf(self->m_atom);
}

static PyObject*
cp_constatom__size__(CpConstAtomObject* self, CpLayerObject* layer)
{
  return _Cp_SizeOf(self->m_atom, layer);
}

static PyObject*
cp_constatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpConstAtomObject* self = (CpConstAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpConstAtom_Pack;
    CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpConstAtom_Unpack;
    CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_constatom__size__;
    CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_constatom__type__;
    CpBuiltinAtom_CATOM(self).ob_bits = NULL;

    self->m_atom = NULL;
    self->m_value = NULL;
  }
  return (PyObject*)self;
}

static void
cp_constatom_dealloc(CpConstAtomObject* self)
{
  Py_XDECREF(self->m_atom);
  Py_XDECREF(self->m_value);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_constatom_init(CpConstAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "atom", "value", NULL };
  PyObject* atom = NULL;
  PyObject* value = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist, &atom, &value)) {
    return -1;
  }
  _Cp_SetObj(self->m_atom, atom);
  _Cp_SetObj(self->m_value, value);
  return 0;
}

/* Public API */

/*CpAPI*/
int
CpConstAtom_Pack(CpConstAtomObject* self, PyObject* value, CpLayerObject* layer)
{
  return _Cp_Pack(self->m_value, self->m_atom, layer);
}

/*CpAPI*/
PyObject*
CpConstAtom_Unpack(CpConstAtomObject* self, CpLayerObject* layer)
{
  PyObject* res = _Cp_Unpack(self->m_atom, layer);
  if (!res) {
    return NULL;
  }

  if (PyObject_RichCompareBool(res, self->m_value, Py_NE)) {
    PyErr_Format(PyExc_ValueError,
                 "Value is not equal to constant (parsed=%R, constant=%R)",
                 res,
                 self->m_value);
    Py_DECREF(res);
    return NULL;
  }
  // REVISIT: Should we free the 'res' object here?
  return res;
}

/* type setup */

PyTypeObject CpConstAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpConstAtom_NAME),
  .tp_basicsize = sizeof(CpConstAtomObject),
  .tp_dealloc = (destructor)cp_constatom_dealloc,
  .tp_init = (initproc)cp_constatom_init,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = (newfunc)cp_constatom_new,
};