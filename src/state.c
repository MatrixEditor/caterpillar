/* state and layer implementation */
#include "caterpillar/state.h"
#include "caterpillar/context.h"
#include "structmember.h"

/* layer implementation */
static PyObject*
cp_layer_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpLayerObject* self;
  self = (CpLayerObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->m_field = NULL;
  self->m_obj = NULL;
  self->m_value = NULL;
  self->m_path = NULL;
  self->m_sequence = NULL;
  self->m_length = -1;
  self->m_index = -1;
  self->s_greedy = false;
  self->s_sequential = false;
  self->m_parent = NULL;
  self->m_state = NULL;
  return (PyObject*)self;
}

static void
cp_layer_dealloc(CpLayerObject* self)
{
  Py_XDECREF(self->m_field);
  Py_XDECREF(self->m_obj);
  Py_XDECREF(self->m_value);
  Py_XDECREF(self->m_path);
  Py_XDECREF(self->m_sequence);
  Py_XDECREF(self->m_state);
  Py_XDECREF(self->m_parent);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_layer_init(CpLayerObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "state", "field",    "obj",    "value",
                            "path",  "sequence", "parent", NULL };
  PyObject *state = NULL, *field = NULL, *obj = NULL, *value = NULL,
           *path = NULL, *sequence = NULL, *parent = NULL, *next = NULL;
  if (!PyArg_ParseTupleAndKeywords(args,
                                   kw,
                                   "O|OOOOOOO",
                                   kwlist,
                                   &state,
                                   &field,
                                   &obj,
                                   &value,
                                   &path,
                                   &sequence,
                                   &parent,
                                   &next))
    return -1;

  if (!PyObject_IsInstance(state, (PyObject*)(&CpState_Type))) {
    PyErr_SetString(PyExc_TypeError, "state must be an instance of CpState");
    return -1;
  }

  Py_XSETREF(self->m_state, (CpStateObject*)Py_NewRef(state));
  _Cp_SetObj(self->m_field, field);
  _Cp_SetObj(self->m_obj, obj);
  _Cp_SetObj(self->m_value, value);
  _Cp_SetObj(self->m_path, path);
  _Cp_SetObj(self->m_sequence, sequence);
  Py_XSETREF(self->m_parent, (CpLayerObject*)Py_XNewRef(parent));
  self->s_greedy = false;
  self->m_index = -1;
  self->m_length = -1;
  self->s_sequential = false;
  return 0;
}

static PyObject*
cp_layer__context_getattr__(CpLayerObject* self, PyObject* args)
{
  _modulestate* state = get_global_module_state();
  PyObject *tmp = NULL, *lineValue = NULL, *lastKey = NULL, *key = NULL,
           *obj = NULL;
  if (!PyArg_ParseTuple(args, "O", &lineValue)) {
    return NULL;
  }

  PyObject* values = PyUnicode_Split(lineValue, state->str_path_delim, -1);
  if (!values) {
    return NULL;
  }

  size_t length = PyList_Size(values);
  if (length == 0) {
    Py_XDECREF(values);
    PyErr_SetString(PyExc_ValueError, "Empty path");
    return NULL;
  }

  key = PyList_GetItem(values, 0);
  if (!key) {
    Py_XDECREF(values);
    return NULL;
  }

  tmp = PyObject_GenericGetAttr((PyObject*)self, key);
  if (!tmp) {
    PyErr_Clear();
    PyErr_Format(PyExc_ValueError, "CpLayer has no attribute '%s'", key);
    Py_XDECREF(values);
    return NULL;
  }

  obj = tmp;
  Py_XSETREF(lastKey, Py_XNewRef(key));
  for (size_t i = 1; i < length; i++) {
    key = PyList_GetItem(values, i);
    if (!key) {
      Py_XDECREF(values);
      return NULL;
    }

    tmp = PyObject_GetAttr(obj, key);
    if (!tmp) {
      PyErr_Clear();
      PyErr_Format(
        PyExc_ValueError, "'%s' has no attribute '%s'", lastKey, key);
      Py_XDECREF(values);
      return NULL;
    }

    Py_XSETREF(obj, tmp);
    Py_XSETREF(lastKey, Py_XNewRef(key));
  }
  Py_XDECREF(values);
  return obj;
}

