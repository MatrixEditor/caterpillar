/* context and context path implementation */
#include "caterpillar/caterpillar.h"
#include "private.h"
#include "structmember.h"

/* impl */
static int
cp_context_init(CpContextObject* self, PyObject* args, PyObject* kw)
{
  return PyDict_Type.tp_init((PyObject*)&self->m_dict, args, kw) < 0;
}

static int
cp_context__setattr__(CpContextObject* self, char* name, PyObject* value)
{
  return PyDict_SetItemString((PyObject*)&self->m_dict, name, value);
}

static PyObject*
cp_context__context_getattr__(CpContextObject* self, PyObject* args)
{
  PyObject* name = NULL;
  if (!PyArg_ParseTuple(args, "O", &name)) {
    return NULL;
  }
  return CpContext_GenericGetAttr((PyObject*)self, name);
}

static PyObject*
cp_context__context_setattr__(CpContextObject* self, PyObject* args)
{
  PyObject *name = NULL, *value = NULL;
  if (!PyArg_ParseTuple(args, "OO", &name, &value)) {
    return NULL;
  }
  return CpContext_GenericSetAttr((PyObject*)self, name, value) < 0
           ? NULL
           : Py_NewRef(Py_None);
}

static PyObject*
cp_context__getattro__(CpContextObject* self, PyObject* name)
{
  PyObject* result = PyObject_GenericGetAttr((PyObject*)&self->m_dict, name);
  if (result)
    return result;
  PyErr_Clear();

  // try to resolve via __getitem__ call
  result = PyDict_GetItem((PyObject*)&self->m_dict, name);
  if (result)
    return Py_NewRef(result);

  PyErr_Clear();
  return CpContext_GenericGetAttr((PyObject*)self, name);
}

static PyObject*
cp_context__getattr__(CpContextObject* self, const char* path)
{
  PyObject* result = PyObject_GetAttrString((PyObject*)&self->m_dict, path);
  if (result)
    return result;

  PyErr_Clear();
  // try to resolve via __getitem__ call
  result = PyDict_GetItemString((PyObject*)&self->m_dict, path);
  if (result)
    return Py_NewRef(result);

  PyErr_Clear();
  return CpContext_GenericGetAttrString((PyObject*)self, path);
}

static PyObject*
cp_context_get_root(CpContextObject* self, void* closure)
{
  return CpContext_GetRoot((PyObject*)self);
}

/* public API */

/*CpAPI*/
PyObject*
CpContext_GenericGetAttrString(PyObject* context, const char* path)
{
  PyObject *pathObj = NULL, *result = NULL;
  if (!path) {
    PyErr_SetString(PyExc_ValueError, "Path must not be NULL!");
    goto finish;
  }

  pathObj = PyUnicode_FromString(path);
  if (!pathObj) {
    goto finish;
  }

  result = CpContext_GenericGetAttr(context, pathObj);
finish:
  Py_XDECREF(pathObj);
  return result;
}

