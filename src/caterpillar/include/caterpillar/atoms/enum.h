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
#ifndef ENUMATOMOBJ_H
#define ENUMATOMOBJ_H

#include "caterpillar/atoms/builtins.h"

struct _enumatomobj
{
  CpBuiltinAtom_HEAD

    /// Stores the mapping of the underlying enum type.
    PyObject* m_members;

  PyObject* m_value2member_map;
  PyObject* m_default;

  /// Reference to the atom that is responsible for
  /// parsing the enum value
  PyObject* m_atom;

  /// Reference to the enum type
  PyObject* m_enum_type;
};

#define CpEnumAtom_CheckExact(op) Py_IS_TYPE((op), &CpEnumAtom_Type)
#define CpEnumAtom_Check(op) (PyObject_TypeCheck((op), &CpEnumAtom_Type))

static inline CpEnumAtomObject*
CpEnumAtom_New(PyObject* members, PyObject* atom)
{
  return (CpEnumAtomObject*)CpObject_Create(
    &CpEnumAtom_Type, "OO", members, atom);
}

#endif