/* PUblic API */
CpLayerObject*
CpLayer_New(CpStateObject* state, CpLayerObject* parent)
{
  CpLayerObject* self =
    (CpLayerObject*)CpObject_Create(&CpLayer_Type, "O", state);
  if (!self) {
    return NULL;
  }
  if (parent) {
    Py_XSETREF(self->m_parent, (CpLayerObject*)Py_XNewRef(parent));
    // automatically inherit field object
    // TODO: document this
    Py_XSETREF(self->m_field, Py_XNewRef(parent->m_field));
  }
  return self;
}

int
CpLayer_SetSequence(CpLayerObject* self,
                    PyObject* sequence,
                    Py_ssize_t length,
                    int8_t greedy)
{
  if (!sequence || !self) {
    PyErr_SetString(PyExc_ValueError, "sequence and layer must be non-null");
    return -1;
  }

  Py_XSETREF(self->m_sequence, Py_NewRef(sequence));
  self->m_length = length;
  self->s_greedy = greedy;
  self->m_index = 0;
  self->s_sequential = false;
  return 0;
}

int
CpLayer_Invalidate(CpLayerObject* self)
{
  if (!self) {
    PyErr_SetString(PyExc_ValueError, "layer must be non-null");
    return -1;
  }

  Py_XSETREF(self->m_parent, NULL);
  Py_XSETREF(self->m_field, NULL);
  Py_XSETREF(self->m_value, NULL);
  Py_XSETREF(self->m_sequence, NULL);
  Py_XSETREF(self->m_obj, NULL);
  Py_XSETREF(self->m_state, NULL);
  Py_XSETREF(self->m_path, NULL);
  Py_CLEAR(self);
  return 0;
}

/* docs */

/* type */
static PyMemberDef CpLayer_Members[] = {
  { "state", T_OBJECT, offsetof(CpLayerObject, m_state), READONLY, "state" },
  { "field", T_OBJECT, offsetof(CpLayerObject, m_field), 0, "field" },
  { "obj", T_OBJECT, offsetof(CpLayerObject, m_obj), 0, "obj" },
  { "value", T_OBJECT, offsetof(CpLayerObject, m_value), 0, "value" },
  { "path", T_OBJECT, offsetof(CpLayerObject, m_path), 0, "path" },
  { "sequence", T_OBJECT, offsetof(CpLayerObject, m_sequence), 0, "sequence" },
  { "length",
    T_PYSSIZET,
    offsetof(CpLayerObject, m_length),
    READONLY,
    "length" },
  { "index", T_PYSSIZET, offsetof(CpLayerObject, m_index), READONLY, "index" },
  { "greedy", T_BOOL, offsetof(CpLayerObject, s_greedy), READONLY, "greedy" },
  { "sequential",
    T_INT,
    offsetof(CpLayerObject, s_sequential),
    READONLY,
    "sequential" },
  { "parent", T_OBJECT, offsetof(CpLayerObject, m_parent), 0, "parent" },
  { NULL } /* Sentinel */
};

static PyMethodDef CpLayer_Methods[] = {
  { "__context_getattr__",
    (PyCFunction)cp_layer__context_getattr__,
    METH_VARARGS },
  { NULL } /* Sentinel */
};

PyTypeObject CpLayer_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(layer),
  sizeof(CpLayerObject),        /* tp_basicsize */
  0,                            /* tp_itemsize */
  (destructor)cp_layer_dealloc, /* tp_dealloc */
  0,                            /* tp_vectorcall_offset */
  0,                            /* tp_getattr */
  0,                            /* tp_setattr */
  0,                            /* tp_as_async */
  0,                            /* tp_repr */
  0,                            /* tp_as_number */
  0,                            /* tp_as_sequence */
  0,                            /* tp_as_mapping */
  0,                            /* tp_hash */
  0,                            /* tp_call */
  0,                            /* tp_str */
  0,                            /* tp_getattro */
  0,                            /* tp_setattro */
  0,                            /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,           /* tp_flags */
  NULL,                         /* tp_doc */
  0,                            /* tp_traverse */
  0,                            /* tp_clear */
  0,                            /* tp_richcompare */
  0,                            /* tp_weaklistoffset */
  0,                            /* tp_iter */
  0,                            /* tp_iternext */
  CpLayer_Methods,              /* tp_methods */
  CpLayer_Members,              /* tp_members */
  0,                            /* tp_getset */
  0,                            /* tp_base */
  0,                            /* tp_dict */
  0,                            /* tp_descr_get */
  0,                            /* tp_descr_set */
  0,                            /* tp_dictoffset */
  (initproc)cp_layer_init,      /* tp_init */
  0,                            /* tp_alloc */
  (newfunc)cp_layer_new,        /* tp_new */
  0,                            /* tp_free */
  0,                            /* tp_is_gc */
  0,                            /* tp_bases */
  0,                            /* tp_mro */
  0,                            /* tp_cache */
  0,                            /* tp_subclasses */
  0,                            /* tp_weaklist */
  0,                            /* tp_del */
  0,                            /* tp_version_tag */
  0,                            /* tp_finalize */
  0,                            /* tp_vectorcall */
  0,                            /* tp_watched */
};