/*CpAPI*/
PyObject*
CpContext_GenericGetAttr(PyObject* context, PyObject* path)
{
  _modulestate* state = get_global_module_state();
  PyObject* str = PyObject_Repr(path);
  // Names starting with 'n' contain a NEW reference to a
  // Python object, whereas variables starting with 'b'
  // store a borrowed reference.
  PyObject *nObj = NULL, *nValues = NULL, *nTmp = NULL, *nLastKey = NULL;
  PyObject* bKey = NULL;
  size_t length = 0;

  // We should not assert that context and path are NOT NULL,
  // due to the nature of this method. (exported API)
  if (!context) {
    PyErr_SetString(PyExc_ValueError, "Context must not be NULL!");
    goto error;
  }

  if (!path) {
    PyErr_SetString(PyExc_ValueError, "Path must not be NULL!");
    goto error;
  }

  // At first, we will split up the path into several elements
  nValues = PyUnicode_Split(path, state->str__path_sep, -1);
  if (!nValues) {
    goto error;
  }

  length = PyList_Size(nValues);
  if (length == 0) {
    PyErr_SetString(PyExc_ValueError, "Empty or invalid path!");
    goto error;
  }

  bKey = PyList_GetItem(nValues, 0);
  if (!bKey) {
    goto error;
  }

  // go through each element and use object.__getattr__ for each of them
  nTmp = PyObject_GetItem(context, bKey);
  if (!nTmp) {
    // not even present on the top layer -> invalid path
    PyErr_Clear();
    nTmp = PyObject_GenericGetAttr(context, bKey);
    if (!nTmp) {
      goto error;
    }
  }

  Py_XSETREF(nObj, Py_XNewRef(nTmp));
  Py_XSETREF(nLastKey, Py_XNewRef(bKey));
  for (size_t depth = 1; depth < length; ++depth) {
    // Fetch each path element and use getattr(nObj, bKey)
    // for each of them.
    bKey = PyList_GetItem(nValues, depth);
    if (!bKey) {
      goto error;
    }

    Py_XSETREF(nTmp, PyObject_GetAttr(nObj, bKey));
    if (!nTmp) {
      PyErr_Clear();
      PyErr_Format(PyExc_ValueError,
                   "%R has no attribute %R in path %R",
                   nLastKey,
                   bKey,
                   path);
      goto error;
    }

    Py_SETREF(nObj, Py_NewRef(nTmp));
    Py_SETREF(nLastKey, Py_NewRef(bKey));
  }
  goto success;

error:
  Py_XSETREF(nObj, NULL);

success:
  Py_XDECREF(nValues);
  Py_XDECREF(nTmp);
  Py_XDECREF(nLastKey);

  // already a new reference, we don't have to use Py_NewRef here.
  return nObj;
}

/*CpAPI*/
PyObject*
CpContext_GetRoot(PyObject* pObj)
{
  // TODO: NULL check
  _modulestate* state = get_global_module_state();
  PyObject* nRoot = NULL;
  if (!pObj) {
    PyErr_SetString(PyExc_ValueError, "Context must not be NULL!");
    return NULL;
  }

  nRoot = CpContext_ITEM(pObj, state->str__context_root);
  if (nRoot)
    return nRoot;

  PyErr_Clear();
  return Py_NewRef(pObj);
}

/*CpAPI*/
int
CpContext_GenericSetAttrString(PyObject* pContext,
                               const char* pPath,
                               PyObject* pValue)
{
  PyObject* nPathObj = NULL;
  int vResult = 0;
  if (!pPath) {
    PyErr_SetString(PyExc_ValueError, "Path must not be NULL!");
    goto finish;
  }

  nPathObj = PyUnicode_FromString(pPath);
  if (!nPathObj) {
    goto finish;
  }

  vResult = CpContext_GenericSetAttr(pContext, nPathObj, pValue);
finish:
  Py_XDECREF(nPathObj);
  return vResult;
}

/*CpAPI*/
int
CpContext_GenericSetAttr(PyObject* pContext, PyObject* pPath, PyObject* pValue)
{
  _modulestate* state = get_global_module_state();
  PyObject *nElemets = NULL, *nMaxSplit = PyLong_FromLong(1), *nObj = NULL,
           *bNewPath = NULL, *bTarget = NULL;
  int error = 0;
  if (!nMaxSplit)
    goto error;

  if (!pContext) {
    PyErr_SetString(PyExc_ValueError, "Context object must not be NULL!");
    goto error;
  }
  if (!pPath) {
    PyErr_SetString(PyExc_ValueError, "Target path must not be NULL!");
    goto error;
  }

  // [0] - path to the object storing the target attribute
  // [1] - target attribute
  nElemets = PyObject_CallMethodObjArgs(
    pPath, state->str__fn_rsplit, state->str__path_sep, nMaxSplit, NULL);
  if (!nElemets)
    goto error;

  // if length is one, set the attribute directly
  if (PyList_Size(nElemets) == 1) {
    if (PyObject_SetItem(
          pContext, pPath, pValue ? pValue : Py_NewRef(Py_None)) < 0)
      goto error;
  } else {
    bNewPath = PyList_GetItem(nElemets, 0);
    if (!bNewPath)
      goto error;

    nObj = CpContext_GenericGetAttr(pContext, bNewPath);
    if (!nObj)
      goto error;

    bTarget = PyList_GetItem(nElemets, 1);
    if (!bTarget)
      goto error;

    if (PyObject_SetAttr(nObj, bTarget, pValue ? pValue : Py_NewRef(Py_None)) <
        0)
      goto error;
  }
  goto success;

error:
  error = -1;

success:
  Py_XDECREF(nObj);
  Py_XDECREF(nElemets);
  Py_XDECREF(nMaxSplit);
  return error;
}

