/* pascal string implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>

/*impl*/
static PyObject*
cp_pstringatom_type(PyObject* self)
{
  return Py_XNewRef(&PyUnicode_Type);
}

static PyObject*
cp_pstringatom_size(CpPStringAtomObject* self, CpLayerObject* layer)
{
  PyErr_SetString(PyExc_TypeError, "Pascal strings do not have a static size!");
  return NULL;
}

static PyObject*
cp_pstringatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpPStringAtomObject* self = (CpPStringAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpPStringAtom_Pack;
    CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpPStringAtom_Unpack;
    CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_pstringatom_size;
    CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_pstringatom_type;
    CpBuiltinAtom_CATOM(self).ob_bits = NULL;

    self->m_encoding = NULL;
    self->m_errors = NULL;
    self->m_atom = NULL;
  }
  return (PyObject*)self;
}

static void
cp_pstringatom_dealloc(CpPStringAtomObject* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_pstringatom_init(CpPStringAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "atom", "encoding", "errors", NULL };
  PyObject *encoding = NULL, *errors = NULL, *atom = NULL;

  if (!PyArg_ParseTupleAndKeywords(
        args, kwds, "O|OO", kwlist, &atom, &encoding, &errors)) {
    return -1;
  }
  _modulestate* mod = get_global_module_state();

  _Cp_SetObj(self->m_atom, atom);
  _Cp_SetObj(self->m_encoding, encoding);
  if (!self->m_encoding) {
    _Cp_SetObj(self->m_encoding, mod->str_utf8);
  }
  _Cp_SetObj(self->m_errors, errors);
  if (!self->m_errors) {
    _Cp_SetObj(self->m_errors, mod->str_strict);
  }
  return 0;
}

static PyObject*
cp_pstringatom_repr(CpPStringAtomObject* self)
{
  return PyUnicode_FromFormat(
    "<pstring [%R %R] %R>", self->m_encoding, self->m_errors, self->m_atom);
}

_CpEndian_ImplSetByteorder(CpPStringAtomObject, pstringatom, self->m_atom);

/* Public API */

/*CpAPI*/
int
CpPStringAtom_Pack(CpPStringAtomObject* self,
                   PyObject* value,
                   CpLayerObject* layer)
{
  if (!PyUnicode_Check(value)) {
    PyErr_Format(PyExc_TypeError,
                 "Pascal strings must be packed from unicode - got %R",
                 value);
    return -1;
  }

  PyObject* length = PyLong_FromSsize_t(PyUnicode_GET_LENGTH(value));
  if (!length) {
    return -1;
  }

  if (_Cp_Pack(length, self->m_atom, layer)) {
    Py_DECREF(length);
    return -1;
  }
  Py_DECREF(length);

  PyObject* bytes = PyUnicode_AsEncodedString(
    value, PyUnicode_DATA(self->m_encoding), PyUnicode_DATA(self->m_errors));
  if (!bytes) {
    return -1;
  }
  PyObject* res = CpState_Write(layer->m_state, bytes);
  Py_DECREF(bytes);
  if (!res) {
    return -1;
  }
  Py_XDECREF(res);
  return 0;
}

/*CpAPI*/
PyObject*
CpPStringAtom_Unpack(CpPStringAtomObject* self, CpLayerObject* layer)
{
  PyObject* length = _Cp_Unpack(self->m_atom, layer);
  if (length == NULL) {
    return NULL;
  }

  PyObject* bytes = CpState_Read(layer->m_state, length);
  Py_DECREF(length);
  if (!bytes) {
    return NULL;
  }
  PyObject* string = PyUnicode_Decode(PyBytes_AS_STRING(bytes),
                                      PyBytes_GET_SIZE(bytes),
                                      PyUnicode_DATA(self->m_encoding),
                                      PyUnicode_DATA(self->m_errors));
  Py_DECREF(bytes);
  return string;
}

/* docs */

/* type */
static PyMemberDef CpPStringAtom_Members[] = {
  { "atom", T_OBJECT, offsetof(CpPStringAtomObject, m_atom), 0, NULL },
  { "encoding", T_STRING, offsetof(CpPStringAtomObject, m_encoding), 0, NULL },
  { "errors", T_STRING, offsetof(CpPStringAtomObject, m_errors), 0, NULL },
  { NULL } /* Sentinel */
};

static PyMethodDef CpPStringAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(pstringatom, NULL),
  { NULL } /* Sentinel */
};

PyTypeObject CpPStringAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpPStringAtom_NAME),
  .tp_basicsize = sizeof(CpPStringAtomObject),
  .tp_dealloc = (destructor)cp_pstringatom_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_members = CpPStringAtom_Members,
  .tp_init = (initproc)cp_pstringatom_init,
  .tp_new = (newfunc)cp_pstringatom_new,
  .tp_repr = (reprfunc)cp_pstringatom_repr,
  .tp_methods = CpPStringAtom_Methods,
};