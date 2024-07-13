/* string atom implementation */

#include "caterpillar/caterpillar.h"
#include "caterpillar/atoms/string.h"
#include "caterpillar/parsing.h"
#include "caterpillar/module.h"

#include <structmember.h>

static PyObject*
cp_stringatom__type__(PyObject* self)
{
  return Py_XNewRef(&PyUnicode_Type);
}

static PyObject*
cp_stringatom__size__(CpStringAtomObject* self, CpLayerObject* layer)
{
  bool greedy = false;
  Py_ssize_t length = 0;
  if (_CpUnpack_EvalLength(layer, self->m_length, &greedy, &length) < 0) {
    return NULL;
  }

  if (greedy || length < 0) {
    PyErr_SetString(PyExc_ValueError, "Invalid dynamic length");
    return NULL;
  }
  return PyLong_FromSize_t(length);
}

static PyObject*
cp_stringatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpStringAtomObject* self = (CpStringAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    CpFieldCAtom_CATOM(self).ob_pack = (packfunc)CpStringAtom_Pack;
    CpFieldCAtom_CATOM(self).ob_unpack = (unpackfunc)CpStringAtom_Unpack;
    CpFieldCAtom_CATOM(self).ob_pack_many = NULL;
    CpFieldCAtom_CATOM(self).ob_unpack_many = NULL;
    CpFieldCAtom_CATOM(self).ob_size = (sizefunc)cp_stringatom__size__;
    CpFieldCAtom_CATOM(self).ob_type = (typefunc)cp_stringatom__type__;
    CpFieldCAtom_CATOM(self).ob_bits = NULL;

    self->m_encoding = NULL;
    self->m_length = NULL;
    self->m_errors = NULL;
  }
  return (PyObject*)self;
}

static void
cp_stringatom_dealloc(CpStringAtomObject* self)
{
  Py_CLEAR(self->m_encoding);
  Py_CLEAR(self->m_length);
  Py_CLEAR(self->m_errors);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_stringatom_init(CpStringAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "length", "encoding", "errors", NULL };
  PyObject *length = NULL, *encoding = NULL, *errors = NULL;
  if (!PyArg_ParseTupleAndKeywords(
        args, kwds, "OU|U", kwlist, &length, &encoding, &errors)) {
    return -1;
  }

  _Cp_SetObj(self->m_length, length);
  _Cp_SetObj(self->m_encoding, encoding);
  _Cp_SetObj(self->m_errors, errors);
  if (!self->m_errors) {
    _modulestate* mod = get_global_module_state();
    _Cp_SetObj(self->m_errors, mod->str_strict);
  }
  return 0;
}

/* Public API */

int
CpStringAtom_Pack(CpStringAtomObject* self,
                  PyObject* value,
                  CpLayerObject* layer)
{
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

PyObject*
CpStringAtom_Unpack(CpStringAtomObject* self, CpLayerObject* layer)
{
  Py_ssize_t length = 0;
  bool greedy = false;
  PyObject* res = NULL;
  if (_CpUnpack_EvalLength(layer, self->m_length, &greedy, &length) < 0) {
    return NULL;
  }
  if (greedy) {
    res = CpState_ReadFully(layer->m_state);
  } else {
    res = CpState_Read(layer->m_state, length);
  }
  if (!res) {
    return NULL;
  }

  PyObject* string = PyUnicode_Decode(PyBytes_AS_STRING(res),
                                      PyBytes_GET_SIZE(res),
                                      PyUnicode_DATA(self->m_encoding),
                                      PyUnicode_DATA(self->m_errors));
  Py_XDECREF(res);
  return string;
}

/* type setup */
static PyMemberDef CpStringAtom_Members[] = {
  { "encoding", T_STRING, offsetof(CpStringAtomObject, m_encoding), 0, NULL },
  { "length", T_OBJECT_EX, offsetof(CpStringAtomObject, m_length), 0, NULL },
  { "errors", T_STRING, offsetof(CpStringAtomObject, m_errors), 0, NULL },
  { NULL } /* Sentinel */
};

PyTypeObject CpStringAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(stringatom),
  sizeof(CpStringAtomObject),        /* tp_basicsize */
  0,                                 /* tp_itemsize */
  (destructor)cp_stringatom_dealloc, /* tp_dealloc */
  0,                                 /* tp_vectorcall_offset */
  0,                                 /* tp_getattr */
  0,                                 /* tp_setattr */
  0,                                 /* tp_as_async */
  0,                                 /* tp_repr */
  0,                                 /* tp_as_number */
  0,                                 /* tp_as_sequence */
  0,                                 /* tp_as_mapping */
  0,                                 /* tp_hash */
  0,                                 /* tp_call */
  0,                                 /* tp_str */
  0,                                 /* tp_getattro */
  0,                                 /* tp_setattro */
  0,                                 /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,                /* tp_flags */
  NULL,                              /* tp_doc */
  0,                                 /* tp_traverse */
  0,                                 /* tp_clear */
  0,                                 /* tp_richcompare */
  0,                                 /* tp_weaklistoffset */
  0,                                 /* tp_iter */
  0,                                 /* tp_iternext */
  0,                                 /* tp_methods */
  CpStringAtom_Members,              /* tp_members */
  0,                                 /* tp_getset */
  0,                                 /* tp_base */
  0,                                 /* tp_dict */
  0,                                 /* tp_descr_get */
  0,                                 /* tp_descr_set */
  0,                                 /* tp_dictoffset */
  (initproc)cp_stringatom_init,      /* tp_init */
  0,                                 /* tp_alloc */
  (newfunc)cp_stringatom_new,        /* tp_new */
  0,                                 /* tp_free */
  0,                                 /* tp_is_gc */
  0,                                 /* tp_bases */
  0,                                 /* tp_mro */
  0,                                 /* tp_cache */
  0,                                 /* tp_subclasses */
  0,                                 /* tp_weaklist */
  0,                                 /* tp_del */
  0,                                 /* tp_version_tag */
  0,                                 /* tp_finalize */
  0,                                 /* tp_vectorcall */
  0,                                 /* tp_watched */
};
