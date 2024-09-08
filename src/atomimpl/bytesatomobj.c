/* constatom C implementation */
#include "caterpillar/caterpillar.h"

#include <structmember.h>

/*impl*/

static PyObject*
cp_bytesatom_type(CpBytesAtomObject* self)
{
  return Py_NewRef(&PyBytes_Type);
}

static PyObject*
cp_bytesatom_size(CpBytesAtomObject* self, CpLayerObject* layer)
{
  return CpBytesAtom_GetLength(self, layer);
}

static PyObject*
cp_bytesatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpBytesAtomObject* self = (CpBytesAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpBytesAtom_Pack;
    CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpBytesAtom_Unpack;
    CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_bytesatom_size;
    CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_bytesatom_type;
    CpBuiltinAtom_CATOM(self).ob_bits = NULL;
    self->m_length = NULL;
    self->s_callable = 0;
  }
  return (PyObject*)self;
}

static void
cp_bytesatom_dealloc(CpBytesAtomObject* self)
{
  Py_XDECREF(self->m_length);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_bytesatom_init(CpBytesAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "length", NULL };
  PyObject* length = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &length)) {
    return -1;
  }
  _Cp_SetObj(self->m_length, length);
  self->s_callable = PyCallable_Check(self->m_length);
  return 0;
}

static PyObject*
cp_bytesatom_repr(CpBytesAtomObject* self)
{
  return PyUnicode_FromFormat("<bytes %R>", self->m_length);
}

/* Public API */

/*CpAPI*/
PyObject*
CpBytesAtom_GetLength(CpBytesAtomObject* self, CpLayerObject* layer)
{
  if (self->s_callable) {
    return PyObject_CallOneArg(self->m_length, (PyObject*)layer);
  }
  return Py_NewRef(self->m_length);
}

/*CpAPI*/
int
CpBytesAtom_Pack(CpBytesAtomObject* self, PyObject* value, CpLayerObject* layer)
{
  PyObject* length = CpBytesAtom_GetLength(self, layer);
  if (length == NULL) {
    return -1;
  }

  if (PyLong_AS_LONG(length) != PyBytes_GET_SIZE(value)) {
    PyErr_SetString(PyExc_ValueError, "Invalid length");
    return -1;
  }
  Py_DECREF(length);

  PyObject* res = CpState_Write(layer->m_state, value);
  if (!res) {
    return -1;
  }
  Py_DECREF(res);
  return 0;
}

/*CpAPI*/
PyObject*
CpBytesAtom_Unpack(CpBytesAtomObject* self, CpLayerObject* layer)
{
  PyObject* length = CpBytesAtom_GetLength(self, layer);
  if (length == NULL) {
    return NULL;
  }
  return CpState_Read(layer->m_state, length);
}

/* docs */

/* type setup */
static PyMemberDef CpBytesAtom_Members[] = {
  { "length", T_OBJECT, offsetof(CpBytesAtomObject, m_length), READONLY },
  { NULL }
};

PyTypeObject CpBytesAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpBytesAtom_NAME),
  .tp_basicsize = sizeof(CpBytesAtomObject),
  .tp_members = CpBytesAtom_Members,
  .tp_new = (newfunc)cp_bytesatom_new,
  .tp_init = (initproc)cp_bytesatom_init,
  .tp_dealloc = (destructor)cp_bytesatom_dealloc,
  .tp_repr = (reprfunc)cp_bytesatom_repr,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
};