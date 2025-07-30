#include "caterpillar/caterpillar.h"
#include "private.h"

#include <stddef.h>
#include <structmember.h>

static PyObject*
cp_atom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpAtomObject* self = NULL;
  if ((self = (CpAtomObject*)type->tp_alloc(type, 0), !self)) {
    return NULL;
  }

  self->ob_bits = NULL;
  self->ob_pack = NULL;
  self->ob_pack_many = NULL;
  self->ob_unpack = NULL;
  self->ob_unpack_many = NULL;
  self->ob_size = NULL;
  self->ob_type = NULL;
  return _Cp_CAST(PyObject*, self);
}

static void
cp_atom_dealloc(CpAtomObject* self)
{
  self->ob_bits = NULL;
  self->ob_pack = NULL;
  self->ob_pack_many = NULL;
  self->ob_unpack = NULL;
  self->ob_unpack_many = NULL;
  self->ob_size = NULL;
  self->ob_type = NULL;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_atom_init(CpAtomObject* self, PyObject* args, PyObject* kw)
{
  // We don't have to initialize anything here, because subclasses
  // will overload the `__init__` method and place their method
  // implementations.
  _Cp_InitNoArgs(CAtoms, args, kw);
}

static PyObject*
cp_atom_repr(CpAtomObject* self)
{
  return PyUnicode_FromString("<Atom>");
}

static PyObject*
cp_atom_pack(CpAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "obj", "context", NULL };
  PyObject *op = NULL, *context = NULL;
  if (!self->ob_pack) {
    PyErr_Format(PyExc_NotImplementedError,
                 "The atom of type '%s' cannot be packed (missing __pack__)",
                 Py_TYPE(self)->tp_name);
    return NULL;
  }

  if (PyArg_ParseTupleAndKeywords(args, kw, "OO", kwlist, &op, &context) < 0) {
    return NULL;
  }

  return self->ob_pack((PyObject*)self, op, context) ? NULL
                                                     : Py_NewRef(Py_None);
}

static PyObject*
cp_atom_pack_many(CpAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "obj", "context", "lengthinfo", NULL };
  PyObject *ops = NULL, *context = NULL, *lengthinfo = NULL;
  if (!self->ob_pack_many) {
    PyErr_Format(
      PyExc_NotImplementedError,
      "The atom of type '%s' cannot be packed (missing __pack_many__)",
      Py_TYPE(self)->tp_name);
    return NULL;
  }

  if (PyArg_ParseTupleAndKeywords(
        args, kw, "OOO", kwlist, &ops, &context, &lengthinfo) < 0) {
    return NULL;
  }

  return self->ob_pack_many((PyObject*)self, ops, context, lengthinfo)
           ? NULL
           : Py_NewRef(Py_None);
}

static PyObject*
cp_atom_unpack(CpAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "context", NULL };
  PyObject* context = NULL;

  if (!self->ob_unpack) {
    PyErr_Format(
      PyExc_NotImplementedError,
      "The atom of type '%s' cannot be unpacked (missing __unpack__)",
      Py_TYPE(self)->tp_name);
    return NULL;
  }
  if (PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &context) < 0) {
    return NULL;
  }
  PyObject* r = self->ob_unpack((PyObject*)self, context);
  return r;
}

static PyObject*
cp_atom_unpack_many(CpAtomObject* self, PyObject* args, PyObject* kw)
{

  static char* kwlist[] = { "context", "lengthinfo", NULL };
  PyObject *context = NULL, *lengthinfo = NULL;
  if (self->ob_unpack_many == NULL) {
    PyErr_Format(
      PyExc_NotImplementedError,
      "The atom of type '%s' cannot be unpacked (missing __unpack_many__)",
      Py_TYPE(self)->tp_name);
    return NULL;
  }

  if (PyArg_ParseTupleAndKeywords(
        args, kw, "OO", kwlist, &context, &lengthinfo) < 0) {
    return NULL;
  }
  return self->ob_unpack_many((PyObject*)self, context, lengthinfo);
}

static PyObject*
cp_atom_type(CpAtomObject* self)
{
  return self->ob_type ? self->ob_type(_Cp_CAST(PyObject*, self))
                       : Py_NotImplemented;
}

static PyObject*
cp_atom_bits(CpAtomObject* self)
{
  return self->ob_bits ? self->ob_bits(_Cp_CAST(PyObject*, self))
                       : Py_NotImplemented;
}

