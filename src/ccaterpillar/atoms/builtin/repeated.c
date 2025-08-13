#include "../../private.h"
#include "caterpillar/caterpillar.h"

#include <structmember.h>

static PyObject*
cp_repeatedatom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpRepeatedAtomObject* self;
  if ((self = (CpRepeatedAtomObject*)type->tp_alloc(type, 0), !self)) {
    return NULL;
  }

  CpBuiltinAtom_ATOM(self).ob_bits = CpRepeatedAtom_Bits;
  CpBuiltinAtom_ATOM(self).ob_pack = CpRepeatedAtom_Pack;
  CpBuiltinAtom_ATOM(self).ob_pack_many = NULL;
  CpBuiltinAtom_ATOM(self).ob_unpack = CpRepeatedAtom_Unpack;
  CpBuiltinAtom_ATOM(self).ob_unpack_many = NULL;
  CpBuiltinAtom_ATOM(self).ob_type = CpRepeatedAtom_TypeOf;
  CpBuiltinAtom_ATOM(self).ob_size = CpRepeatedAtom_Size;
  return _Cp_CAST(PyObject*, self);
}

static void
cp_repeatedatom_dealloc(CpRepeatedAtomObject* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_repeatedatom_init(CpRepeatedAtomObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "atom", "length", NULL };
  PyObject *atom = NULL, *length = NULL;

  if (!PyArg_ParseTupleAndKeywords(args, kw, "OO", kwlist, &atom, &length)) {
    return -1;
  }
  _Cp_SetObj(self->m_atom, atom);
  _Cp_SetObj(self->m_length, length);

  return 0;
}

static PyObject*
cp_repeatedatom__repr__(CpRepeatedAtomObject* self)
{
  return PyUnicode_FromFormat("%R[%R]", self->m_atom, self->m_length);
}

_CpEndian_ImplSetByteorder(CpRepeatedAtomObject, repeatedatom, self->m_atom);

/* Private API */
static int
_CpPack_EvalLength(PyObject* pContext,
                   PyObject* pLength,
                   Py_ssize_t pSize,
                   int* pGreedy,
                   Py_ssize_t* pEvaluatedLength)
{
  PyObject *nStart = NULL, *nSizeObj = NULL;
  int result = 0;
  _modulestate* state = get_global_module_state();

  if (Py_Is(pLength, &_Py_EllipsisObject)) {
    // greedy
    *pGreedy = true;
    *pEvaluatedLength = pSize;
    goto success;
  }

  if (PySlice_Check(pLength)) {
    // prefixed length
    *pGreedy = false;
    nStart = PyObject_GetAttr(pLength, state->str__start);
    if (!nStart) {
      goto error;
    }

    if (Py_IsNone(nStart)) {
      PyErr_SetString(
        PyExc_ValueError,
        "Prefixed length is not supported for this atom! (start=None)");
      goto error;
    }

    nSizeObj = PyLong_FromSsize_t(pSize);
    if (!nSizeObj) {
      goto error;
    }

    result = CpAtom_Pack(nStart, nSizeObj, pContext);
    if (result < 0) {
      goto error;
    }
    *pEvaluatedLength = pSize;
    goto success;
  }

  if (PyLong_Check(pLength)) {
    *pGreedy = false;
    *pEvaluatedLength = PyLong_AsSsize_t(pLength);
    if (*pEvaluatedLength < 0) {
      PyErr_Clear();
      PyErr_SetString(PyExc_ValueError,
                      "Negative length is not supported for this atom!");
      goto error;
    }

    if (*pEvaluatedLength != pSize) {
      PyErr_Format(PyExc_ValueError,
                   "given length %d does not match sequence size %d",
                   *pEvaluatedLength,
                   pSize);
      goto error;
    }
    goto success;
  }

  PyErr_SetString(PyExc_ValueError,
                  "length is not an integer or slice nor is greedy!");

error:
  result = -1;

success:
  Py_XDECREF(nStart);
  Py_XDECREF(nSizeObj);
  return result;
}

