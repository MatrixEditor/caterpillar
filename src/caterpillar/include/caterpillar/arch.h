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
#ifndef CP_ARCH_H
#define CP_ARCH_H

#include "caterpillarapi.h"

// -----------------------------------------------------------------------------
// CAPI Architecture and Byte Order Concepts
//
// Each *cArch* object uses two attributes that are shared between the
// Python and C implementations. Likewise, the *cByteOrder* object
// relies on two attributes defined by the _EndianLike protocol.
// -----------------------------------------------------------------------------

/**
 * @brief Represents an architecture configuration.
 *
 * The `_archobj` struct encapsulates architectural information, such as
 * its name and pointer size. This object is typically used by pointer
 * atoms to model architecture-specific characteristics.
 */
struct _archobj
{
  PY_OBJECT_HEAD;

  /// Name of the architecture.
  PyObject* name;

  /// Size of pointers for this architecture, in bytes.
  int pointer_size;
};

/**
 * @brief Determine if an object is exactly of type `CpArchObject`.
 *
 * Checks whether the specified Python object is an exact instance of
 * `CpArchObject`. Returns 1 if true, 0 otherwise.
 *
 * @param op Python object to check.
 * @return 1 if the object is exactly a `CpArchObject`; 0 otherwise.
 */
#define CpArch_CheckExact(op) Py_IS_TYPE((op), &CpArch_Type)

/**
 * @brief Determine if an object is an instance of `CpArchObject` or its
 * subclasses.
 *
 * Checks whether the specified Python object is an instance of `CpArchObject`
 * or any of its subclasses. Returns 1 if true, 0 otherwise.
 *
 * @param op Python object to check.
 * @return 1 if the object is an instance of `CpArchObject`; 0 otherwise.
 */
#define CpArch_Check(op) PyObject_TypeCheck((PyObject*)(op), &CpArch_Type)

/**
 * @brief Create a new `CpArchObject` instance.
 *
 * Constructs a new architecture object with the specified name and pointer
 * size.
 *
 * @param name Name of the architecture.
 * @param ptrSize Pointer size in bytes.
 * @return A new `CpArchObject` instance on success; NULL on failure.
 */
static PyObject*
CpArch_New(const char* name, int ptrSize)
{
  return CpObject_Create(&CpArch_Type, "si", name, ptrSize);
}

/**
 * @brief Retrieve the name of an architecture object.
 *
 * @param obj A valid `CpArchObject` instance.
 * @return New reference to the name attribute.
 */
static inline PyObject*
CpArch_GetName(PyObject* obj)
{
  return Py_NewRef(_Cp_CAST(CpArchObject*, obj)->name);
}

/**
 * @brief Retrieve the pointer size of an architecture object.
 *
 * @param obj A valid `CpArchObject` instance.
 * @return Pointer size in bytes.
 */
static inline int
CpArch_GetPtrSize(PyObject* obj)
{
  return _Cp_CAST(CpArchObject*, obj)->pointer_size;
}

// -----------------------------------------------------------------------------
// Endian
// -----------------------------------------------------------------------------

/**
 * @brief Represents an endianness configuration.
 *
 * The `_endianobj` struct defines an endianness type, including its
 * human-readable name and format character used for data struct packing.
 */
struct _endianobj
{
  PY_OBJECT_HEAD;

  /// The human readable name of this endian
  PyObject* name;

  /// struct format character
  char id;
};

/**
 * @brief Determine if an object is exactly of type `CpEndianObject`.
 *
 * Checks whether the specified Python object is an exact instance of
 * `CpEndianObject`. Returns 1 if true, 0 otherwise.
 *
 * @param op Python object to check.
 * @return 1 if the object is exactly a `CpEndianObject`; 0 otherwise.
 */
#define CpEndian_CheckExact(op) Py_IS_TYPE((op), &CpEndian_Type)

/**
 * @brief Determine if an object is an instance of `CpEndianObject` or its
 * subclasses.
 *
 * Checks whether the specified Python object is an instance of `CpEndianObject`
 * or any of its subclasses. Returns 1 if true, 0 otherwise.
 *
 * @param op Python object to check.
 * @return 1 if the object is an instance of `CpEndianObject`; 0 otherwise.
 */
#define CpEndian_Check(op) PyObject_TypeCheck((PyObject*)(op), &CpEndian_Type)

/**
 * @brief Create a new `CpEndianObject` instance.
 *
 * Constructs a new endian object with the specified name and format character.
 *
 * @param name Human-readable name of the endianness.
 * @param id Format character used for struct packing.
 * @return A new `CpEndianObject` instance on success; NULL on failure.
 */
static inline PyObject*
CpEndian_New(const char* name, char id)
{
  return CpObject_Create(&CpEndian_Type, "sb", name, id);
}

/**
 * @brief Retrieve the name of an endianness object.
 *
 * @param obj A valid `CpEndianObject` instance.
 * @return New reference to the name attribute.
 */
static inline PyObject*
CpEndian_GetName(PyObject* obj)
{
  return Py_NewRef(_Cp_CAST(CpEndianObject*, obj)->name);
}

/**
 * @brief Retrieve the format character identifier for an endianness object.
 *
 * @param obj A valid `CpEndianObject` instance.
 * @return Format character used for struct packing.
 */
static inline char
CpEndian_GetId(PyObject* obj)
{
  return _Cp_CAST(CpEndianObject*, obj)->id;
}

/**
 * @brief Set the byte order of the specified object.
 *
 * Invokes the `__set_byteorder__` method on the target object to update
 * its byte order configuration. Returns NULL if the method is not
 * present.
 *
 * @param op Python object that supports the `__set_byteorder__` method.
 * @param endian New `CpEndianObject` to set as the byte order.
 * @return New reference to the result on success; NULL on failure.
 */
static inline PyObject*
CpEndian_SetEndian(PyObject* op, CpEndianObject* endian)
{
  PyObject* attr = PyObject_GetAttrString(op, "__set_byteorder__");
  if (!attr) {
    return NULL;
  }
  PyObject* ret = PyObject_CallOneArg(attr, (PyObject*)endian);
  if (!ret) {
    return NULL;
  }
  Py_DECREF(attr);
  return ret;
}

#endif