static PyObject*
cp_atom_size(CpAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "context", NULL };
  PyObject* context = NULL;

  if (!self->ob_size) {
    PyErr_Format(PyExc_NotImplementedError,
                 "The atom of type '%s' has no size (missing __size__)",
                 Py_TYPE(self)->tp_name);
    return NULL;
  }
  if (PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &context) < 0) {
    return NULL;
  }
  if (Py_IsNone(context)) {
    PyErr_SetString(PyExc_ValueError, "context must be set!");
    return NULL;
  }
  return self->ob_size((PyObject*)self, context);
}

/*CpAPI*/
int
CpAtom_Pack(PyObject* pAtom, PyObject* pObj, PyObject* pContext)
{
  _modulestate* state = NULL;
  PyObject* nResult = NULL;
  packfunc func = NULL;

  if (CpAtom_Check(pAtom)) {
    func = _Cp_CAST(CpAtomObject*, pAtom)->ob_pack;
    if (!func) {
      PyErr_Format(PyExc_NotImplementedError,
                   "The atom of type '%s' cannot be packed (missing __pack__)",
                   Py_TYPE(pAtom)->tp_name);
      return -1;
    }
    return func(pAtom, pObj, pContext);
  }

  state = get_global_module_state();
  nResult =
    PyObject_CallMethodObjArgs(pAtom, state->str__pack, pObj, pContext, NULL);
  if (!nResult) {
    return -1;
  }
  Py_DECREF(nResult);
  return 0;
}

/*CpAPI*/
PyObject*
CpAtom_Unpack(PyObject* pAtom, PyObject* pContext)
{
  _modulestate* state = NULL;
  PyObject* nResult = NULL;
  unpackfunc func = NULL;

  if (CpAtom_Check(pAtom)) {
    func = _Cp_CAST(CpAtomObject*, pAtom)->ob_unpack;
    if (!func) {
      PyErr_Format(
        PyExc_NotImplementedError,
        "The atom of type '%s' cannot be unpacked (missing __unpack__)",
        Py_TYPE(pAtom)->tp_name);
      return NULL;
    }
    nResult = func(pAtom, pContext);
  } else {
    state = get_global_module_state();
    nResult =
      PyObject_CallMethodObjArgs(pAtom, state->str__unpack, pContext, NULL);
  }
  return nResult;
}

/*CpAPI*/
int
CpAtom_PackMany(PyObject* pAtom,
                PyObject* pObj,
                PyObject* pContext,
                PyObject* pLengthInfo)
{
  _modulestate* state = NULL;
  PyObject* nResult = NULL;
  packmanyfunc func = NULL;

  if (CpAtom_Check(pAtom)) {
    func = _Cp_CAST(CpAtomObject*, pAtom)->ob_pack_many;
    if (!func) {
      PyErr_Format(PyExc_NotImplementedError,
                   "The atom of type '%s' cannot be packed (missing __pack__)",
                   Py_TYPE(pAtom)->tp_name);
      return -1;
    }
    return func(pAtom, pObj, pContext, pLengthInfo);
  }

  state = get_global_module_state();
  nResult = PyObject_CallMethodObjArgs(
    pAtom, state->str__pack_many, pObj, pContext, NULL);
  if (!nResult) {
    return -1;
  }
  Py_DECREF(nResult);
  return 0;
}

/*CpAPI*/
PyObject*
CpAtom_Size(PyObject* pAtom, PyObject* pContext)
{
  _modulestate* state = NULL;
  PyObject* nResult = NULL;
  sizefunc func = NULL;

  if (CpAtom_Check(pAtom)) {
    func = _Cp_CAST(CpAtomObject*, pAtom)->ob_size;
    if (!func) {
      PyErr_Format(PyExc_NotImplementedError,
                   "The atom of type '%s' has no size (missing __size__)",
                   Py_TYPE(pAtom)->tp_name);
      return NULL;
    }
    nResult = func(pAtom, pContext);
  } else {
    state = get_global_module_state();
    nResult =
      PyObject_CallMethodObjArgs(pAtom, state->str__size, pContext, NULL);
  }
  return nResult;
}

/*CpAPI*/
PyObject*
CpAtom_UnpackMany(PyObject* pAtom, PyObject* pContext, PyObject* pLengthInfo)
{
  _modulestate* state = NULL;
  PyObject* nResult = NULL;
  unpackmanyfunc func = NULL;

  if (CpAtom_Check(pAtom)) {
    func = _Cp_CAST(CpAtomObject*, pAtom)->ob_unpack_many;
    if (!func) {
      PyErr_Format(
        PyExc_NotImplementedError,
        "The atom of type '%s' cannot be unpacked (missing __unpack__)",
        Py_TYPE(pAtom)->tp_name);
      return NULL;
    }
    nResult = func(pAtom, pContext, pLengthInfo);
  } else {
    state = get_global_module_state();
    nResult = PyObject_CallMethodObjArgs(
      pAtom, state->str__unpack_many, pContext, NULL);
  }
  return nResult;
}