//-------------------------------------------------------------------------------
// state
static PyObject*
cp_state_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpStateObject* self = (CpStateObject*)type->tp_alloc(type, 0);
  if (!self) {
    return NULL;
  }
  self->mod = get_global_module_state();
  self->m_io = NULL;
  self->m_globals = (PyObject*)CpContext_New();
  self->m_offset_table = PyDict_New();
  return (PyObject*)self;
}

static void
cp_state_dealloc(CpStateObject* self)
{

  Py_CLEAR(self->m_io);
  Py_CLEAR(self->m_globals);
  Py_CLEAR(self->m_offset_table);
  self->mod = NULL;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_state_set_globals(CpStateObject* self, PyObject* globals, void*);

static int
cp_state_set_offset_table(CpStateObject* self, PyObject* offset_table, void*);

static int
cp_state_init(CpStateObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "io", "globals", "offset_table", NULL };
  PyObject *io = NULL, *globals = NULL, *offset_table = NULL;
  if (!PyArg_ParseTupleAndKeywords(
        args, kw, "|OOOO", kwlist, &io, &globals, &offset_table)) {
    return -1;
  }

  _Cp_SetObj(self->m_io, io);
  if (globals)
    if (cp_state_set_globals(self, globals, NULL) < 0)
      return -1;

  if (offset_table)
    if (cp_state_set_offset_table(self, offset_table, NULL) < 0) {
      return -1;
    }
  return 0;
}

static int
cp_state_set_globals(CpStateObject* self, PyObject* globals, void* unused)
{
  if (!globals) {
    PyErr_SetString(PyExc_ValueError, "globals is NULL!");
    return -1;
  }

  if (PyObject_IsInstance(globals, (PyObject*)&CpContext_Type)) {
    _Cp_SetObj(self->m_globals, globals);
  } else {
    if (!PyMapping_Check(globals)) {
      PyErr_SetString(PyExc_TypeError, "globals must be a mapping");
      return -1;
    }
    self->m_globals = CpObject_CreateOneArg(&CpContext_Type, globals);
  }
  return 0;
}

static PyObject*
cp_state_get_globals(CpStateObject* self)
{
  return Py_NewRef(self->m_globals ? self->m_globals : Py_None);
}

static int
cp_state_set_offset_table(CpStateObject* self,
                          PyObject* offset_table,
                          void* unused)
{
  if (!offset_table) {
    PyErr_SetString(PyExc_ValueError, "offset_table is NULL!");
    return -1;
  }
  if (!PyMapping_Check(offset_table)) {
    PyErr_SetString(PyExc_TypeError, "offset_table must be a mapping");
    return -1;
  }
  _Cp_SetObj(self->m_offset_table, offset_table);
  return 0;
}

static PyObject*
cp_state_get_offset_table(CpStateObject* self)
{
  return Py_NewRef(self->m_offset_table ? self->m_offset_table : Py_None);
}

static PyObject*
cp_state_write(CpStateObject* self, PyObject* args)
{
  PyObject* value = NULL;
  if (!PyArg_ParseTuple(args, "O", &value)) {
    return NULL;
  }
  return CpState_Write(self, value);
}

static PyObject*
cp_state_read(CpStateObject* self, PyObject* args)
{
  Py_ssize_t size = 0;
  if (!PyArg_ParseTuple(args, "n", &size)) {
    return NULL;
  }
  return CpState_Read(self, size);
}

static PyObject*
cp_state_tell(CpStateObject* self)
{
  return CpState_Tell(self);
}

static PyObject*
cp_state_seek(CpStateObject* self, PyObject* args)
{
  PyObject* offset = NULL;
  int whence = 0;
  if (!PyArg_ParseTuple(args, "O|i", &offset, &whence)) {
    return NULL;
  }
  return CpState_Seek(self, offset, whence);
}

