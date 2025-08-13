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
#ifndef CP_BUILTIN_H
#define CP_BUILTIN_H

#include "caterpillar/caterpillarapi.h"
#include "caterpillar/atom.h"

// Builtin atoms are similar to the Python class FieldMixin but implement
// all parts of a field separately. For instance, the builtin atom for a
// sequence only implements the sequence part.
struct _builtinatomobj
{
  // this class does not implement any struct-like methods but implements
  // special operators used by caterpillar.
  CpAtom_HEAD;
};

#define CpBuiltinAtom_CheckExact(op) Py_IS_TYPE((op), &CpBuiltinAtom_Type)
#define CpBuiltinAtom_Check(op) PyObject_TypeCheck((op), &CpBuiltinAtom_Type)
#define CpBuiltinAtom_HEAD CpBuiltinAtomObject ob_base
#define CpBuiltinAtom_ATOM(self) (self)->ob_base.ob_base

static inline PyObject *
CpBuiltinAtom_New(void)
{
  return CpObject_CreateNoArgs(&CpBuiltinAtom_Type);
}

#endif