static int
_CpUnpack_EvalLength(PyObject* pContext,
                     PyObject* pSeqLength,
                     int* pGreedy,
                     Py_ssize_t* pEvaluatedLength)
{
  PyObject *nStart = NULL, *nSizeObj = NULL;
  int result = 0;
  _modulestate* state = get_global_module_state();

  *pEvaluatedLength = 0;
  *pGreedy = false;
  // 1. Case: greedy length
  //    We have to set the context variables accordingly.
  if (Py_IS_TYPE(pSeqLength, &PyEllipsis_Type)) {
    *pGreedy = true;
    *pEvaluatedLength = -1;
    goto success;
  }

  // 2. Case: length is a slice (prefixed type)
  //    As this is a special type, we have to first parse the length
  //    using the given start atom.
  if (PySlice_Check(pSeqLength)) {
    *pGreedy = false;
    if ((nStart = PyObject_GetAttr(pSeqLength, state->str__start), !nStart)) {
      goto error;
    }

    if (Py_IsNone(nStart)) {
      PyErr_SetString(PyExc_ValueError,
                      "Prefixed length is not supported for this atom!");
      goto error;
    }

    // revisit: set is_seq to false
    CpContext_SETITEM(pContext, state->str__context_is_seq, Py_False);
    nSizeObj = CpAtom_Unpack(nStart, pContext);
    CpContext_SETITEM(pContext, state->str__context_is_seq, Py_True);
    if (!nSizeObj) {
      goto error;
    }

    *pEvaluatedLength = PyLong_AsSsize_t(nSizeObj);
    if (*pEvaluatedLength < 0) {
      PyErr_Clear();
      PyErr_SetString(PyExc_ValueError,
                      "Negative length is not supported for this atom!");
      goto error;
    }

    goto success;
  }

  if (PyLong_Check(pSeqLength)) {
    *pGreedy = false;
    *pEvaluatedLength = PyLong_AsSsize_t(pSeqLength);
    if (*pEvaluatedLength < 0) {
      PyErr_Clear();
      PyErr_SetString(PyExc_ValueError,
                      "Negative length is not supported for this atom!");
      goto error;
    }
    goto success;
  }

  PyErr_SetString(PyExc_ValueError,
                  "length is not an integer or slice nor is greedy!");

error:
  result = -1;

success:
  Py_XDECREF(nStart);
  Py_XDECREF(nSizeObj);
  return result;
}

/* Public API */

/*CpAPI*/
PyObject*
CpRepeatedAtom_TypeOf(PyObject* pAtom)
{
  PyObject *nResult = NULL, *nAtomType = NULL;

  _Cp_AssignCheck(nAtomType,
                  CpAtom_TypeOf(_Cp_CAST(CpRepeatedAtomObject*, pAtom)->m_atom),
                  error);

  _Cp_AssignCheck(
    nResult, PyObject_GetItem((PyObject*)&PyList_Type, nAtomType), error);

  goto success;

error:
  nResult = NULL;

success:
  Py_XDECREF(nAtomType);
  return nResult;
}

/*CpAPI*/
PyObject*
CpRepeatedAtom_Bits(PyObject* pAtom)
{
  PyObject *nResult = NULL, *nLength = NULL, *nAtomBits = NULL,
           *nBitsSize = PyLong_FromLong(8);
  if (!nBitsSize) {
    goto error;
  }
  _Cp_AssignCheck(nLength, CpRepeatedAtom_GetLength(pAtom, NULL), error);
  if (!PyNumber_Check(nLength)) {
    PyErr_SetString(PyExc_ValueError, "length is not a number!");
    goto error;
  }

  _Cp_AssignCheck(nAtomBits,
                  CpAtom_BitsOf(_Cp_CAST(CpRepeatedAtomObject*, pAtom)->m_atom),
                  error);
  _Cp_AssignCheck(nResult, PyNumber_Multiply(nLength, nAtomBits), error);
  Py_XSETREF(nResult, PyNumber_Multiply(nResult, nBitsSize));
  if (!nResult) {
    goto error;
  }
  goto success;

error:
  Py_XSETREF(nResult, NULL);

success:
  Py_XDECREF(nLength);
  Py_XDECREF(nAtomBits);
  Py_XDECREF(nBitsSize);
  return nResult;
}

/*CpAPI*/
PyObject*
CpRepeatedAtom_Size(PyObject* pAtom, PyObject* pContext)
{
  PyObject *nLength = NULL, *nAtomSize = NULL, *nResult = NULL;
  _Cp_AssignCheck(nLength, CpRepeatedAtom_GetLength(pAtom, pContext), error);
  _Cp_AssignCheck(
    nAtomSize,
    CpAtom_Size(_Cp_CAST(CpRepeatedAtomObject*, pAtom)->m_atom, pContext),
    error);

  if (!PyNumber_Check(nAtomSize)) {
    PyErr_SetString(PyExc_ValueError, "atom size is not a number!");
    goto error;
  }
  if (!PyNumber_Check(nLength)) {
    PyErr_SetString(PyExc_ValueError, "length is not a constant!");
    goto error;
  }

  if ((nResult = PyNumber_Multiply(nLength, nAtomSize), !nResult)) {
    goto error;
  }
  goto success;

error:
  Py_XSETREF(nResult, NULL);

success:
  Py_XDECREF(nLength);
  Py_XDECREF(nAtomSize);
  return nResult;
}

