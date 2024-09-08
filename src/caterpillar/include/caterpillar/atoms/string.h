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

struct _stringatomobj
{
  CpBuiltinAtom_HEAD

    PyObject* m_length;
  PyObject* m_errors;
  PyObject* m_encoding;
};

#define CpStringAtom_NAME "string"
#define CpStringAtom_CheckExact(op) Py_IS_TYPE((op), &CpStringAtom_Type)
#define CpStringAtom_Check(op) PyObject_TypeCheck((op), &CpStringAtom_Type)

// TODO: CString, PString

struct _bytesatomobj
{
  CpBuiltinAtom_HEAD

    PyObject* m_length;
    int s_callable;
};

#define CpBytesAtom_NAME "octetstring"
#define CpBytesAtom_CheckExact(op) Py_IS_TYPE((op), &CpBytesAtom_Type)
#define CpBytesAtom_Check(op) PyObject_TypeCheck((op), &CpBytesAtom_Type)

static inline CpBytesAtomObject*
CpBytesAtom_New(PyObject* length)
{
  return (CpBytesAtomObject*)CpObject_CreateOneArg(&CpBytesAtom_Type, length);
}

#endif