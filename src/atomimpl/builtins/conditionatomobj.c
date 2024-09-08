/* condition atom implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

/* impl */

static PyObject*
cp_conditionatom_type(CpConditionAtomObject* self)
{
  PyObject* atom_type = CpTypeOf(self->m_atom);
  if (!atom_type)
    return NULL;

  _modulestate* state = get_global_module_state();
  Py_XSETREF(atom_type, PyObject_GetItem(state->Optional_Type, atom_type));
  return atom_type;
}

static PyObject*
cp_conditionatom_size(CpConditionAtomObject* self, CpLayerObject* layer)
{
  return _Cp_SizeOf(self->m_atom, layer);
}

static PyObject*
cp_conditionatom_repr(CpConditionAtomObject* self)
{
  return PyUnicode_FromFormat(
    "<conditional [<%s>] %R>", Py_TYPE(self->m_condition)->tp_name, self->m_atom);
}

static PyObject*
cp_conditionatom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpConditionAtomObject* self = (CpConditionAtomObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  CpBuiltinAtom_CATOM(self).ob_bits = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpConditionAtom_Pack;
  CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpConditionAtom_Unpack;
  CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_conditionatom_size;
  CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_conditionatom_type;
  return (PyObject*)self;
}

static void
cp_conditionatom_dealloc(CpConditionAtomObject* self)
{
  CpBuiltinAtom_CATOM(self).ob_bits = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack = NULL;
  CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack = NULL;
  CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_CATOM(self).ob_size = NULL;
  CpBuiltinAtom_CATOM(self).ob_type = NULL;
  Py_CLEAR(self->m_atom);
  Py_CLEAR(self->m_condition);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_conditionatom_init(CpConditionAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "condition", "atom", NULL };
  PyObject *condition = NULL, *atom = NULL;

  if (!PyArg_ParseTupleAndKeywords(args, kw, "OO", kwlist, &condition, &atom))
    return -1;

  _Cp_SetObj(self->m_atom, atom);
  _Cp_SetObj(self->m_condition, condition);
  return 0;
}

static PyObject*
cp_conditionatom_set_byteorder(CpConditionAtomObject* self,
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
cp_conditionatom_is_enabled(CpConditionAtomObject* self, PyObject* args)
{
  PyObject* layer = NULL;
  if (!PyArg_ParseTuple(args, "O", &layer)) {
    return NULL;
  }

  if (CpConditionAtom_IsEnabled(self, layer)) {
    Py_RETURN_TRUE;
  }
  Py_RETURN_FALSE;
}

/* Public API */

/*CpAPI*/
int
CpConditionAtom_IsEnabled(CpConditionAtomObject* self, PyObject* context)
{
  if (self->m_condition == NULL) {
    return true;
  }

  if (PyCallable_Check(self->m_condition)) {
    PyObject* result = PyObject_CallOneArg(self->m_condition, context);
    if (result == NULL) {
      return -1;
    }
    int truth = PyObject_IsTrue(result);
    Py_DECREF(result);
    return truth;
  }

  return PyObject_IsTrue(self->m_condition);
}

/*CpAPI*/
int
CpConditionAtom_Pack(CpConditionAtomObject* self, PyObject* op, PyObject* layer)
{
  if (!CpConditionAtom_IsEnabled(self, layer)) {
    return 0;
  }

  return _Cp_Pack(op, self->m_atom, (CpLayerObject*)layer);
}

/*CpAPI*/
PyObject*
CpConditionAtom_Unpack(CpConditionAtomObject* self, CpLayerObject* layer)
{
  if (!CpConditionAtom_IsEnabled(self, (PyObject*)layer)) {
    return NULL;
  }
  return _Cp_Unpack(self->m_atom, layer);
}

/* docs */

/* members */
static PyMemberDef CpConditionAtom_Members[] = {
  { "condition",
    T_OBJECT,
    offsetof(CpConditionAtomObject, m_condition),
    READONLY },
  { "atom", T_OBJECT, offsetof(CpConditionAtomObject, m_atom), READONLY },
  { NULL }
};

/* methods */
static PyMethodDef CpConditionAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(conditionatom, NULL),
  { "is_enabled", (PyCFunction)cp_conditionatom_is_enabled, METH_VARARGS },
  { NULL }
};

PyTypeObject CpConditionAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpConditionAtom_NAME),
  .tp_basicsize = sizeof(CpConditionAtomObject),
  .tp_dealloc = (destructor)cp_conditionatom_dealloc,
  .tp_init = (initproc)cp_conditionatom_init,
  .tp_members = CpConditionAtom_Members,
  .tp_methods = CpConditionAtom_Methods,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_new = (newfunc)cp_conditionatom_new,
  .tp_repr = (reprfunc)cp_conditionatom_repr,
};
