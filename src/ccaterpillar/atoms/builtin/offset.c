#include "../../private.h"
#include "caterpillar/caterpillar.h"

#include <structmember.h>

static PyObject*
cp_offsetatom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpOffsetAtomObject* self;
  _Cp_AssignCheck(self, (CpOffsetAtomObject*)type->tp_alloc(type, 0), error);

  CpBuiltinAtom_ATOM(self).ob_bits = NULL;
  CpBuiltinAtom_ATOM(self).ob_pack = CpOffsetAtom_Pack;
  CpBuiltinAtom_ATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_ATOM(self).ob_unpack = CpOffsetAtom_Unpack;
  CpBuiltinAtom_ATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_ATOM(self).ob_type = CpOffsetAtom_TypeOf;
  CpBuiltinAtom_ATOM(self).ob_size = CpOffsetAtom_Size;
  self->m_atom = NULL;
  self->m_offset = NULL;
  self->m_whence = NULL;
  self->s_is_number = false;
  self->s_keep_pos = false;

  return _Cp_CAST(PyObject*, self);
error:
  return NULL;
}

static void
cp_offsetatom_dealloc(CpOffsetAtomObject* self)
{
  Py_CLEAR(self->m_atom);
  Py_CLEAR(self->m_offset);
  Py_CLEAR(self->m_whence);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_offsetatom_init(CpOffsetAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "atom", "offset", "whence", "keep_pos", NULL };
  PyObject *bAtom = NULL, *bOffset = NULL;
  int whence = PY_SEEK_SET, keepPos = false;
  if (!PyArg_ParseTupleAndKeywords(
        args, kw, "OO|ip", kwlist, &bAtom, &bOffset, &whence, &keepPos)) {
    return -1;
  }
  _Cp_SetObj(self->m_atom, bAtom);
  _Cp_SetObj(self->m_offset, bOffset);
  if (whence < PY_SEEK_SET || whence > PY_SEEK_END) {
    PyErr_SetString(PyExc_ValueError, "invalid whence");
    goto error;
  }

  _Cp_AssignCheck(self->m_whence, PyLong_FromLong(whence), error);
  self->s_keep_pos = keepPos;
  self->s_is_number = PyNumber_Check(self->m_offset);
  return 0;

error:
  return -1;
}

static PyObject*
cp_offsetatom_str(CpOffsetAtomObject* self)
{
  return PyUnicode_FromFormat("%R at %R", self->m_atom, self->m_offset);
}

static PyObject*
cp_offsetatom_repr(CpOffsetAtomObject* self)
{
  return PyUnicode_FromFormat(
    "<OffsetAt target=%R at=%R>", self->m_atom, self->m_offset);
}

static PyObject*
cp_offsetatom__offset_get(CpOffsetAtomObject* self)
{
  return Py_NewRef(self->m_offset);
}

static int
cp_offsetatom__offset_set(CpOffsetAtomObject* self,
                          PyObject* value,
                          void* closure)
{
  _Cp_SetObj(self->m_offset, value);
  self->s_is_number = PyNumber_Check(self->m_offset);
  return 0;
}

static PyObject*
cp_offsetatom_eval_offset(PyObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "context", NULL };
  PyObject* context = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &context)) {
    return NULL;
  }
  return CpOffsetAtom_EvalOffset(self, context);
}

_CpEndian_ImplSetByteorder(CpOffsetAtomObject, offsetatom, self->m_atom);

/*Public API*/

/*CpAPI*/
PyObject*
CpOffsetAtom_Size(PyObject* pAtom, PyObject* pContext)
{
  return CpAtom_Size(_Cp_CAST(CpOffsetAtomObject*, pAtom)->m_atom, pContext);
}

/*CpAPI*/
PyObject*
CpOffsetAtom_EvalOffset(PyObject* pAtom, PyObject* pContext)
{
  PyObject *nResult = NULL, *nOffset = NULL;
  CpOffsetAtomObject* self = _Cp_CAST(CpOffsetAtomObject*, pAtom);

  if (self->s_is_number) {
    nResult = Py_NewRef(self->m_offset);
    goto success;
  }

  _Cp_AssignCheck(nOffset, Cp_EvalObject(self->m_offset, pContext), error);
  if (!PyNumber_Check(nOffset)) {
    // try to convert it to a number
    _Cp_AssignCheck(
      nResult, CpObject_CreateOneArg(&PyLong_Type, nOffset), error);
  } else {
    nResult = Py_NewRef(nOffset);
  }
  goto success;

error:
  Py_CLEAR(nOffset);
  Py_CLEAR(nResult);

success:
  return nResult;
}

