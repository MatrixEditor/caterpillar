/* enum atom C implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

/* impl */
static PyObject*
cp_enumatom_type(CpEnumAtomObject* self)
{
  if (self->m_enum_type) {
    return Py_NewRef(self->m_enum_type);
  }
  return CpTypeOf(self->m_atom);
}

static PyObject*
cp_enumatom_size(CpEnumAtomObject* self, CpLayerObject* layer)
{
  return _Cp_SizeOf(self->m_atom, layer);
}

static PyObject*
cp_enumatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpEnumAtomObject* atom = (CpEnumAtomObject*)type->tp_alloc(type, 0);
  if (atom != NULL) {
    CpBuiltinAtom_CATOM(atom).ob_pack = (packfunc)CpEnumAtom_Pack;
    CpBuiltinAtom_CATOM(atom).ob_unpack = (unpackfunc)CpEnumAtom_Unpack;
    CpBuiltinAtom_CATOM(atom).ob_pack_many = NULL;
    CpBuiltinAtom_CATOM(atom).ob_unpack_many = NULL;
    CpBuiltinAtom_CATOM(atom).ob_size = (sizefunc)cp_enumatom_size;
    CpBuiltinAtom_CATOM(atom).ob_type = (typefunc)cp_enumatom_type;
    CpBuiltinAtom_CATOM(atom).ob_bits = NULL;

    atom->m_atom = NULL;
    atom->m_enum_type = NULL;
    atom->m_members = NULL;
    atom->m_value2member_map = NULL;
    atom->m_default = Py_NewRef(CpInvalidDefault);
  }
  return (PyObject*)atom;
}

static void
cp_enumatom_dealloc(CpEnumAtomObject* self)
{
  Py_XDECREF(self->m_atom);
  Py_XDECREF(self->m_members);
  Py_XDECREF(self->m_enum_type);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_enumatom_init(CpEnumAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "atom", "enum_type", "default", NULL };
  PyObject *atom = NULL, *enum_type = NULL, *default_value = NULL;
  if (!PyArg_ParseTupleAndKeywords(
        args, kwds, "OO|O", kwlist, &atom, &enum_type, &default_value)) {
    return -1;
  }
  _Cp_SetObj(self->m_atom, atom);
  _Cp_SetObj(self->m_enum_type, enum_type);
  _Cp_SetObj(self->m_default, default_value);

  _modulestate* mod = get_global_module_state();
  PyObject* members =
    PyObject_GetAttr(self->m_enum_type, mod->str__member_map_);
  if (!members) {
    return -1;
  }

  _Cp_SetObj(self->m_members, members);
  PyObject* value2member_map =
    PyObject_GetAttr(self->m_enum_type, mod->str__value2member_map_);
  if (!value2member_map) {
    return -1;
  }
  _Cp_SetObj(self->m_value2member_map, value2member_map);

  return 0;
}

_CpEndian_ImplSetByteorder(CpEnumAtomObject, enumatom, self->m_atom);

static PyObject*
cp_enumatom_repr(CpEnumAtomObject* self)
{
  return PyUnicode_FromFormat(
    "<enum [<%s>] %R>", ((PyTypeObject *)self->m_enum_type)->tp_name, self->m_atom);
}

/* Public API */

/*CpAPI*/
int
CpEnumAtom_Pack(CpEnumAtomObject* self, PyObject* value, CpLayerObject* layer)
{
  // TODO: check enum type - add strict flag
  // if (!PyObject_TypeCheck(value, (PyTypeObject*)self->m_enum_type)) {
  //   PyErr_Format(PyExc_TypeError,
  //                "Expected a %s, got %s",
  //                Py_TYPE(self->m_enum_type)->tp_name,
  //                Py_TYPE(value)->tp_name);
  //   return -1;
  // }
  int res = 0;
  if (PyObject_TypeCheck(value, (PyTypeObject*)self->m_enum_type)) {
    PyObject* real_value = PyObject_GetAttrString(value, "value");
    if (!real_value) {
      return -1;
    }
    res = _Cp_Pack(real_value, self->m_atom, layer);
    Py_DECREF(real_value);
  } else {
    res = _Cp_Pack(value, self->m_atom, layer);
  }

  return res;
}

/*CpAPI*/
PyObject*
CpEnumAtom_Unpack(CpEnumAtomObject* self, CpLayerObject* layer)
{
  PyObject* value = _Cp_Unpack(self->m_atom, layer);
  if (!value) {
    return NULL;
  }

  PyObject* by_name = PyDict_GetItem(self->m_members, value);
  if (by_name) {
    Py_DECREF(value);
    return Py_NewRef(by_name);
  }
  // not found
  PyErr_Clear();

  PyObject* by_value = PyDict_GetItem(self->m_value2member_map, value);
  if (by_value) {
    Py_DECREF(value);
    return Py_NewRef(by_value);
  }

  // not found, fallback to default value
  PyErr_Clear();

  if (Cp_IsInvalidDefault(self->m_default)) {
    // TODO: add strict parsing flag here
    return value;
  }
  Py_DECREF(value);
  return Py_NewRef(self->m_default);
}

/* docs */

/* type setup */

static PyMemberDef CpEnumAtom_Members[] = {
  { "atom", T_OBJECT, offsetof(CpEnumAtomObject, m_atom), READONLY },
  { "enum_type", T_OBJECT, offsetof(CpEnumAtomObject, m_enum_type), READONLY },
  { "members", T_OBJECT, offsetof(CpEnumAtomObject, m_members), READONLY },
  { "default", T_OBJECT, offsetof(CpEnumAtomObject, m_default), 0 },
  { NULL }
};

static PyMethodDef CpEnumAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(enumatom, NULL),
  {
    NULL,
  }
};

PyTypeObject CpEnumAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpEnumAtom_NAME),
  .tp_basicsize = sizeof(CpEnumAtomObject),
  .tp_dealloc = (destructor)cp_enumatom_dealloc,
  .tp_init = (initproc)cp_enumatom_init,
  .tp_repr = (reprfunc)cp_enumatom_repr,
  .tp_members = CpEnumAtom_Members,
  .tp_methods = CpEnumAtom_Methods,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_new = (newfunc)cp_enumatom_new,
};