/*CpAPI*/
int
CpRepeatedAtom_Pack(PyObject* pAtom, PyObject* pObj, PyObject* pContext)
{
  PyObject *nLengthInfo = NULL, *nLength = NULL, *nTmpObj = NULL,
           *nResult = NULL, *nRaisedException = NULL, *nSeqContext = NULL,
           *nBasePath = NULL, *nTmpPath = NULL, *nTmpIndex = NULL;
  Py_ssize_t seqLength = 0, index = 0;
  bool hasPackMany = false, isSeq = false;
  int result = 0;
  _modulestate* state = get_global_module_state();
  CpRepeatedAtomObject* self = _Cp_CAST(CpRepeatedAtomObject*, pAtom);

  hasPackMany = CpAtom_HasPackMany(self->m_atom);
  isSeq = PySequence_Check(pObj);

  // first, get the length of the input sequence
  if (isSeq) {
    if ((seqLength = PySequence_Length(pObj)) < 0) {
      goto error;
    }
  } else {
    PyErr_Format(PyExc_ValueError, "input object (%R) is not a sequence", pObj);
    goto error;
  }
  _Cp_AssignCheck(nLength, CpRepeatedAtom_GetLength(pAtom, pContext), error);

  if ((nLengthInfo = CpLengthInfo_New(seqLength, hasPackMany), !nLengthInfo)) {
    goto error;
  }

  if (_CpPack_EvalLength(
        pContext,
        nLength,
        seqLength,
        &_Cp_CAST(CpLengthInfoObject*, nLengthInfo)->m_greedy,
        &_Cp_CAST(CpLengthInfoObject*, nLengthInfo)->m_length) < 0) {
    goto error;
  }
  if (hasPackMany) {
    // class explicitly defines __pack_many__ -> use it
    result = CpAtom_PackMany(self->m_atom, pObj, pContext, nLengthInfo);
    if (result < 0 &&
        (nRaisedException = PyErr_GetRaisedException(),
         nRaisedException && PyErr_GivenExceptionMatches(
                               nRaisedException, PyExc_NotImplementedError))) {
      // Make sure this method continues to pack the given object
      PyErr_Clear();
    } else {
      if (result < 0 && nRaisedException) {
        // This call steals a reference to exc, which must be a valid exception.
        PyErr_SetRaisedException(nRaisedException);
        nRaisedException = NULL;
      }
      goto success;
    }
  }

  if (CpLengthInfo_IsGreedy(nLengthInfo)) {
    if (CpLengthInfo_SetLength(nLengthInfo, seqLength) < 0) {
      goto error;
    }
  } else {
    if (CpLengthInfo_Length(nLengthInfo) != seqLength) {
      PyErr_Format(PyExc_ValueError,
                   "given length %d does not match sequence size %d",
                   CpLengthInfo_Length(nLengthInfo),
                   seqLength);
      goto error;
    }
  }

  // create context compatible to Python implementation
  _Cp_AssignCheck(nSeqContext, CpContext_New(), error);
  // _root
  _Cp_AssignCheck(nTmpObj, CpContext_GetRoot(pContext), error);
  if (CpContext_SETITEM(nSeqContext, state->str__context_root, nTmpObj) < 0)
    goto error;

  // _parent
  if (CpContext_SETITEM(
        nSeqContext, state->str__context_parent, Py_NewRef(pContext)) < 0)
    goto error;

  // _io
  if (CpContext_COPYITEM(nSeqContext, pContext, state->str__context_io) < 0) {
    goto error;
  }

  // _length
  if (CpContext_SETITEM(nSeqContext,
                        state->str__context_length,
                        CpLengthInfo_LengthAsLong(nLengthInfo)) < 0)
    goto error;

  // _field
  if (CpContext_COPYITEM(nSeqContext, pContext, state->str__context_field) < 0)
    PyErr_Clear();

  // _is_seq
  CpContext_SETITEM(nSeqContext, state->str__context_is_seq, Py_False);

  // main loop
  if ((nBasePath = CpContext_ITEM(pContext, state->str__context_path),
       !nBasePath)) {
    goto error;
  }

  for (index = 0; index < CpLengthInfo_Length(nLengthInfo); ++index) {
    Py_XSETREF(nTmpObj, PySequence_ITEM(pObj, index));
    if (!nTmpObj) {
      goto error;
    }

    Py_XSETREF(nTmpPath, PyUnicode_FromFormat("%S.%d", nBasePath, index));
    if (!nTmpPath) {
      goto error;
    }

    Py_XSETREF(nTmpIndex, PyLong_FromSsize_t(index));
    if (!nTmpIndex) {
      goto error;
    }

    CpContext_SETITEM(nSeqContext, state->str__context_index, nTmpIndex);
    CpContext_SETITEM(nSeqContext, state->str__context_path, nTmpPath);
    CpContext_SETITEM(nSeqContext, state->str__context_obj, nTmpObj);
    if (CpAtom_Pack(self->m_atom, nTmpObj, nSeqContext) < 0) {
      if (nRaisedException = PyErr_GetRaisedException(),
          nRaisedException &&
            PyErr_GivenExceptionMatches(nRaisedException, CpExc_Stop)) {
        // Make sure this method continues to pack the given object
        PyErr_Clear();
        break;
      } else {
        if (nRaisedException) {
          // This call steals a reference to exc, which must be a valid
          // exception.
          PyErr_SetRaisedException(nRaisedException);
          nRaisedException = NULL;
        }
        goto error;
      }
    }
  }

  goto success;

error:
  result = -1;

success:
  Py_XDECREF(nLengthInfo);
  Py_XDECREF(nLength);
  Py_XDECREF(nTmpObj);
  Py_XDECREF(nResult);
  Py_XDECREF(nRaisedException);
  Py_XDECREF(nSeqContext);
  Py_XDECREF(nTmpIndex);
  Py_XDECREF(nTmpPath);
  Py_XDECREF(nBasePath);
  return result;
}

