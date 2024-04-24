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
 * @brief Defines the base type for atom objects to be a Atom
 */
#define CpAtom_HEAD CpAtomObject ob_base;

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
#define CpAtom_Check(op) PyObject_TypeCheck((op), &CpAtom_Type)

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

// ---------------------------------------------------------------------------
// CAtom

/**
 * @brief Size-Protocol
 *
 * Each atom object may implement the `__size__` method, which is used
 * to determine the size of the object. Its C function pointer must conform
 * to this type definition.
 *
 * The signature of this function is as follows:
 * @code {.cpp}
 * PyObject* sizefunc(PyObject* self, PyObject* ctx);
 * @endcode
 *
 * @param atom the atom object (self)
 * @param ctx the context object
 * @return the size of the object
 */
typedef PyObject* (*sizefunc)(PyObject*, PyObject*);

/**
 * @brief Type-Protocol
 *
 * In order to replace types accordingly, each atom object may implement
 * the `__type__` method. It must return a new type object, or
 * `NotImplemented` for any type.
 *
 * The signature of this function is as follows:
 * @code {.cpp}
 * PyObject* typefunc(PyObject* self, PyObject* ctx);
 * @endcode
 *
 * @param atom the atom object (self)
 * @param ctx the context object
 * @return the type of the object
 */
typedef PyObject* (*typefunc)(PyObject*);

/**
 * @brief Pack-Protocol
 *
 * Each atom object may implement the `__pack__` method, which is used
 * to pack an object to the underlying stream. Note that the context
 * parameter is set to a `PyObject` instead of a specialized `CpContext`
 * or `CpLayer`. The provided context object must implement the context
 * protocol, therefore this function is context type independent.
 *
 * The signature of this function is as follows:
 * @code {.cpp}
 * int packfunc(PyObject* self, PyObject* op, PyObject* ctx);
 * @endcode
 *
 * @param self the atom object (self)
 * @param op the object to pack
 * @param ctx the context object
 * @return the result of the `__pack__` method
 */
typedef int (*packfunc)(PyObject*, PyObject*, PyObject*);

/**
 * @brief Pack-Protocol (many)
 *
 * This is another specialized version of the `packfunc` function, which
 * is used to pack multiple objects to the underlying stream. See `packfunc`
 * for more information.
 */
typedef int (*packmanyfunc)(PyObject*, PyObject*, PyObject*);

/**
 * @brief Unpack-Protocol
 *
 * Each atom object may implement the `__unpack__` method, which is used
 * to unpack an object from the underlying stream. The same notes from
 * the `packfunc` apply here.
 *
 * @param self the atom object (self)
 * @param ctx the context object
 * @return the result of the `__unpack__` method, or `NULL` on error
 */
typedef PyObject* (*unpackfunc)(PyObject*, PyObject*);

/**
 * @brief Unpack-Protocol (many)
 *
 * This is another specialized version of the `unpackfunc` function, which
 * is used to unpack multiple objects from the underlying stream. See
 * `unpackfunc` for more information.
 */
typedef PyObject* (*unpackmanyfunc)(PyObject*, PyObject*);

/// Experimental API
/**
 * @brief Bits-Protocol
 *
 * Each atom object may implement the `__bits__` method, which is only used
 * by the `Bitfield` class. It must return the amount of bits the object
 * occupies.
 *
 * The signature of this function is as follows:
 * @code {.cpp}
 * PyObject* bitsfunc(PyObject* self);
 * @endcode
 *
 * @param atom the atom object (self)
 * @param ctx the context object
 * @return the result of the `__bits__` method
 */
typedef PyObject* (*bitsfunc)(PyObject*);

/**
 * @brief Defines the base type for atom objects to be a CAtom
 */
#define CpCAtom_HEAD CpCAtomObject ob_base;

/**
 * @brief Atom object for C types
 */
typedef struct _catomobj
{
  CpAtom_HEAD;

  // C functions to implement
  sizefunc ob_size;
  typefunc ob_type;
  packfunc ob_pack;
  packmanyfunc ob_pack_many;
  unpackfunc ob_unpack;
  unpackmanyfunc ob_unpack_many;
  bitsfunc ob_bits;
} CpCAtomObject;

/// Atom object type
PyAPI_DATA(PyTypeObject) CpCAtom_Type;

/**
 * @brief Checks if the given object is an atom
 *
 * This macro will check the type of the object and return
 * 1 if it is an atom and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an atom, 0 otherwise
 */
#define CpCAtom_Check(op) Py_IS_TYPE((op), &CpCAtom_Type)

/**
 * @brief Checks if the given object is an atom
 *
 * This macro will check the exact type of the object and return
 * 1 if it is of type `CpCAtom` and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an atom, 0 otherwise
 */
#define CpCAtom_CheckExact(op) Py_TYPE(op) == &CpCAtom_Type

#define Cp_CATOM(x) (x)->ob_base

#endif