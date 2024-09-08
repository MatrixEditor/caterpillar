/* layer implementation */
#include "caterpillar/caterpillar.h"

#include <structmember.h>

/* top level layer impl */
static PyObject*
cp_layer_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpLayerObject* self;
  self = (CpLayerObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->m_path = NULL;
  self->m_parent = NULL;
  self->m_state = NULL;
  self->m_class = CpLayerClass_Default;
  return (PyObject*)self;
}

static void
cp_layer_dealloc(CpLayerObject* self)
{
  Py_XDECREF(self->m_path);
  Py_XDECREF(self->m_state);
  Py_XDECREF(self->m_parent);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_layer_init(CpLayerObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "state", "path", "parent", NULL };
  PyObject *state = NULL, *path = NULL, *parent = NULL;
  if (!PyArg_ParseTupleAndKeywords(
        args, kw, "O|OO", kwlist, &state, &path, &parent))
    return -1;

  if (!PyObject_IsInstance(state, (PyObject*)(&CpState_Type))) {
    PyErr_SetString(PyExc_TypeError, "state must be an instance of CpState");
    return -1;
  }

  Py_XSETREF(self->m_state, (CpStateObject*)Py_NewRef(state));
  _Cp_SetObj(self->m_path, path);
  Py_XSETREF(self->m_parent, (CpLayerObject*)Py_XNewRef(parent));
  return 0;
}

/*CpAPI*/
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
    Py_XSETREF(self->m_path, Py_XNewRef(parent->m_path));
  }
  return self;
}

/*CpAPI*/
int
CpLayer_Invalidate(CpLayerObject* self)
{
  if (!self) {
    PyErr_SetString(PyExc_ValueError, "layer must be non-null");
    return -1;
  }

  Py_XSETREF(self->m_parent, NULL);
  Py_XSETREF(self->m_state, NULL);
  Py_XSETREF(self->m_path, NULL);
  Py_CLEAR(self);
  return 0;
}

/* docs */

/* type */
static PyMemberDef CpLayer_Members[] = {
  { "state", T_OBJECT, offsetof(CpLayerObject, m_state), READONLY, "state" },
  { "path", T_OBJECT, offsetof(CpLayerObject, m_path), 0, "path" },
  { "parent", T_OBJECT, offsetof(CpLayerObject, m_parent), 0, "parent" },
  { NULL } /* Sentinel */
};

PyTypeObject CpLayer_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(layer),
  .tp_basicsize = sizeof(CpLayerObject),
  .tp_dealloc = (destructor)cp_layer_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_members = CpLayer_Members,
  .tp_init = (initproc)cp_layer_init,
  .tp_new = (newfunc)cp_layer_new,
};

//-------------------------------------------------------------------------------
// seq layer

static PyObject*
cp_seqlayer_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpSeqLayerObject* self = (CpSeqLayerObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;
  self->ob_base.m_path = NULL;
  self->m_sequence = NULL;
  self->m_length = -1;
  self->m_index = -1;
  self->s_greedy = false;
  self->ob_base.m_parent = NULL;
  self->ob_base.m_state = NULL;
  self->ob_base.m_class = CpLayerClass_Sequence;
  return (PyObject*)self;
}

static void
cp_seqlayer_dealloc(CpSeqLayerObject* self)
{
  Py_XDECREF(self->ob_base.m_path);
  Py_XDECREF(self->m_sequence);
  Py_XDECREF(self->ob_base.m_parent);
  Py_XDECREF(self->ob_base.m_state);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_seqlayer_init(CpSeqLayerObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "state", "path", "parent", NULL };
  PyObject *state = NULL, *sequence = NULL, *path = NULL, *parent = NULL;
  if (!PyArg_ParseTupleAndKeywords(
        args, kw, "O|OOO", kwlist, &state, &sequence, &path, &parent))
    return -1;

  if (!PyObject_IsInstance(state, (PyObject*)(&CpState_Type))) {
    PyErr_SetString(PyExc_TypeError, "state must be an instance of CpState");
    return -1;
  }

  Py_XSETREF(self->ob_base.m_state, (CpStateObject*)Py_NewRef(state));
  _Cp_SetObj(self->ob_base.m_path, path);
  Py_XSETREF(self->ob_base.m_parent, (CpLayerObject*)Py_XNewRef(parent));
  return 0;
}

/*CpAPI*/
int
CpSeqLayer_SetSequence(CpSeqLayerObject* self,
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
  return 0;
}

