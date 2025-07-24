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
#ifndef CP_BUILTIN_CONDITIONAL_H
#define CP_BUILTIN_CONDITIONAL_H

#include "caterpillar/atoms/builtin/builtin.h"
#include "caterpillar/caterpillarapi.h"

//------------------------------------------------------------------------------
// Conditional
//------------------------------------------------------------------------------
struct _conditionalatomobj
{
  CpBuiltinAtom_HEAD;

  /// Stores a reference to the actual parsing struct that will be used
  /// to parse or build our data. This attribute is never null.
  PyObject* m_atom;

  /// A constant or dynamic value to represent the condition.
  PyObject* m_condition;
};

#define CpConditionalAtom_CheckExact(op)                                       \
  Py_IS_TYPE((op), &CpConditionalAtom_Type)
#define CpConditionalAtom_Check(op)                                            \
  PyObject_TypeCheck((op), &CpConditionalAtom_Type)

static inline PyObject*
CpConditionalAtom_GetAtom(PyObject* pObj)
{
  return Py_XNewRef(_Cp_CAST(CpConditionalAtomObject*, pObj)->m_atom);
}

static inline PyObject*
CpConditionalAtom_GetCondition(PyObject* pObj)
{
  return Py_XNewRef(_Cp_CAST(CpConditionalAtomObject*, pObj)->m_condition);
}

static inline PyObject*
CpConditionalAtom_New(PyObject* atom, PyObject* condition)
{
  return CpObject_Create(&CpConditionalAtom_Type, "OO", atom, condition);
}

static inline int
CpConditionalAtom_SetAtom(PyObject* pObj, PyObject* pAtom)
{
  CpConditionalAtomObject* self = _Cp_CAST(CpConditionalAtomObject*, pObj);
  if (!pAtom) {
    PyErr_SetString(PyExc_ValueError, "Atom cannot be null");
  }

  Py_XSETREF(self->m_atom, Py_NewRef(pAtom));
  return 0;
}

static inline int
CpConditionalAtom_SetCondition(PyObject* pObj, PyObject* pCondition)
{
  CpConditionalAtomObject* self = _Cp_CAST(CpConditionalAtomObject*, pObj);
  if (!pCondition) {
    PyErr_SetString(PyExc_ValueError, "Condition cannot be null");
  }

  Py_XSETREF(self->m_condition, Py_NewRef(pCondition));
  return 0;
}

#endif