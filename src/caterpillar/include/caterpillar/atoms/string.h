/**
 * Copyright (C) MatrixEditor 2024
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
#ifndef STRINGATOMOBJ_H
#define STRINGATOMOBJ_H

#include "caterpillar/atoms/builtins.h"
#include "caterpillar/parsing.h"

#if PY_3_13_PLUS
// Python3.13 comes with a new API
#define CpCompat_PyUnicode_Strip(obj, chars)                                   \
  PyObject_CallMethod((obj), "strip", "O", (chars))

#else

#define CpCompat_PyUnicode_Strip(obj, chars)                                   \
  _PyUnicode_XStrip((obj), 1, (chars))

#endif

// ---------------------------------------------------------------------------
// Default String
struct _stringatomobj
{
  CpBuiltinAtom_HEAD

    /// The length of this string. It can be a constant integer
    /// object or a ContextLambda.
    PyObject* m_length;

  /// Whether this string should ignore errors when parsing
  PyObject* m_errors;

  /// The encoding of this string
  PyObject* m_encoding;
};

#define CpStringAtom_CheckExact(op) Py_IS_TYPE((op), &CpStringAtom_Type)
#define CpStringAtom_Check(op) PyObject_TypeCheck((op), &CpStringAtom_Type)

// TODO: CString, PString

// ---------------------------------------------------------------------------
// Bytes
struct _bytesatomobj
{
  CpBuiltinAtom_HEAD

    /// The length of this string. It can be a constant integer
    /// object or a ContextLambda.
    PyObject* m_length;

  // -- internal ---
  int s_callable;
};

// REVISIT: The name of this atom should be something similar to 'bytes'
#define CpBytesAtom_CheckExact(op) Py_IS_TYPE((op), &CpBytesAtom_Type)
#define CpBytesAtom_Check(op) PyObject_TypeCheck((op), &CpBytesAtom_Type)

static inline CpBytesAtomObject*
CpBytesAtom_New(PyObject* length)
{
  return (CpBytesAtomObject*)CpObject_CreateOneArg(&CpBytesAtom_Type, length);
}

// ---------------------------------------------------------------------------
// PString

struct _pstringatomobj
{
  CpBuiltinAtom_HEAD

    /// The atom that parses the length of this string
    PyObject* m_atom;

  /// Whether this string should ignore errors when parsing
  PyObject* m_errors;

  /// The encoding of this string
  PyObject* m_encoding;
};

#define CpPStringAtom_CheckExact(op) Py_IS_TYPE((op), &CpPStringAtom_Type)
#define CpPStringAtom_Check(op) PyObject_TypeCheck((op), &CpPStringAtom_Type)

static inline CpPStringAtomObject*
CpPStringAtom_New(PyObject* atom, PyObject* encoding)
{
  return (CpPStringAtomObject*)CpObject_Create(
    &CpPStringAtom_Type, "OO", atom, encoding);
}

// ---------------------------------------------------------------------------
// CString

struct _cstringatomobj
{
  CpBuiltinAtom_HEAD

    PyObject* m_length;
  PyObject* m_encoding;
  PyObject* m_errors;
  PyObject* m_terminator;
  PyObject* _m_terminator_bytes;

  int s_callable;
  int s_number;
  int s_keep_terminator;
  int s_greedy;
};

#define CpCStringAtom_CheckExact(op) Py_IS_TYPE((op), &CpCStringAtom_Type)
#define CpCStringAtom_Check(op) PyObject_TypeCheck((op), &CpCStringAtom_Type)

static inline CpCStringAtomObject*
CpCStringAtom_New(PyObject* length,
                  PyObject* encoding,
                  PyObject* errors,
                  PyObject* terminator)
{
  return (CpCStringAtomObject*)CpObject_Create(
    &CpCStringAtom_Type, "OOOO", length, encoding, errors, terminator);
}

static inline PyObject*
CpCStringAtom_Length(CpCStringAtomObject* self, CpLayerObject* layer)
{
  if (self->s_number) {
    return Py_NewRef(self->m_length);
  }
  if (self->s_greedy) {
    Py_RETURN_NONE;
  }
  if (self->s_callable) {
    return PyObject_CallOneArg(self->m_length, (PyObject*)layer);
  }
  return _Cp_Unpack(self->m_length, layer);
}

#endif