/*CpAPI*/
PyObject*
CpRepeatedAtom_Unpack(PyObject* pAtom, PyObject* pContext)
{
  PyObject *nResult = NULL, *nTmpObj = NULL, *nSeqContext = NULL,
           *nRaisedException = NULL, *nBasePath = NULL, *nTmpPath = NULL,
           *nLength = NULL, *nLengthInfo = NULL, *nSeq = NULL,
           *nTmpIndex = NULL;
  _modulestate* state = get_global_module_state();
  Py_ssize_t index = 0;
  bool hasUnpackMany = false;
  CpRepeatedAtomObject* self = _Cp_CAST(CpRepeatedAtomObject*, pAtom);

  hasUnpackMany = CpAtom_HasPackMany(self->m_atom);
  _Cp_AssignCheck(nLength, CpRepeatedAtom_GetLength(pAtom, pContext), error);
  _Cp_AssignCheck(nLengthInfo, CpLengthInfo_New(0, false), error);
  if (_CpUnpack_EvalLength(
        pContext,
        nLength,
        &_Cp_CAST(CpLengthInfoObject*, nLengthInfo)->m_greedy,
        &_Cp_CAST(CpLengthInfoObject*, nLengthInfo)->m_length) < 0) {
    goto error;
  }

  if (hasUnpackMany) {
    nTmpObj = CpAtom_UnpackMany(self->m_atom, pContext, nLengthInfo);
    if (!nTmpObj &&
        (nRaisedException = PyErr_GetRaisedException(),
         nRaisedException && PyErr_GivenExceptionMatches(
                               nRaisedException, PyExc_NotImplementedError))) {
      PyErr_Clear();
    } else {
      if (nRaisedException) {
        // This call steals a reference to exc, which must be a valid
        // exception.
        PyErr_SetRaisedException(nRaisedException);
        nRaisedException = NULL;
      }
      goto success;
    }
  }
  _Cp_AssignCheck(nSeqContext, CpContext_New(), error);
  _Cp_AssignCheck(nSeq, PyList_New(0), error);
  Py_XSETREF(nTmpObj, NULL);
  Py_XSETREF(nResult, Py_NewRef(nSeq));

  // base path
  _Cp_AssignCheck(
    nBasePath, CpContext_ITEM(pContext, state->str__context_path), error);

  // _root
  CpContext_SETITEM(
    nSeqContext, state->str__context_root, CpContext_GetRoot(pContext));
  // _parent
  CpContext_SETITEM(nSeqContext, state->str__context_parent, pContext);
  // _length
  CpContext_SETITEM(nSeqContext, state->str__context_length, nLength);
  // _obj
  CpContext_COPYITEM(nSeqContext, pContext, state->str__context_obj);
  // _is_seq
  CpContext_SETITEM(nSeqContext, state->str__context_is_seq, Py_False);
  // _field
  if (CpContext_COPYITEM(nSeqContext, pContext, state->str__context_field) <
      0) {
    // optional
    PyErr_Clear();
  }
  // _io
  CpContext_COPYITEM(nSeqContext, pContext, state->str__context_io);
  // _lst
  CpContext_SETITEM(nSeqContext, state->str__context_list, nSeq);

  while (CpLengthInfo_IsGreedy(nLengthInfo) ||
         index < CpLengthInfo_Length(nLengthInfo)) {

    // set new path and index
    Py_XSETREF(nTmpPath, PyUnicode_FromFormat("%S.%d", nBasePath, index));
    Py_XSETREF(nTmpIndex, PyLong_FromSsize_t(index));
    if (!nTmpPath || !nTmpIndex) {
      goto error;
    }

    CpContext_SETITEM(nSeqContext, state->str__context_path, nTmpPath);
    CpContext_SETITEM(nSeqContext, state->str__context_index, nTmpIndex);
    Py_XSETREF(nTmpObj, CpAtom_Unpack(self->m_atom, nSeqContext));
    if (!nTmpObj &&
        (nRaisedException = PyErr_GetRaisedException(),
         nRaisedException &&
           (PyErr_GivenExceptionMatches(nRaisedException, CpExc_Stop) ||
            CpLengthInfo_IsGreedy(nLengthInfo)))) {
      // Make sure this method continues to pack the given object
      PyErr_Clear();
      break;
    } else {
      if (nRaisedException) {
        // This call steals a reference to exc, which must be a valid
        // exception.
        PyErr_SetRaisedException(nRaisedException);
        nRaisedException = NULL;
      }
      if (!nTmpObj)
        goto error;
    }

    if (PyList_Append(nSeq, nTmpObj) < 0) {
      goto error;
    }
    ++index;
  }

  // REVISIT: array factory
  goto success;

error:
  Py_XSETREF(nResult, NULL);

success:
  Py_XDECREF(nLength);
  Py_XDECREF(nLengthInfo);
  Py_XDECREF(nSeqContext);
  Py_XDECREF(nBasePath);
  Py_XDECREF(nTmpPath);
  Py_XDECREF(nTmpIndex);
  Py_XDECREF(nTmpObj);
  Py_XDECREF(nRaisedException);
  // Py_XDECREF(nSeq); // new ref is stored in nResult
  return nResult;
}

