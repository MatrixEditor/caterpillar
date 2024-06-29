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
#ifndef CP_ARCH_H
#define CP_ARCH_H

#include "macros.h"
#include "module.h"

/// Arch object type
PyAPI_DATA(PyTypeObject) CpArch_Type;

/**
 * @brief Configuration class that represents an architecture.
 *
 * This class/struct will be used by pointer atoms to represent
 * an architecture with its pointer size.
 */
typedef struct _archobj
{
  /// The name of the architecture
  PyObject_HEAD PyObject* name;
  /// The pointer size of the architecture
  int pointer_size;
} CpArchObject;

/**
 * @brief Checks if the given object is an architecture object
 *
 * This macro will check the exact type of the object and return
 * 1 if it is of type `CpArchObject` and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an architecture object, 0 otherwise
 */
#define CpArch_CheckExact(op) Py_IS_TYPE((op), &CpArch_Type)

/**
 * @brief Checks if the given object is an architecture object
 *
 * This macro will check the type of the object and return
 * 1 if it is an architecture object and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an architecture object, 0 otherwise
 */
#define CpArch_Check(op) PyObject_TypeCheck((PyObject*)(op), &CpArch_Type)

/// Endian object type
PyAPI_DATA(PyTypeObject) CpEndian_Type;

/**
 * @brief Configuration class that represents endian configuration.
 */
typedef struct _endianobj
{
  /// The human readable name of this endian
  PyObject_HEAD PyObject* name;
  /// struct format character
  char id;
} CpEndianObject;

/**
 * @brief Checks if the given object is an endian object
 *
 * This macro will check the exact type of the object and return
 * 1 if it is of type `CpEndianObject` and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an endian object, 0 otherwise
 */
#define CpEndian_CheckExact(op) Py_IS_TYPE((op), &CpEndian_Type)

/**
 * @brief Checks if the given object is an endian object
 *
 * This macro will check the type of the object and return
 * 1 if it is an endian object and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an endian object, 0 otherwise
 */
#define CpEndian_Check(op) PyObject_TypeCheck((PyObject*)(op), &CpEndian_Type)

/**
 * @brief Checks if the given object is a little endian
 *
 * @param endian the object to check
 * @param mod the module state
 * @return 1 if the object is a little endian, 0 otherwise
 *
 * @note 1 is returned even if the current object may be the native endian
 */
PyAPI_FUNC(int) CpEndian_IsLittleEndian(CpEndianObject *endian, _modulestate *mod);

#endif