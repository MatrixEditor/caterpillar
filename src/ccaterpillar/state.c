/* state and layer implementation */
#include "caterpillar/state.h"
#include "caterpillar/context.h"
#include "structmember.h"

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
  PyObject* size = 0;
  if (!PyArg_ParseTuple(args, "O", &size)) {
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
  PyObject* whence = NULL;
  if (!PyArg_ParseTuple(args, "OO", &offset, &whence)) {
    return NULL;
  }
  return CpState_Seek(self, offset, whence);
}

/* PUblic API */

/*CpAPI*/
CpStateObject*
CpState_New(PyObject* io)
{
  return (CpStateObject*)CpObject_CreateOneArg(&CpState_Type, io);
}

/*CpAPI*/
int
CpState_SetGlobals(CpStateObject* self, PyObject* globals)
{
  return cp_state_set_globals(self, globals, NULL);
}

/*CpAPI*/
PyObject*
CpState_Tell(CpStateObject* self)
{
  if (!self->m_io) {
    PyErr_SetString(PyExc_ValueError, "io is NULL!");
    return NULL;
  }
  return PyObject_CallMethodNoArgs(self->m_io, self->mod->str_tell);
}

/*CpAPI*/
PyObject*
CpState_Seek(CpStateObject* self, PyObject* offset, PyObject* whence)
{
  if (!self->m_io) {
    PyErr_SetString(PyExc_ValueError, "io is NULL!");
    return NULL;
  }
  return PyObject_CallMethodObjArgs(
    self->m_io, self->mod->str_seek, offset, whence, NULL);
}

/*CpAPI*/
PyObject*
CpState_ReadSsize_t(CpStateObject* self, Py_ssize_t size)
{
  PyObject* sizeobj = PyLong_FromSsize_t(size);
  PyObject* res = CpState_Read(self, sizeobj);
  Py_DECREF(sizeobj);
  return res;
}

/*CpAPI*/
PyObject*
CpState_Read(CpStateObject* self, PyObject* sizeobj)
{
  if (!self->m_io) {
    PyErr_SetString(PyExc_ValueError, "io is NULL!");
    return NULL;
  }
  PyObject* res =
    PyObject_CallMethodOneArg(self->m_io, self->mod->str_read, sizeobj);
  Py_DECREF(sizeobj);

  if (!res) {
    if (!PyErr_Occurred()) {
      PyErr_Format(PyExc_ValueError,
                   "read() returned NULL without error (possible size "
                   "overflow?). Tried to read %R bytes",
                   sizeobj);
    }
    return NULL;
  }

  Py_ssize_t length = 0;
  if ((length = PyObject_Length(res)) != PyLong_AsSsize_t(sizeobj)) {
    Py_DECREF(res);
    PyErr_Format(PyExc_ValueError,
                 "read() expected to return buffer with length %R, got %ld",
                 sizeobj,
                 length);
    return NULL;
  }
  return res;
}

/*CpAPI*/
PyObject*
CpState_ReadFully(CpStateObject* self)
{
  if (!self->m_io) {
    PyErr_SetString(PyExc_ValueError, "io is NULL!");
    return NULL;
  }
  return PyObject_CallMethodNoArgs(self->m_io, self->mod->str_read);
}

/*CpAPI*/
PyObject*
CpState_Write(CpStateObject* self, PyObject* value)
{
  if (!self->m_io) {
    PyErr_SetString(PyExc_ValueError, "io is NULL!");
    return NULL;
  }
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
  .tp_basicsize = sizeof(CpStateObject),
  .tp_dealloc = (destructor)cp_state_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_doc = NULL,
  .tp_methods = CpState_Methods,
  .tp_members = CpState_Members,
  .tp_getset = CpState_GetSetters,
  .tp_init = (initproc)cp_state_init,
  .tp_new = (newfunc)cp_state_new,
};