/*CpAPI*/
CpSeqLayerObject*
CpSeqLayer_New(CpStateObject* state, CpLayerObject* parent)
{
  CpSeqLayerObject* self =
    (CpSeqLayerObject*)CpObject_Create(&CpSeqLayer_Type, "O", state);
  if (!self) {
    return NULL;
  }
  if (parent) {
    Py_XSETREF(self->ob_base.m_parent, (CpLayerObject*)Py_XNewRef(parent));
    Py_XSETREF(self->ob_base.m_path, Py_XNewRef(parent->m_path));
  }
  return self;
}

/* docs */

/* type */
static PyMemberDef CpSeqLayer_Members[] = {
  {
    "sequence",
    T_OBJECT,
    offsetof(CpSeqLayerObject, m_sequence),
    READONLY,
  },
  {
    "length",
    T_PYSSIZET,
    offsetof(CpSeqLayerObject, m_length),
    0,
  },
  {
    "index",
    T_PYSSIZET,
    offsetof(CpSeqLayerObject, m_index),
    0,
  },
  { NULL } /* Sentinel */
};

PyTypeObject CpSeqLayer_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpSeqLayer_NAME),
  .tp_basicsize = sizeof(CpSeqLayerObject),
  .tp_dealloc = (destructor)cp_seqlayer_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_members = CpSeqLayer_Members,
  .tp_init = (initproc)cp_seqlayer_init,
  .tp_new = (newfunc)cp_seqlayer_new,
};

//-------------------------------------------------------------------------------
// obj layer

static PyObject*
cp_objlayer_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpObjLayerObject* self = (CpObjLayerObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;
  self->ob_base.m_path = NULL;
  self->m_obj = NULL;
  self->ob_base.m_parent = NULL;
  self->ob_base.m_state = NULL;
  self->ob_base.m_class = CpLayerClass_Object;
  return (PyObject*)self;
}

static void
cp_objlayer_dealloc(CpObjLayerObject* self)
{
  Py_XDECREF(self->ob_base.m_path);
  Py_XDECREF(self->m_obj);
  Py_XDECREF(self->ob_base.m_parent);
  Py_XDECREF(self->ob_base.m_state);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_objlayer_init(CpObjLayerObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "state", "path", "parent", NULL };
  PyObject *state = NULL, *path = NULL, *parent = NULL;
  if (!PyArg_ParseTupleAndKeywords(
        args, kw, "O|OO", kwlist, &state, &path, &parent))
    return -1;

  if (!PyObject_IsInstance(state, (PyObject*)(&CpState_Type))) {
    PyErr_SetString(PyExc_TypeError, "state must be an instance of CpState");
    return -1;
  }

  Py_XSETREF(self->ob_base.m_state, (CpStateObject*)Py_NewRef(state));
  Py_XSETREF(self->m_obj, (PyObject*)CpContext_New());
  Py_XSETREF(self->ob_base.m_path, Py_XNewRef(path));
  Py_XSETREF(self->ob_base.m_parent, (CpLayerObject*)Py_XNewRef(parent));
  return 0;
}

static PyObject*
cp_objlayer_context_getattr(CpLayerObject* self, PyObject* args)
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
    PyErr_Format(PyExc_ValueError, "CpObjLayer has no attribute '%s'", key);
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

/*CpAPI*/
CpObjLayerObject*
CpObjLayer_New(CpStateObject* state, CpLayerObject* parent)
{
  CpObjLayerObject* self = (CpObjLayerObject*)CpObject_CreateOneArg(
    &CpObjLayer_Type, (PyObject*)state);
  if (!self) {
    return NULL;
  }
  if (parent) {
    Py_XSETREF(self->ob_base.m_parent, (CpLayerObject*)Py_XNewRef(parent));
    Py_XSETREF(self->ob_base.m_path, Py_XNewRef(parent->m_path));
  }
  return self;
}

/* docs */

/* type */
static PyMemberDef CpObjLayer_Members[] = {
  {
    "obj",
    T_OBJECT,
    offsetof(CpObjLayerObject, m_obj),
    0,
  },
  { NULL } /* Sentinel */
};

static PyMethodDef CpObjLayer_Methods[] = {
  { "__context_getattr__",
    (PyCFunction)cp_objlayer_context_getattr,
    METH_VARARGS},
  { NULL } /* Sentinel */
};

PyTypeObject CpObjLayer_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpObjLayer_NAME),
  .tp_basicsize = sizeof(CpObjLayerObject),
  .tp_dealloc = (destructor)cp_objlayer_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_doc = NULL,
  .tp_methods = CpObjLayer_Methods,
  .tp_members = CpObjLayer_Members,
  .tp_init = (initproc)cp_objlayer_init,
  .tp_new = (newfunc)cp_objlayer_new,
};