/*CpAPI*/
int
CpOffsetAtom_Pack(PyObject* pAtom, PyObject* pObj, PyObject* pContext)
{
  PyObject *nFallbackOffset = NULL, *nTmp = NULL, *nIO = NULL, *nTmpIO = NULL,
           *nOffset = NULL, *nRoot = NULL, *nOffsets = NULL, *nBuffer = NULL;
  int result = 0;
  CpOffsetAtomObject* self = _Cp_CAST(CpOffsetAtomObject*, pAtom);
  _modulestate* state = get_global_module_state();

  // first, query fallbck
  _Cp_AssignCheck(nFallbackOffset, CpContextIO_Tell(pContext), error);
  _Cp_AssignCheck(nOffset, CpOffsetAtom_EvalOffset(pAtom, pContext), error);
  _Cp_AssignCheck(
    nTmp, CpContextIO_Seek(pContext, nOffset, self->m_whence), error);
  Py_CLEAR(nTmp);

  _Cp_AssignCheck(nIO, CpContext_IO(pContext, state), error);
  _Cp_AssignCheck(nTmpIO, CpObject_CreateNoArgs(CpBytesIO_Type), error);

  if (CpContext_SETITEM(pContext, state->str__context_io, nTmpIO) < 0) {
    goto error;
  }

  // then pack
  if (CpAtom_Pack(self->m_atom, pObj, pContext) < 0) {
    goto error;
  }

  // finally, seek back
  _Cp_AssignCheck(
    nTmp, CpContextIO_Seek(pContext, nFallbackOffset, self->m_whence), error);
  Py_CLEAR(nTmp);

  _Cp_AssignCheck(nRoot, CpContext_GetRoot(pContext), error);
  _Cp_AssignCheck(
    nOffsets, CpContext_ITEM(nRoot, state->str__context_offsets), error);
  _Cp_AssignCheck(
    nBuffer, PyObject_CallMethodNoArgs(nTmpIO, state->str__io_getvalue), error);

  if (PyObject_SetItem(nOffsets, nOffset, nBuffer) < 0) {
    goto error;
  }
  if (CpContext_SETIO(pContext, state, nIO) < 0) {
    goto error;
  }
  goto success;

error:
  result = -1;

success:
  Py_XDECREF(nFallbackOffset);
  Py_XDECREF(nTmp);
  Py_XDECREF(nIO);
  Py_XDECREF(nTmpIO);
  Py_XDECREF(nOffset);
  Py_XDECREF(nRoot);
  Py_XDECREF(nOffsets);
  Py_XDECREF(nBuffer);
  return result;
}

/*CpAPI*/
PyObject*
CpOffsetAtom_Unpack(PyObject* pAtom, PyObject* pContext)
{
  PyObject *nResult = NULL, *nOffset = NULL, *nTmp = NULL,
           *nFallbackOffset = NULL;
  CpOffsetAtomObject* self = _Cp_CAST(CpOffsetAtomObject*, pAtom);

  _Cp_AssignCheck(nFallbackOffset, CpContextIO_Tell(pContext), error);
  _Cp_AssignCheck(nOffset, CpOffsetAtom_EvalOffset(pAtom, pContext), error);
  _Cp_AssignCheck(
    nTmp, CpContextIO_Seek(pContext, nOffset, self->m_whence), error);
  Py_CLEAR(nTmp);

  _Cp_AssignCheck(nResult, CpAtom_Unpack(self->m_atom, pContext), error);
  _Cp_AssignCheck(
    nTmp, CpContextIO_Seek(pContext, nFallbackOffset, self->m_whence), error);
  goto success;

error:
  Py_CLEAR(nResult);

success:
  Py_XDECREF(nTmp);
  Py_XDECREF(nOffset);
  Py_XDECREF(nFallbackOffset);
  return nResult;
}

/*CpAPI*/
PyObject*
CpOffsetAtom_TypeOf(PyObject* pAtom)
{
  return CpAtom_TypeOf(_Cp_CAST(CpOffsetAtomObject*, pAtom)->m_atom);
}

/*type*/
static PyMemberDef CpOffsetAtom_Members[] = {
  { "offset", T_OBJECT, offsetof(CpOffsetAtomObject, m_offset), 0 },
  { "whence", T_OBJECT, offsetof(CpOffsetAtomObject, m_whence), 0 },
  { "is_number", T_BOOL, offsetof(CpOffsetAtomObject, s_is_number), READONLY },
  { "keep_pos", T_BOOL, offsetof(CpOffsetAtomObject, s_keep_pos), 0 },
  { NULL }
};

static PyGetSetDef CpOffsetAtom_GetSet[] = {
  { "offset",
    (getter)cp_offsetatom__offset_get,
    (setter)cp_offsetatom__offset_set,
    NULL,
    NULL },
  { NULL },
};

static PyMethodDef CpOffsetAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(offsetatom, NULL),
  {
    "eval_offset",
    (PyCFunction)cp_offsetatom_eval_offset,
    METH_VARARGS | METH_KEYWORDS,
    NULL,
  },
  { NULL }
};

PyTypeObject CpOffsetAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpOffsetAtom_NAME),
  .tp_basicsize = sizeof(CpOffsetAtomObject),
  .tp_dealloc = (destructor)cp_offsetatom_dealloc,
  .tp_init = (initproc)cp_offsetatom_init,
  .tp_members = CpOffsetAtom_Members,
  .tp_methods = CpOffsetAtom_Methods,
  .tp_getset = CpOffsetAtom_GetSet,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_new = (newfunc)cp_offsetatom_new,
  .tp_str = (reprfunc)cp_offsetatom_str,
  .tp_repr = (reprfunc)cp_offsetatom_repr,
};

/*init*/
int
cp_offset__mod_types()
{
  CpOffsetAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpModule_SetupType(&CpOffsetAtom_Type, -1);
  return 0;
}

void
cp_offset__mod_clear(PyObject* m, _modulestate* state)
{
}

int
cp_offset__mod_init(PyObject* m, _modulestate* state)
{
  CpModule_AddObject(CpOffsetAtom_NAME, &CpOffsetAtom_Type, -1);
  return 0;
}