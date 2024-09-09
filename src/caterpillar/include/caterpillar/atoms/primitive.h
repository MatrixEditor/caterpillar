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

#include "caterpillar/atoms/builtins.h"


//------------------------------------------------------------------------------
// primitive atom
struct _primitiveatomobj {
  CpAtom_HEAD
};

#define CpPrimitiveAtom_NAME "patom"
#define CpPrimitiveAtom_CheckExact(op) Py_IS_TYPE((op), &CpPrimitiveAtom_Type)
#define CpPrimitiveAtom_Check(op) (PyObject_TypeCheck((op), &CpPrimitiveAtom_Type))

//------------------------------------------------------------------------------
// Bool

/// @struct _boolatomobj
/// @brief Struct representing a bool atom object.
///
/// This struct defines a bool atom object which is part of the CpFieldCAtom
/// family.
struct _boolatomobj
{
  CpBuiltinAtom_HEAD
};

/// @brief Bool atom object type
///
/// This variable defines the type object for bool atom objects, allowing
/// them to be used across the library.
// PyAPI_DATA(PyTypeObject) CpBoolAtom_Type;
#define CpBoolAtom_NAME "bool_t"

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

//------------------------------------------------------------------------------
// Char Atom
struct _charatomobj
{
  CpBuiltinAtom_HEAD
};

/// Char atom object type
// PyAPI_DATA(PyTypeObject) CpCharAtom_Type;
#define CpCharAtom_NAME "char_t"

/** @brief Checks if the given object is a char atom object */
#define CpCharAtom_CheckExact(op) Py_IS_TYPE((op), &CpCharAtom_Type)
/** @brief Checks if the given object is a char atom object */
#define CpCharAtom_Check(op) (PyObject_TypeCheck((op), &CpCharAtom_Type))

//------------------------------------------------------------------------------
// Padding
struct _paddingatomobj
{
  CpBuiltinAtom_HEAD

    char padding;
};

/// Padding atom object type
// PyAPI_DATA(PyTypeObject) CpPaddingAtom_Type;
#define CpPaddingAtom_NAME "padding_t"

/** @brief Checks if the given object is a padding atom object */
#define CpPaddingAtom_CheckExact(op) Py_IS_TYPE((op), &CpPaddingAtom_Type)
/** @brief Checks if the given object is a padding atom object */
#define CpPaddingAtom_Check(op) (PyObject_TypeCheck((op), &CpPaddingAtom_Type))

#endif