/*CpAPI*/
PyObject*
CpContextIO_Tell(PyObject* pContext)
{
  PyObject *nResult = NULL, *nIO = NULL;
  _modulestate* state = get_global_module_state();

  _Cp_AssignCheck(nIO, CpContext_IO(pContext, state), error);
  _Cp_AssignCheck(
    nResult, PyObject_CallMethodNoArgs(nIO, state->str__io_tell), error);
  goto success;

error:
  Py_CLEAR(nResult);

success:
  Py_XDECREF(nIO);
  return nResult;
}

/*CpAPI*/
PyObject*
CpContextIO_Seek(PyObject* pContext, PyObject* pOffset, PyObject* pWhence)
{
  PyObject *nResult = NULL, *nIO = NULL;
  _modulestate* state = get_global_module_state();

  _Cp_AssignCheck(nIO, CpContext_IO(pContext, state), error);
  _Cp_AssignCheck(nResult,
                  PyObject_CallMethodObjArgs(
                    nIO, state->str__io_seek, pOffset, pWhence, NULL),
                  error);
  goto success;

error:
  Py_CLEAR(nResult);

success:
  Py_XDECREF(nIO);
  return nResult;
}

/*CpAPI*/
PyObject*
CpContextIO_Read(PyObject* pContext, PyObject* pSize)
{
  PyObject *nResult = NULL, *nIO = NULL;
  _modulestate* state = get_global_module_state();

  _Cp_AssignCheck(nIO, CpContext_IO(pContext, state), error);
  _Cp_AssignCheck(
    nResult,
    PyObject_CallMethodObjArgs(nIO, state->str__io_read, pSize, NULL),
    error);
  goto success;

error:
  Py_CLEAR(nResult);

success:
  Py_XDECREF(nIO);
  return nResult;
}

/*CpAPI*/
PyObject*
CpContextIO_ReadSsize_t(PyObject* pContext, Py_ssize_t pSize)
{
  PyObject *nResult = NULL, *nSize = NULL;

  _Cp_AssignCheck(nSize, PyLong_FromSsize_t(pSize), error);
  _Cp_AssignCheck(nResult, CpContextIO_Read(pContext, nSize), error);

error: // == success:
  Py_XDECREF(nSize);
  return nResult;
}

/*CpAPI*/
PyObject*
CpContextIO_ReadFully(PyObject* pContext)
{
  PyObject *nResult = NULL, *nIO = NULL;
  _modulestate* state = get_global_module_state();

  _Cp_AssignCheck(nIO, CpContext_IO(pContext, state), error);
  _Cp_AssignCheck(
    nResult, PyObject_CallMethodNoArgs(nIO, state->str__io_read), error);
  goto success;

error:
  Py_CLEAR(nResult);

success:
  Py_XDECREF(nIO);
  return nResult;
}

/*CpAPI*/
PyObject*
CpContextIO_WriteBytes(PyObject* pContext, PyObject* pData)
{
  PyObject *nResult = NULL, *nIO = NULL;
  _modulestate* state = get_global_module_state();

  _Cp_AssignCheck(nIO, CpContext_IO(pContext, state), error);
  _Cp_AssignCheck(
    nResult,
    PyObject_CallMethodObjArgs(nIO, state->str__io_write, pData, NULL),
    error);
  goto success;

error:
  Py_CLEAR(nResult);

success:
  Py_XDECREF(nIO);
  return nResult;
}

/*CpAPI*/
PyObject*
CpContextIO_Write(PyObject* pContext, const char* pData, Py_ssize_t pSize)
{
  PyObject *nResult = NULL, *nData = NULL;

  _Cp_AssignCheck(nData, PyUnicode_FromStringAndSize(pData, pSize), error);
  _Cp_AssignCheck(nResult, CpContextIO_WriteBytes(pContext, nData), error);

error: // == success:
  Py_XDECREF(nData);
  return nResult;
}