/* PUblic API */
CpStateObject*
CpState_New(PyObject* io)
{
  return (CpStateObject*)CpObject_CreateOneArg(&CpState_Type, io);
}

int
CpState_SetGlobals(CpStateObject* self, PyObject* globals)
{
  return cp_state_set_globals(self, globals, NULL);
}

PyObject*
CpState_Tell(CpStateObject* self)
{
  return PyObject_CallMethodNoArgs(self->m_io, self->mod->str_tell);
}

PyObject*
CpState_Seek(CpStateObject* self, PyObject* offset, int whence)
{
  return PyObject_CallMethodObjArgs(
    self->m_io, self->mod->str_seek, offset, whence);
}

PyObject*
CpState_Read(CpStateObject* self, Py_ssize_t size)
{
  PyObject* sizeobj = PyLong_FromSsize_t(size);
  PyObject* res =
    PyObject_CallMethodOneArg(self->m_io, self->mod->str_read, sizeobj);
  Py_DECREF(sizeobj);
  return res;
}

PyObject*
CpState_Write(CpStateObject* self, PyObject* value)
{
  return PyObject_CallMethodOneArg(self->m_io, self->mod->str_write, value);
}

/* docs */

/* members */
static PyGetSetDef CpState_GetSetters[] = {
  { "globals",
    (getter)cp_state_get_globals,
    (setter)cp_state_set_globals,
    NULL,
    NULL },
  { "offset_table",
    (getter)cp_state_get_offset_table,
    (setter)cp_state_set_offset_table,
    NULL,
    NULL },
  { NULL },
};

static PyMemberDef CpState_Members[] = {
  { "io", T_OBJECT, offsetof(CpStateObject, m_io), 0, NULL },
  { "globals", T_OBJECT, offsetof(CpStateObject, m_globals), 0, NULL },
  { "offset_table",
    T_OBJECT,
    offsetof(CpStateObject, m_offset_table),
    0,
    NULL },
  { NULL } /* Sentinel */
};

static PyMethodDef CpState_Methods[] = {
  { "write", (PyCFunction)cp_state_write, METH_VARARGS },
  { "read", (PyCFunction)cp_state_read, METH_VARARGS },
  { "tell", (PyCFunction)cp_state_tell, METH_NOARGS },
  { "seek", (PyCFunction)cp_state_seek, METH_VARARGS },
  { NULL } /* Sentinel */
};

/* type */
PyTypeObject CpState_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(State),
  sizeof(CpStateObject),        /* tp_basicsize */
  0,                            /* tp_itemsize */
  (destructor)cp_state_dealloc, /* tp_dealloc */
  0,                            /* tp_vectorcall_offset */
  0,                            /* tp_getattr */
  0,                            /* tp_setattr */
  0,                            /* tp_as_async */
  0,                            /* tp_repr */
  0,                            /* tp_as_number */
  0,                            /* tp_as_sequence */
  0,                            /* tp_as_mapping */
  0,                            /* tp_hash */
  0,                            /* tp_call */
  0,                            /* tp_str */
  0,                            /* tp_getattro */
  0,                            /* tp_setattro */
  0,                            /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,           /* tp_flags */
  NULL,                         /* tp_doc */
  0,                            /* tp_traverse */
  0,                            /* tp_clear */
  0,                            /* tp_richcompare */
  0,                            /* tp_weaklistoffset */
  0,                            /* tp_iter */
  0,                            /* tp_iternext */
  CpState_Methods,              /* tp_methods */
  CpState_Members,              /* tp_members */
  CpState_GetSetters,           /* tp_getset */
  0,                            /* tp_base */
  0,                            /* tp_dict */
  0,                            /* tp_descr_get */
  0,                            /* tp_descr_set */
  0,                            /* tp_dictoffset */
  (initproc)cp_state_init,      /* tp_init */
  0,                            /* tp_alloc */
  (newfunc)cp_state_new,        /* tp_new */
  0,                            /* tp_free */
  0,                            /* tp_is_gc */
  0,                            /* tp_bases */
  0,                            /* tp_mro */
  0,                            /* tp_cache */
  0,                            /* tp_subclasses */
  0,                            /* tp_weaklist */
  0,                            /* tp_del */
  0,                            /* tp_version_tag */
  0,                            /* tp_finalize */
  0,                            /* tp_vectorcall */
  0,                            /* tp_watched */
};