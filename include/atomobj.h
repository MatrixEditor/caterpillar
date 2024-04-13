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
#ifndef ATOMOBJ_H
#define ATOMOBJ_H

#include "macros.h"

/**
 * @brief Special base class for all atom objects
 *
 * This class/struct is used as a base class for all atom objects
 * in the library. It only contains method definitions and does not
 * provide any actual functionality. Fields/Attributes should be
 * defined in the derived class.
 *
 * @see _catomobj
 */
typedef struct _atomobj
{
  PyObject_HEAD
} CpAtomObject;

/// Atom object type
PyAPI_DATA(PyTypeObject) CpAtom_Type;

/**
 * @brief Checks if the given object is an atom object
 *
 * This macro will check the exact type of the object and return
 * 1 if it is of type `CpAtomObject` and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an atom object, 0 otherwise
 */
#define CpAtom_CheckExact(op) Py_IS_TYPE((op), &CpAtom_Type)

/**
 * @brief Checks if the given object is an atom object
 *
 * This macro will check the type of the object and return
 * 1 if it is an atom object and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an atom object, 0 otherwise
 */
#define CpAtom_Check(op)                                                       \
  PyObject_TypeCheck((PyObject*)(op), (PyObject*)&CpAtom_Type)

// default method names
#define CpAtom_Pack_STR "__pack__"
#define CpAtom_Unpack_STR "__unpack__"
#define CpAtom_PackMany_STR "__pack_many__"
#define CpAtom_UnpackMany_STR "__unpack_many__"
#define CpAtom_Size_STR "__size__"
#define CpAtom_Type_STR "__type__"

// default utility macros

/**
 * @brief Checks if the given object has an attribute
 */
#define CpAtom_HasAttrString(op, name) PyObject_HasAttrString((op), (name))

/**
 * @brief Checks if the given object has an attribute
 */
#define CpAtom_HasAttr(op, name) PyObject_HasAttr((op), (name))

#define CpAtom_HasPack(op) CpAtom_HasAttrString((op), CpAtom_Pack_STR)
#define CpAtom_HasUnpack(op) CpAtom_HasAttrString((op), CpAtom_Unpack_STR)
#define CpAtom_HasPackMany(op) CpAtom_HasAttrString((op), CpAtom_PackMany_STR)
#define CpAtom_HasUnpackMany(op)                                               \
  CpAtom_HasAttrString((op), CpAtom_UnpackMany_STR)
#define CpAtom_HasSize(op) CpAtom_HasAttrString((op), CpAtom_Size_STR)
#define CpAtom_HasType(op) CpAtom_HasAttrString((op), CpAtom_Type_STR)

// API functions

/**
 * @brief Packs the given object (`op`) using the current context by calling the
 * `__pack__` method on the `atom` instance.
 *
 * @param atom the atom object
 * @param attrname the attribute name of the `__pack__` method
 * @param op the object to pack
 * @param ctx the context object
 * @return the result of the `__pack__` method or `NULL` on error
 */
PyAPI_FUNC(PyObject*)
  CpAtom_Pack(PyObject* atom, PyObject* attrname, PyObject* op, PyObject* ctx);

#endif