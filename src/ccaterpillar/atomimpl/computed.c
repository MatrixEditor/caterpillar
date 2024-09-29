/* computed atom C implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

/* impl */
static PyObject*
cp_computedatom_type(CpComputedAtomObject* self)
{
  if (self->s_callable) {
    return Py_XNewRef(get_global_module_state()->Any_Type);
  }
  return Py_NewRef(Py_TYPE(self->m_value));
}

static PyObject*
cp_computedatom_size(CpComputedAtomObject* self, PyObject* ctx)
{
  // TODO: explain why computed atom objects are of size 0
  return PyLong_FromSize_t(0);
}

static PyObject*
cp_computedatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpComputedAtomObject* self = (CpComputedAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpComputedAtom_Pack;
    CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpComputedAtom_Unpack;
    CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_computedatom_size;
    CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_computedatom_type;
    CpBuiltinAtom_CATOM(self).ob_bits = NULL;

    self->m_value = NULL;
    self->s_callable = false;
  }
  return (PyObject*)self;
}

static void
cp_computedatom_dealloc(CpComputedAtomObject* self)
{
  Py_XDECREF(self->m_value);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_computedatom_init(CpComputedAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "value", NULL };
  PyObject* value = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &value)) {
    return -1;
  }

  _Cp_SetObj(self->m_value, value);
  self->s_callable = PyCallable_Check(self->m_value);
  return 0;
}

static PyObject*
cp_computedatom_repr(CpComputedAtomObject* self)
{
  return PyUnicode_FromFormat(
    "<computed %s>",
    self->s_callable ? "<lambda>" : Py_TYPE(self->m_value)->tp_name);
}

/* Public API */

/*CpAPI*/
int
CpComputedAtom_Pack(CpComputedAtomObject* self,
                    PyObject* obj,
                    CpLayerObject* layer)
{
  return 0;
}

/*CpAPI*/
PyObject*
CpComputedAtom_Unpack(CpComputedAtomObject* self, CpLayerObject* layer)
{
  return CpComputedAtom_Value(self, layer);
}

/* docs */

/* type */

static PyMemberDef cp_computedatom_members[] = {
  { "value", T_OBJECT, offsetof(CpComputedAtomObject, m_value), READONLY, "value" },
  { NULL }
};

PyTypeObject CpComputedAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpComputedAtom_NAME),
  .tp_basicsize = sizeof(CpComputedAtomObject),
  .tp_dealloc = (destructor)cp_computedatom_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_init = (initproc)cp_computedatom_init,
  .tp_new = (newfunc)cp_computedatom_new,
  .tp_members = cp_computedatom_members,
  .tp_repr = (reprfunc)cp_computedatom_repr,
};