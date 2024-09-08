/* switch atom implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

/* impl */
static PyObject*
cp_switchatom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpSwitchAtomObject* self = (CpSwitchAtomObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  CpBuiltinAtom_CATOM(self).ob_bits = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpSwitchAtom_Pack;
  CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpSwitchAtom_Unpack;
  CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_size = NULL;
  CpBuiltinAtom_CATOM(self).ob_type = NULL;
  self->s_callable = false;
  return (PyObject*)self;
}

static void
cp_switchatom_dealloc(CpSwitchAtomObject* self)
{
  CpBuiltinAtom_CATOM(self).ob_bits = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_size = NULL;
  CpBuiltinAtom_CATOM(self).ob_type = NULL;
  Py_CLEAR(self->m_cases);
  Py_CLEAR(self->m_atom);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_switchatom_init(CpSwitchAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "atom", "cases", NULL };
  PyObject* cases = NULL;
  PyObject* atom = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "OO", kwlist, &atom, &cases)) {
    return -1;
  }
  _Cp_SetObj(self->m_cases, cases);
  _Cp_SetObj(self->m_atom, atom);
  self->s_callable = PyCallable_Check(self->m_atom);
  return 0;
}

static PyObject*
cp_switchatom_set_byteorder(CpSwitchAtomObject* self,
                            PyObject* args,
                            PyObject* kw)
{
  _CpEndian_KwArgsGetByteorder(NULL);
  PyObject* new_atom =
    CpEndian_SetEndian(self->m_atom, (CpEndianObject*)byteorder);
  if (!new_atom) {
    return NULL;
  }
  _Cp_SetObj(self->m_atom, new_atom);
  return (PyObject*)self;
}

static PyObject*
cp_switchatom_get_next(CpSwitchAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "atom", "context", NULL };
  PyObject* op = NULL;
  PyObject* context = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "OO", kwlist, &op, &context)) {
    return NULL;
  }

  return CpSwitchAtom_GetNext(self, op, context);
}

static PyObject*
cp_switchatom_repr(CpSwitchAtomObject* self)
{
  return PyUnicode_FromFormat("<switch [<%s>] %R>", Py_TYPE(self->m_cases)->tp_name, self->m_atom);
}

/* Public API */

/*CpAPI*/
PyObject*
CpSwitchAtom_GetNext(CpSwitchAtomObject* self, PyObject* op, PyObject* context)
{
  PyObject* result = NULL;
  if (PyCallable_Check(self->m_cases)) {
    result = PyObject_CallOneArg(self->m_cases, context);
    if (!result)
      return NULL;
  } else {
    result = PyObject_GetItem(self->m_cases, op);
    if (!result) {
      result = PyObject_GetItem(self->m_cases, CpInvalidDefault);
      if (!result)
        return NULL;
    }
  }
  // TODO: check for nested struct
  return result;
}

/*CpAPI*/
PyObject*
CpSwitchAtom_Unpack(CpSwitchAtomObject* self, CpLayerObject* layer)
{
  PyObject* value = _Cp_Unpack(self->m_atom, layer);
  if (!value) {
    return NULL;
  }

  PyObject* next_atom = CpSwitchAtom_GetNext(self, value, (PyObject*)layer);
  if (!next_atom) {
    Py_DECREF(value);
    return NULL;
  }

  if (Py_IsNone(next_atom)) {
    // TODO: document this behaviour
    return value;
  }

  PyObject* result = _Cp_Unpack(next_atom, layer);
  Py_DECREF(value);
  Py_DECREF(next_atom);
  return result;
}

/*CpAPI*/
int
CpSwitchAtom_Pack(CpSwitchAtomObject* self, PyObject* obj, CpLayerObject* layer)
{
  if (!self->s_callable) {
    PyErr_SetString(
      PyExc_TypeError,
      ("Switch atom currently supports only callable atoms when used as a "
       "condition to select the final atom to be used to pack the given "
       "value."));
    return -1;
  }

  PyObject* value = PyObject_CallOneArg(self->m_atom, (PyObject*)layer);
  if (!value) {
    return -1;
  }

  PyObject* next_atom = CpSwitchAtom_GetNext(self, value, (PyObject*)layer);
  if (!next_atom) {
    Py_DECREF(value);
    return -1;
  }

  int result = _Cp_Pack(obj, next_atom, layer);
  Py_DECREF(next_atom);
  Py_DECREF(value);
  return result;
}

/* docs */

/* members */
static PyMemberDef CpSwitchAtom_Members[] = {
  { "cases", T_OBJECT, offsetof(CpSwitchAtomObject, m_cases), READONLY },
  { "atom", T_OBJECT, offsetof(CpSwitchAtomObject, m_atom), READONLY },
  { NULL }
};

/* methods */
static PyMethodDef CpSwitchAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(switchatom, NULL),
  { "get_next",
    (PyCFunction)cp_switchatom_get_next,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { NULL }
};

PyTypeObject CpSwitchAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpConditionAtom_NAME),
  .tp_basicsize = sizeof(CpConditionAtomObject),
  .tp_dealloc = (destructor)cp_switchatom_dealloc,
  .tp_init = (initproc)cp_switchatom_init,
  .tp_members = CpSwitchAtom_Members,
  .tp_methods = CpSwitchAtom_Methods,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_new = (newfunc)cp_switchatom_new,
  .tp_repr = (reprfunc)cp_switchatom_repr,
};
