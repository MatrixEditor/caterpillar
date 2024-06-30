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
#ifndef PRIMITIVEATOMOBJ_H
#define PRIMITIVEATOMOBJ_H

#include "caterpillar/field.h"
#include "caterpillar/macros.h"
#include "caterpillar/state.h"

typedef struct _boolatomobj
{
  CpFieldCAtom_HEAD
} CpBoolAtomObject;

/// Bool atom object type
PyAPI_DATA(PyTypeObject) CpBoolAtom_Type;

/** @brief Checks if the given object is a bool atom object */
#define CpBoolAtom_CheckExact(op) Py_IS_TYPE((op), &CpBoolAtom_Type)
/** @brief Checks if the given object is a bool atom object */
#define CpBoolAtom_Check(op) (PyObject_TypeCheck((op), &CpBoolAtom_Type))

PyAPI_FUNC(int)
  CpBoolAtom_Pack(CpBoolAtomObject* self, PyObject* value, CpLayerObject* layer);

PyAPI_FUNC(PyObject*)
  CpBoolAtom_Unpack(CpBoolAtomObject* self, CpLayerObject* layer);


//------------------------------------------------------------------------------
// Char Atom
typedef struct _charatomobj
{
  CpFieldCAtom_HEAD
} CpCharAtomObject;

/// Char atom object type
PyAPI_DATA(PyTypeObject) CpCharAtom_Type;

/** @brief Checks if the given object is a char atom object */
#define CpCharAtom_CheckExact(op) Py_IS_TYPE((op), &CpCharAtom_Type)
/** @brief Checks if the given object is a char atom object */
#define CpCharAtom_Check(op) (PyObject_TypeCheck((op), &CpCharAtom_Type))

PyAPI_FUNC(int)
  CpCharAtom_Pack(CpCharAtomObject* self, PyObject* value, CpLayerObject* layer);

PyAPI_FUNC(int)
  CpCharAtom_PackMany(CpCharAtomObject* self, PyObject* value, CpLayerObject* layer);

PyAPI_FUNC(PyObject*)
  CpCharAtom_Unpack(CpCharAtomObject* self, CpLayerObject* layer);

PyAPI_FUNC(PyObject *)
  CpCharAtom_UnpackMany(CpCharAtomObject *self, CpLayerObject *layer);

#endif