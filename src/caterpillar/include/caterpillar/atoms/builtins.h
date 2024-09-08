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
#ifndef BUILTINS_H
#define BUILTINS_H

#include "caterpillar/caterpillarapi.h"
#include "caterpillar/atomobj.h"

// PROPOSAL: Builtin atoms are similar to the Python class FieldMixin
// but implement all parts of a field separately. For instance, the
// builtin atom for a sequence only implements the sequence part.
struct _builtinatomobj
{
    CpCAtom_HEAD
};

#define CpBuiltinAtom_NAME "builtinatom"
#define CpBuiltinAtom_CheckExact(op) Py_IS_TYPE((op), &CpBuiltinAtom_Type)
#define CpBuiltinAtom_Check(op) PyObject_IsType((op), &CpBuiltinAtom_Type)
#define CpBuiltinAtom_HEAD CpBuiltinAtomObject ob_base;
#define CpBuiltinAtom_CATOM(self) (self)->ob_base.ob_base

//------------------------------------------------------------------------------
// Repeated
struct _repeatedatomobj
{
    CpBuiltinAtom_HEAD

    /// Stores a reference to the actual parsing struct that will be used
    /// to parse or build our data. This attribute is never null.
    PyObject *m_atom;

    /// A constant or dynamic value to represent the amount of structs. Zero
    /// indicates there are no sequence types associated with this field.
    PyObject* m_length;
};

#define CpRepeatedAtom_NAME "repeated"
#define CpRepeatedAtom_CheckExact(op) Py_IS_TYPE((op), &CpRepeatedAtom_Type)
#define CpRepeatedAtom_Check(op) PyObject_IsType((op), &CpRepeatedAtom_Type)

inline CpRepeatedAtomObject *
CpRepeatedAtom_New(PyObject* atom, PyObject* length)
{
  return (CpRepeatedAtomObject*)CpObject_Create(&CpRepeatedAtom_Type, "OO", atom, length);
}

//------------------------------------------------------------------------------
// Conditional
struct _conditionatomobj
{
    CpBuiltinAtom_HEAD

    /// Stores a reference to the actual parsing struct that will be used
    /// to parse or build our data. This attribute is never null.
    PyObject *m_atom;

    /// A constant or dynamic value to represent the condition.
    PyObject *m_condition;
};

#define CpConditionAtom_NAME "condition"
#define CpConditionAtom_CheckExact(op) Py_IS_TYPE((op), &CpConditionAtom_Type)
#define CpConditionAtom_Check(op) PyObject_IsType((op), &CpConditionAtom_Type)

static inline CpConditionAtomObject *
CpConditionAtom_New(PyObject* atom, PyObject* condition)
{
  return (CpConditionAtomObject*)CpObject_Create(&CpConditionAtom_Type, "OO", condition, atom);
}

//------------------------------------------------------------------------------
// Switch
struct _switchatomobj
{
    CpBuiltinAtom_HEAD

    /// Stores a reference to the actual parsing struct that will be used
    /// to parse or build our data. This attribute is never null.
    PyObject *m_atom;

    // A dictionary or dynamic value to represent the cases.
    PyObject *m_cases;

    // -- internal ---
    int s_callable;
};

#define CpSwitchAtom_NAME "switch"
#define CpSwitchAtom_CheckExact(op) Py_IS_TYPE((op), &CpSwitchAtom_Type)
#define CpSwitchAtom_Check(op) PyObject_IsType((op), &CpSwitchAtom_Type)

static inline CpSwitchAtomObject *
CpSwitchAtom_New(PyObject* atom, PyObject* cases)
{
  return (CpSwitchAtomObject*)CpObject_Create(&CpSwitchAtom_Type, "OO", atom, cases);
}

#endif