/* docs */

PyDoc_STRVAR(cp_context__doc__, "\
c_Context(**kwargs)\n\
--\n\
Represents a context object with attribute-style access.\n\
\n\
:param kwargs: The name and value of each keyword argument are used to \
initialize the context.\n\
:type kwargs: dict\n\
");

/* type setup */
static PyMethodDef CpContext_Methods[] = {
  { "__context_getattr__",
    (PyCFunction)cp_context__context_getattr__,
    METH_VARARGS,
    "Gets an attribute from the context" },
  { "__context_setattr__",
    (PyCFunction)cp_context__context_setattr__,
    METH_VARARGS,
    NULL },
  { NULL } /* Sentinel */
};

static PyGetSetDef CpContext_GetSets[] = {
  { "_root", (getter)cp_context_get_root, NULL, NULL, NULL },
  { NULL },
};

PyTypeObject CpContext_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpContext_NAME),
  .tp_basicsize = sizeof(CpContextObject),
  .tp_setattr = (setattrfunc)cp_context__setattr__,
  .tp_getattr = (getattrfunc)cp_context__getattr__,
  .tp_getattro = (getattrofunc)cp_context__getattro__,
  .tp_getset = CpContext_GetSets,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = cp_context__doc__,
  .tp_methods = CpContext_Methods,
  .tp_init = (initproc)cp_context_init,
};

/* init */
int
cp_context__mod_types()
{
  CpContext_Type.tp_base = &PyDict_Type;
  CpModule_SetupType(&CpContext_Type, -1);
  return 0;
}

int
cp_context__mod_init(PyObject* m, _modulestate* state)
{
  // constant path separator to eliminate creating the string
  // every time.
  _CACHED_STRING(state, str__path_sep, ".", -1);
  _CACHED_STRING(state, str__context_root, "_root", -1);
  _CACHED_STRING(state, str__fn_rsplit, "rsplit", -1);
  _CACHED_STRING(state, str__context_parent, "_parent", -1);
  _CACHED_STRING(state, str__context_io, "_io", -1);
  _CACHED_STRING(state, str__context_length, "_length", -1);
  _CACHED_STRING(state, str__context_index, "_index", -1);
  _CACHED_STRING(state, str__context_path, "_path", -1);
  _CACHED_STRING(state, str__context_obj, "_obj", -1);
  _CACHED_STRING(state, str__context_is_seq, "_is_seq", -1);
  _CACHED_STRING(state, str__context_field, "_field", -1);
  _CACHED_STRING(state, str__value, "value", -1);
  _CACHED_STRING(state, str__context_list, "_lst", -1);
  _CACHED_STRING(state, str__io_read, "read", -1);
  _CACHED_STRING(state, str__io_write, "write", -1);
  _CACHED_STRING(state, str__io_seek, "seek", -1);
  _CACHED_STRING(state, str__io_tell, "tell", -1);
  _CACHED_STRING(state, str__context_offsets, "_offsets", -1);
  _CACHED_STRING(state, str__io_getvalue, "getvalue", -1);

  CpModule_AddObject(CpContext_NAME, &CpContext_Type, -1);
  return 0;
}

void
cp_context__mod_clear(PyObject* m, _modulestate* state)
{
  Py_CLEAR(state->str__path_sep);
  Py_CLEAR(state->str__context_root);
  Py_CLEAR(state->str__fn_rsplit);
  Py_CLEAR(state->str__context_parent);
  Py_CLEAR(state->str__context_io);
  Py_CLEAR(state->str__context_length);
  Py_CLEAR(state->str__context_index);
  Py_CLEAR(state->str__context_path);
  Py_CLEAR(state->str__context_obj);
  Py_CLEAR(state->str__context_is_seq);
  Py_CLEAR(state->str__context_field);
  Py_CLEAR(state->str__value);
  Py_CLEAR(state->str__context_list);
  Py_CLEAR(state->str__io_read);
  Py_CLEAR(state->str__io_write);
  Py_CLEAR(state->str__io_seek);
  Py_CLEAR(state->str__io_tell);
  Py_CLEAR(state->str__context_offsets);
  Py_CLEAR(state->str__io_getvalue);
}