/*CpAPI*/
PyObject*
CpAtom_BitsOf(PyObject* pAtom)
{
  _modulestate* state = NULL;
  PyObject* nResult = NULL;
  bitsfunc func = NULL;

  if (CpAtom_Check(pAtom)) {
    func = _Cp_CAST(CpAtomObject*, pAtom)->ob_bits;
    if (!func) {
      PyErr_Format(PyExc_NotImplementedError,
                   "The atom of type '%s' has no bits (missing __bits__)",
                   Py_TYPE(pAtom)->tp_name);
      return NULL;
    }
    nResult = func(pAtom);
  } else {
    state = get_global_module_state();
    nResult = PyObject_CallMethodObjArgs(pAtom, state->str__bits, NULL);
  }
  return nResult;
}

/*CpAPI*/
PyObject*
CpAtom_TypeOf(PyObject* pAtom)
{
  _modulestate* state = NULL;
  PyObject* nResult = NULL;
  typefunc func = NULL;

  if (CpAtom_Check(pAtom)) {
    func = _Cp_CAST(CpAtomObject*, pAtom)->ob_type;
    if (!func) {
      PyErr_Format(PyExc_NotImplementedError,
                   "The atom of type '%s' has no type (missing __type__)",
                   Py_TYPE(pAtom)->tp_name);
      return NULL;
    }
    nResult = func(pAtom);
  } else {
    state = get_global_module_state();
    nResult = PyObject_CallMethodObjArgs(pAtom, state->str__type, NULL);
  }
  return nResult;
}

/* docs */

PyDoc_STRVAR(cp_atom__doc__, "\
Atom()\n\
--\n\
\n\
Base class for C atom types.");

static PyMethodDef CpCAtom_Methods[] = {
  { "__pack__", (PyCFunction)cp_atom_pack, METH_VARARGS | METH_KEYWORDS, NULL },
  { "__pack_many__",
    (PyCFunction)cp_atom_pack_many,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { "__unpack__",
    (PyCFunction)cp_atom_unpack,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { "__unpack_many__",
    (PyCFunction)cp_atom_unpack_many,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { "__type__", (PyCFunction)cp_atom_type, METH_NOARGS, NULL },
  { "__size__", (PyCFunction)cp_atom_size, METH_VARARGS | METH_KEYWORDS, NULL },
  { "__bits__", (PyCFunction)cp_atom_bits, METH_NOARGS, NULL },
  { NULL } /* Sentinel */
};

PyTypeObject CpAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpAtom_NAME),
  .tp_basicsize = sizeof(CpAtomObject),
  .tp_dealloc = (destructor)cp_atom_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = cp_atom__doc__,
  .tp_methods = CpCAtom_Methods,
  .tp_init = (initproc)cp_atom_init,
  .tp_new = (newfunc)cp_atom_new,
  .tp_repr = (reprfunc)cp_atom_repr,
};

/* init */
int
cp_atom__mod_types()
{
  CpModule_SetupType(&CpAtom_Type, -1);
  return 0;
}

void
cp_atom__mod_clear(PyObject* m, _modulestate* state)
{
  Py_CLEAR(state->str__pack_many);
  Py_CLEAR(state->str__pack);
  Py_CLEAR(state->str__unpack_many);
  Py_CLEAR(state->str__unpack);
  Py_CLEAR(state->str__type);
  Py_CLEAR(state->str__size);
  Py_CLEAR(state->str__bits);
  Py_CLEAR(state->str__struct);
}

int
cp_atom__mod_init(PyObject* m, _modulestate* state)
{
  CpModule_AddObject(CpAtom_NAME, &CpAtom_Type, -1);
  _CACHED_STRING(state, str__pack_many, CpAtom_PackMany_STR, -1);
  _CACHED_STRING(state, str__pack, CpAtom_Pack_STR, -1);
  _CACHED_STRING(state, str__unpack_many, CpAtom_UnpackMany_STR, -1);
  _CACHED_STRING(state, str__unpack, CpAtom_Unpack_STR, -1);
  _CACHED_STRING(state, str__type, CpAtom_Type_STR, -1);
  _CACHED_STRING(state, str__size, CpAtom_Size_STR, -1);
  _CACHED_STRING(state, str__bits, CpAtom_Bits_STR, -1);
  _CACHED_STRING(state, str__struct, "__struct__", -1);
  return 0;
}