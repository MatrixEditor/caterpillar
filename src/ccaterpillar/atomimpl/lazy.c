/* lazy C atom implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

/* impl */
static PyObject*
cp_lazyatom_type(CpLazyAtomObject* self)
{
  PyObject* atom = CpLazyAtom_Atom(self);
  if (!atom)
    return NULL;

  PyObject* type = CpTypeOf(atom);
  Py_DECREF(atom);
  return type;
}

static PyObject*
cp_lazyatom_size(CpLazyAtomObject* self, CpLayerObject* layer)
{
  PyObject* atom = CpLazyAtom_Atom(self);
  if (!atom)
    return NULL;

  PyObject* size = _Cp_SizeOf(atom, layer);
  Py_DECREF(atom);
  return size;
}

static PyObject*
cp_lazyatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpLazyAtomObject* self = (CpLazyAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpLazyAtom_Pack;
    CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpLazyAtom_Unpack;
    CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_lazyatom_size;
    CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_lazyatom_type;
    CpBuiltinAtom_CATOM(self).ob_bits = NULL;

    self->m_atom = NULL;
    self->m_fn = NULL;
    self->s_always_lazy = false;
  }
  return (PyObject*)self;
}

static void
cp_lazyatom_dealloc(CpLazyAtomObject* self)
{
  Py_XDECREF(self->m_atom);
  Py_XDECREF(self->m_fn);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_lazyatom_init(CpLazyAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "fn", "always_lazy", NULL };
  PyObject* fn = NULL;
  int always_lazy = 0;
  if (!PyArg_ParseTupleAndKeywords(
        args, kwds, "O|p", kwlist, &fn, &always_lazy)) {
    return -1;
  }

  _Cp_SetObj(self->m_fn, fn);
  self->s_always_lazy = always_lazy;
  self->m_atom = NULL;
  return 0;
}

static PyObject*
cp_lazyatom_repr(CpLazyAtomObject* self)
{
  return PyUnicode_FromFormat("<%slazy %s>",
                              self->s_always_lazy ? "always_" : "",
                              self->m_atom ? Py_TYPE(self->m_atom)->tp_name
                                           : "<lambda>");
}

static PyObject*
cp_lazyatom_set_byteorder(CpLazyAtomObject* self, PyObject* args, PyObject* kw)
{
  _CpEndian_KwArgsGetByteorder(NULL);

  PyObject* atom = CpLazyAtom_Atom(self);
  if (!atom) {
    return NULL;
  }
  PyObject* ret = CpEndian_SetEndian(atom, (CpEndianObject*)byteorder);
  if (!ret) {
    Py_DECREF(atom);
    return NULL;
  }
  _Cp_SetObj(self->m_atom, ret);
  Py_DECREF(atom);
  Py_DECREF(ret);
  return Py_NewRef((PyObject*)self);
}

/* Public API */

/*CpAPI*/
int
CpLazyAtom_Pack(CpLazyAtomObject* self, PyObject* obj, CpLayerObject* layer)
{
  PyObject* atom = CpLazyAtom_Atom(self);
  if (!atom) {
    return -1;
  }
  int res = _Cp_Pack(obj, atom, layer);
  Py_DECREF(atom);
  return res;
}

/*CpAPI*/
PyObject*
CpLazyAtom_Unpack(CpLazyAtomObject* self, CpLayerObject* layer)
{
  PyObject* atom = CpLazyAtom_Atom(self);
  if (!atom) {
    return NULL;
  }
  PyObject* res = _Cp_Unpack(atom, layer);
  Py_DECREF(atom);
  return res;
}

/* docs */

/* type */

static PyMemberDef CpLazyAtom_Members[] = {
  { "fn", T_OBJECT_EX, offsetof(CpLazyAtomObject, m_fn), READONLY },
  { "always_lazy",
    T_BOOL,
    offsetof(CpLazyAtomObject, s_always_lazy),
    READONLY },
  { NULL } /* Sentinel */
};

static PyMethodDef CpLazyAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(lazyatom, NULL),
  { NULL } /* Sentinel */
};

PyTypeObject CpLazyAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpLazyAtom_NAME),
  .tp_basicsize = sizeof(CpLazyAtomObject),
  .tp_dealloc = (destructor)cp_lazyatom_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_init = (initproc)cp_lazyatom_init,
  .tp_new = (newfunc)cp_lazyatom_new,
  .tp_repr = (reprfunc)cp_lazyatom_repr,
  .tp_members = CpLazyAtom_Members,
  .tp_methods = CpLazyAtom_Methods,
};