/* type */
static PyMemberDef CpRepeatedAtom_Members[] = {
  { "length", T_OBJECT, offsetof(CpRepeatedAtomObject, m_length), READONLY },
  { "atom", T_OBJECT, offsetof(CpRepeatedAtomObject, m_atom), READONLY },
  { NULL }
};

static PyMethodDef CpRepeatedAtom_Methods[] = {
  _CpEndian_ImplSetByteorder_MethDef(repeatedatom, NULL),
  {
    NULL,
  }
};

PyTypeObject CpRepeatedAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpRepeatedAtom_NAME),
  .tp_basicsize = sizeof(CpRepeatedAtomObject),
  .tp_dealloc = (destructor)cp_repeatedatom_dealloc,
  .tp_repr = (reprfunc)cp_repeatedatom__repr__,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_doc = NULL,
  .tp_new = (newfunc)cp_repeatedatom_new,
  .tp_init = (initproc)cp_repeatedatom_init,
  .tp_members = CpRepeatedAtom_Members,
  .tp_methods = CpRepeatedAtom_Methods,
};

/* init */
int
cp_repeated__mod_init(PyObject* m, _modulestate* state)
{
  CpModule_AddObject(CpRepeatedAtom_NAME, &CpRepeatedAtom_Type, -1);
  _CACHED_STRING(state, str__start, "start", -1);
  return 0;
}

int
cp_repeated__mod_types()
{
  CpRepeatedAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpModule_SetupType(&CpRepeatedAtom_Type, -1);
  return 0;
}

void
cp_repeated__mod_clear(PyObject* m, _modulestate* state)
{
  Py_CLEAR(state->str__start);
}
