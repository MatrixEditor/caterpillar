/**
 * Copyright (C) MatrixEditor 2025
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
#ifndef CP_BUILTIN_REPEATED_H
#define CP_BUILTIN_REPEATED_H

#include "caterpillar/atoms/builtin/builtin.h"
#include "caterpillar/caterpillarapi.h"

struct _repeatedatomobj
{
  CpBuiltinAtom_HEAD;

  /// Stores a reference to the actual parsing struct that will be used
  /// to parse or build our data. This attribute is never null.
  PyObject* m_atom;

  /// A constant or dynamic value to represent the amount of structs. Zero
  /// indicates there are no sequence types associated with this field.
  PyObject* m_length;
};

#define CpRepeatedAtom_CheckExact(op) Py_IS_TYPE((op), &CpRepeatedAtom_Type)
#define CpRepeatedAtom_Check(op) PyObject_TypeCheck((op), &CpRepeatedAtom_Type)

static inline PyObject*
CpRepeatedAtom_New(PyObject* atom, PyObject* length)
{
  return CpObject_Create(&CpRepeatedAtom_Type, "OO", atom, length);
}

static inline PyObject*
CpRepeatedAtom_GetAtom(PyObject* pObj)
{
  return Py_XNewRef(_Cp_CAST(CpRepeatedAtomObject*, pObj)->m_atom);
}

static inline PyObject*
CpRepeatedAtom_GetLength(PyObject* pObj, PyObject* pContext)
{
  PyObject* nResult = NULL;
  CpRepeatedAtomObject* self = _Cp_CAST(CpRepeatedAtomObject*, pObj);
  if (PyCallable_Check(self->m_length) && pContext) {
    if ((nResult = PyObject_CallOneArg(self->m_length, pContext), !nResult))
      return NULL;
  } else {
    nResult = Py_NewRef(self->m_length);
  }
  return nResult;
}

static inline int
CpRepeatedAtom_SetAtom(PyObject* pObj, PyObject* pAtom)
{
  CpRepeatedAtomObject* self = _Cp_CAST(CpRepeatedAtomObject*, pObj);
  if (!pAtom) {
    PyErr_SetString(PyExc_ValueError, "Atom cannot be null");
  }

  Py_XSETREF(self->m_atom, Py_NewRef(pAtom));
  return 0;
}

static inline int
CpRepeatedAtom_SetLength(PyObject* pObj, PyObject* pLength)
{
  CpRepeatedAtomObject* self = _Cp_CAST(CpRepeatedAtomObject*, pObj);
  if (!pLength) {
    PyErr_SetString(PyExc_ValueError, "Length cannot be null");
  }

  Py_XSETREF(self->m_length, Py_NewRef(pLength));
  return 0;
}

#endif