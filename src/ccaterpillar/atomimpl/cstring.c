/* c-string atom implementation */

#include "caterpillar/caterpillar.h"

#include <structmember.h>
#include <unicodeobject.h>

/* impl */
static PyObject*
cp_cstringatom_type(CpCStringAtomObject* self)
{
  return Py_NewRef(&PyUnicode_Type);
}

static PyObject*
cp_cstringatom_size(CpCStringAtomObject* self, CpLayerObject* layer)
{
  if (self->s_number) {
    return Py_NewRef(self->m_length);
  }
  PyErr_SetString(PyExc_ValueError,
                  "dynamic-sized c-string atoms do not have a static size");
  return NULL;
}

static PyObject*
cp_cstringatom_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
  CpCStringAtomObject* self = (CpCStringAtomObject*)type->tp_alloc(type, 0);
  if (self != NULL) {
    CpBuiltinAtom_CATOM(self).ob_pack = (packfunc)CpCStringAtom_Pack;
    CpBuiltinAtom_CATOM(self).ob_unpack = (unpackfunc)CpCStringAtom_Unpack;
    CpBuiltinAtom_CATOM(self).ob_pack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_unpack_many = NULL;
    CpBuiltinAtom_CATOM(self).ob_size = (sizefunc)cp_cstringatom_size;
    CpBuiltinAtom_CATOM(self).ob_type = (typefunc)cp_cstringatom_type;
    CpBuiltinAtom_CATOM(self).ob_bits = NULL;

    self->m_length = NULL;
    self->m_encoding = NULL;
    self->m_errors = NULL;
    self->m_terminator = NULL;
    self->_m_terminator_bytes = NULL;
    self->s_keep_terminator = false;
    self->s_number = false;
    self->s_callable = false;
    self->s_greedy = false;
  }
  return (PyObject*)self;
}

