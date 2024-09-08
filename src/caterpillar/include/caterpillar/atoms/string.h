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

#define CpStringAtom_NAME "string"
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
#define CpBytesAtom_NAME "octetstring"
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

#define CpPStringAtom_NAME "pstring"
#define CpPStringAtom_CheckExact(op) Py_IS_TYPE((op), &CpPStringAtom_Type)
#define CpPStringAtom_Check(op) PyObject_TypeCheck((op), &CpPStringAtom_Type)

static inline CpPStringAtomObject*
CpPStringAtom_New(PyObject* atom, PyObject* encoding)
{
  return (CpPStringAtomObject*)CpObject_Create(
    &CpPStringAtom_Type, "OO", atom, encoding);
}

#endif