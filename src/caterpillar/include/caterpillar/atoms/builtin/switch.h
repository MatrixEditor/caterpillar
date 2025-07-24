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
#ifndef CP_BUILTIN_SWITCH_H
#define CP_BUILTIN_SWITCH_H

#include "caterpillar/atoms/builtin/builtin.h"
#include "caterpillar/caterpillarapi.h"

//------------------------------------------------------------------------------
// Switch
//------------------------------------------------------------------------------
struct _switchatomobj
{
  CpBuiltinAtom_HEAD;

  /// Stores a reference to the actual parsing struct that will be used
  /// to parse or build our data. This attribute is never null.
  PyObject* m_atom;

  // A dictionary or dynamic value to represent the cases.
  PyObject* m_cases;

  // pre-computed state of the atom object
  int s_callable;
};

#define CpSwitchAtom_CheckExact(op) Py_IS_TYPE((op), &CpSwitchAtom_Type)
#define CpSwitchAtom_Check(op) PyObject_TypeCheck((op), &CpSwitchAtom_Type)

static inline PyObject*
CpSwitchAtom_New(PyObject* atom, PyObject* cases)
{
  return CpObject_Create(&CpSwitchAtom_Type, "OO", atom, cases);
}

static inline PyObject*
CpSwitchAtom_GetAtom(PyObject* pObj)
{
  return Py_XNewRef(_Cp_CAST(CpSwitchAtomObject*, pObj)->m_atom);
}

static inline PyObject*
CpSwitchAtom_GetCases(PyObject* pObj)
{
  return Py_XNewRef(_Cp_CAST(CpSwitchAtomObject*, pObj)->m_cases);
}

static inline int
CpSwitchAtom_IsContextLambda(PyObject* pObj)
{
  return _Cp_CAST(CpSwitchAtomObject*, pObj)->s_callable;
}

static inline int
CpSwitchAtom_SetCases(PyObject* pObj, PyObject* pCases)
{
  CpSwitchAtomObject* self = _Cp_CAST(CpSwitchAtomObject*, pObj);
  if (!pCases) {
    PyErr_SetString(PyExc_ValueError, "Cases cannot be null");
  }

  Py_XSETREF(self->m_cases, Py_NewRef(pCases));
  self->s_callable = PyCallable_Check(self->m_cases);
  return 0;
}

static inline int
CpSwitchAtom_SetAtom(PyObject* pObj, PyObject* pAtom)
{
  CpSwitchAtomObject* self = _Cp_CAST(CpSwitchAtomObject*, pObj);
  if (!pAtom) {
    PyErr_SetString(PyExc_ValueError, "Atom cannot be null");
  }

  Py_XSETREF(self->m_atom, Py_NewRef(pAtom));
  return 0;
}

#endif