static void
cp_cstringatom_dealloc(CpCStringAtomObject* self)
{
  Py_XDECREF(self->m_length);
  Py_XDECREF(self->m_encoding);
  Py_XDECREF(self->m_errors);
  Py_XDECREF(self->m_terminator);
  Py_XDECREF(self->_m_terminator_bytes);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_cstringatom_init(CpCStringAtomObject* self, PyObject* args, PyObject* kwds)
{
  static char* kwlist[] = { "length",     "encoding", "errors",
                            "sep", "keep",     NULL };
  PyObject* length = NULL;
  PyObject* encoding = NULL;
  PyObject* errors = NULL;
  PyObject* terminator = NULL;
  int keep_terminator = false;
  if (!PyArg_ParseTupleAndKeywords(args,
                                   kwds,
                                   "|OOOOp",
                                   kwlist,
                                   &length,
                                   &encoding,
                                   &errors,
                                   &terminator,
                                   &keep_terminator)) {
    return -1;
  }

  _modulestate* mod = get_global_module_state();

  _Cp_SetObj(self->m_length, length);
  if (!self->m_length) {
    // TODO: document this
    _Cp_SetObj(self->m_length, Py_Ellipsis);
  }

  _Cp_SetObj(self->m_encoding, encoding);
  if (!self->m_encoding) {
    Py_XSETREF(self->m_encoding, mod->str_utf8);
  }

  _Cp_SetObj(self->m_errors, errors);
  if (!self->m_errors) {
    Py_XSETREF(self->m_errors, mod->str_strict);
  }

  _Cp_SetObj(self->m_terminator, terminator);
  if (!self->m_terminator) {
    _Cp_SetObj(self->_m_terminator_bytes, mod->cp_bytes__false);
    _Cp_SetObj(self->m_terminator, mod->str_cstring_default_pad);
  } else {
    if (!PyUnicode_Check(self->m_terminator)) {
      PyErr_SetString(PyExc_TypeError, "terminator must be a string");
      return -1;
    }
    self->_m_terminator_bytes =
      PyUnicode_AsEncodedString(self->m_terminator,
                                PyUnicode_AsUTF8AndSize(self->m_encoding, NULL),
                                PyUnicode_AsUTF8AndSize(self->m_errors, NULL));
    if (!self->_m_terminator_bytes) {
      return -1;
    }
  }

  self->s_keep_terminator = keep_terminator;
  self->s_number = PyLong_Check(self->m_length);
  self->s_callable = PyCallable_Check(self->m_length);
  self->s_greedy = Py_IS_TYPE(self->m_length, &PyEllipsis_Type);
  return 0;
}

static PyObject*
cp_cstringatom_repr(CpCStringAtomObject* self)
{
  return PyUnicode_FromFormat(
    "<cstring [%R %R]>", self->m_encoding, self->m_errors);
}

/* Public API */

/*CpAPI*/
int
CpCStringAtom_Pack(CpCStringAtomObject* self,
                   PyObject* value,
                   CpLayerObject* layer)
{
  if (!PyUnicode_Check(value)) {
    PyErr_Format(
      PyExc_TypeError, "C strings must be packed from unicode - got %R", value);
    return -1;
  }
  PyObject* bytes = PyUnicode_AsEncodedString(
    value, PyUnicode_DATA(self->m_encoding), PyUnicode_DATA(self->m_errors));
  if (!bytes) {
    return -1;
  }

  if (!self->s_callable && !self->s_number && !self->s_greedy) {
    // is atom, must pack length as prefix
    PyObject* length = PyLong_FromSsize_t(PyUnicode_GET_LENGTH(value) + 1);
    if (!length) {
      return -1;
    }
    if (_Cp_Pack(length, self->m_length, layer)) {
      Py_DECREF(length);
      return -1;
    }
    Py_DECREF(length);
  }

  PyObject* res = CpState_Write(layer->m_state, bytes);
  Py_DECREF(bytes);
  if (!res) {
    return -1;
  }
  Py_XDECREF(res);

  if (self->s_greedy || (!self->s_callable && !self->s_number)) {
    res = CpState_Write(layer->m_state, self->_m_terminator_bytes);
    if (!res) {
      return -1;
    }
    Py_XDECREF(res);
  } else {
    // NOTE: we know unpack won't be called
    PyObject* length = CpCStringAtom_Length(self, layer);
    if (length == NULL) {
      return -1;
    }
    PyObject* objLength = PyLong_FromSsize_t(PyUnicode_GET_LENGTH(value));
    if (!objLength) {
      Py_DECREF(length);
      return -1;
    }

    PyObject* realLength = PyNumber_Subtract(length, objLength);
    if (!realLength) {
      Py_DECREF(length);
      return -1;
    }

    PyObject* trailer =
      PyNumber_Multiply(self->_m_terminator_bytes, realLength);
    Py_DECREF(objLength);
    Py_DECREF(realLength);
    Py_DECREF(length);
    if (!trailer) {
      return -1;
    }

    res = CpState_Write(layer->m_state, trailer);
    Py_DECREF(trailer);
    if (!res) {
      return -1;
    }
    Py_XDECREF(res);
  }
  return 0;
}

/*CpAPI*/
PyObject*
CpCStringAtom_Unpack(CpCStringAtomObject* self, CpLayerObject* layer)
{
  PyObject* length = CpCStringAtom_Length(self, layer);
  if (length == NULL) {
    return NULL;
  }

  PyObject* result = NULL;
  if (Py_IsNone(length)) {
    // greedy parsing
    result = CpObject_CreateNoArgs(&PyBytes_Type);
    if (!result) {
      return NULL;
    }
    // REVISIT: is this efficient?
    while (true) {
      PyObject* bytes = CpState_ReadSsize_t(layer->m_state, 1);
      if (!bytes) {
        return NULL;
      }
      if (PyBytes_AS_STRING(bytes)[0] ==
          PyBytes_AS_STRING(self->_m_terminator_bytes)[0]) {
        break;
      }
      PyBytes_Concat(&result, bytes);
      Py_DECREF(bytes);
      if (!result) {
        return NULL;
      }
    }
  } else {
    result = CpState_Read(layer->m_state, length);
    Py_DECREF(length);
    if (!result) {
      return NULL;
    }
  }
  if (!result) {
    return NULL;
  }
  PyObject* string = PyUnicode_Decode(PyBytes_AS_STRING(result),
                                      PyBytes_GET_SIZE(result),
                                      PyUnicode_DATA(self->m_encoding),
                                      PyUnicode_DATA(self->m_errors));
  Py_XDECREF(result);
  if (!string) {
    return NULL;
  }

  if (!self->s_keep_terminator) {
    Py_XSETREF(string, _PyUnicode_XStrip(string, 1, self->m_terminator));
  }
  return string;
}

/* docs */

/* type */
static PyMemberDef CpCStringAtom_Members[] = {
  { "encoding",
    T_OBJECT_EX,
    offsetof(CpCStringAtomObject, m_encoding),
    0,
    "the encoding of the string" },
  { "errors",
    T_OBJECT_EX,
    offsetof(CpCStringAtomObject, m_errors),
    0,
    "the error handling for the string" },
  { "terminator",
    T_OBJECT_EX,
    offsetof(CpCStringAtomObject, m_terminator),
    READONLY,
    "the terminator for the string" },
  { "keep_terminator",
    T_BOOL,
    offsetof(CpCStringAtomObject, s_keep_terminator),
    0,
    "whether to keep the terminator" },
  { NULL }
};

PyTypeObject CpCStringAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpCStringAtom_NAME),
  .tp_basicsize = sizeof(CpCStringAtomObject),
  .tp_itemsize = 0,
  .tp_dealloc = (destructor)cp_cstringatom_dealloc,
  .tp_repr = (reprfunc)cp_cstringatom_repr,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = (newfunc)cp_cstringatom_new,
  .tp_members = CpCStringAtom_Members,
  .tp_init = (initproc)cp_cstringatom_init,
  .tp_doc = NULL,
};