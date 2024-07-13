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

#include "caterpillar/caterpillar.h"
#include "caterpillar/field.h"

/// @struct _boolatomobj
/// @brief Struct representing a bool atom object.
///
/// This struct defines a bool atom object which is part of the CpFieldCAtom
/// family.
struct _boolatomobj
{
  CpFieldCAtom_HEAD
};

/// @brief Bool atom object type
///
/// This variable defines the type object for bool atom objects, allowing
/// them to be used across the library.
PyAPI_DATA(PyTypeObject) CpBoolAtom_Type;

/**
 * @brief Checks if the given object is a bool atom object.
 *
 * This macro verifies if the provided object is exactly of the bool
 * atom type.
 *
 * @param op The object to check.
 * @return True if the object is exactly of type CpBoolAtom_Type,
 *         false otherwise.
 */
#define CpBoolAtom_CheckExact(op) Py_IS_TYPE((op), &CpBoolAtom_Type)

/**
 * @brief Checks if the given object is a bool atom object.
 *
 * This macro checks if the provided object is of the bool atom type or
 * a subtype thereof.
 *
 * @param op The object to check.
 * @return True if the object is of type CpBoolAtom_Type or a subtype,
 *         false otherwise.
 */
#define CpBoolAtom_Check(op) (PyObject_TypeCheck((op), &CpBoolAtom_Type))

/**
 * @brief Packs a value into the underlying stream.
 *
 * @param self The bool atom object
 * @param value The boolean value to be packed.
 * @param layer The layer object providing the context for packing.
 * @return Integer status code (typically 0 for success, non-zero for error).
 */
PyAPI_FUNC(int) CpBoolAtom_Pack(CpBoolAtomObject* self,
                                PyObject* value,
                                CpLayerObject* layer);

/**
 * @brief Unpacks a value from the underlying stream.
 *
 * @param self The bool atom object instance.
 * @param layer The layer object providing the context for unpacking.
 * @return The unpacked boolean value as a PyObject.
 */
PyAPI_FUNC(PyObject*)
  CpBoolAtom_Unpack(CpBoolAtomObject* self, CpLayerObject* layer);

//------------------------------------------------------------------------------
// Char Atom
struct _charatomobj
{
  CpFieldCAtom_HEAD
};

/// Char atom object type
// PyAPI_DATA(PyTypeObject) CpCharAtom_Type;

/** @brief Checks if the given object is a char atom object */
#define CpCharAtom_CheckExact(op) Py_IS_TYPE((op), &CpCharAtom_Type)
/** @brief Checks if the given object is a char atom object */
#define CpCharAtom_Check(op) (PyObject_TypeCheck((op), &CpCharAtom_Type))

PyAPI_FUNC(int) CpCharAtom_Pack(CpCharAtomObject* self,
                                PyObject* value,
                                CpLayerObject* layer);

PyAPI_FUNC(PyObject*)
  CpCharAtom_Unpack(CpCharAtomObject* self, CpLayerObject* layer);

//------------------------------------------------------------------------------
// Padding
struct _paddingatomobj
{
  CpFieldCAtom_HEAD

    char padding;
};

/// Padding atom object type
// PyAPI_DATA(PyTypeObject) CpPaddingAtom_Type;

/** @brief Checks if the given object is a padding atom object */
#define CpPaddingAtom_CheckExact(op) Py_IS_TYPE((op), &CpPaddingAtom_Type)
/** @brief Checks if the given object is a padding atom object */
#define CpPaddingAtom_Check(op) (PyObject_TypeCheck((op), &CpPaddingAtom_Type))

PyAPI_FUNC(int) CpPaddingAtom_Pack(CpPaddingAtomObject* self,
                                   PyObject* _,
                                   CpLayerObject* layer);

PyAPI_FUNC(int) CpPaddingAtom_PackMany(CpPaddingAtomObject* self,
                                       PyObject* _,
                                       CpLayerObject* layer);

PyAPI_FUNC(PyObject*)
  CpPaddingAtom_Unpack(CpPaddingAtomObject* self, CpLayerObject* layer);

PyAPI_FUNC(PyObject*)
  CpPaddingAtom_UnpackMany(CpPaddingAtomObject* self, CpLayerObject* layer);

#endif