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
#ifndef CP_STRUCT_H
#define CP_STRUCT_H

#include "caterpillar/caterpillarapi.h"
#include "caterpillar/atoms/builtins.h"

/* Caterpillar Struct C implementation */

/**
 * @brief Internal class used to store information about a field
 */
struct _fieldinfoobj
{
  PyObject_HEAD

  /// the referenced field object
  PyObject *m_field;

  /// the name of the field
  PyObject *m_name;

  /// The configured default value.
  PyObject* m_default;

  // Excluded: True if the field is included in the struct
  int8_t s_excluded;

  // TODO: here's space for more settings
};

/**
 * @brief Checks if the given object is a struct field info object
 *
 * This macro will check the exact type of the object and return
 * 1 if it is of type `CpStructFieldInfo` and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is a struct field info object, 0 otherwise
 */
#define CpStructFieldInfo_CheckExact(op)                                       \
  Py_IS_TYPE((op), &CpStructFieldInfo_Type)

/**
 * @brief Checks if the given object is a struct field info object
 *
 * This macro will check the type of the object and return
 * 1 if it is a struct field info object and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is a struct field info object, 0 otherwise
 */
#define CpStructFieldInfo_Check(op)                                            \
  PyObject_TypeCheck((op), &CpStructFieldInfo_Type)

//---------------------------------------------------------------------------
// struct

/**
 * @brief C implementation of the Python equivalent.
 */
struct _structobj
{
  CpBuiltinAtom_HEAD
  PyTypeObject* m_model; // underlying class

  PyObject* m_members; // Dict[str, FieldInfo]
  PyObject* m_options; // set[CpOption]

  PyObject* m_endian;
  PyObject* m_arch;
  PyObject* m_field_options;

  // internal states
  int8_t s_union;
  int8_t s_kwonly;
  int8_t s_alter_type;
  PyObject* s_std_init_fields;    // list[FieldInfo]
  PyObject* s_kwonly_init_fields; // list[FieldInfo]

  _modulestate* s_mod;
};

/**
 * @brief Checks if the given object is a struct object
 *
 * This macro will check the exact type of the object and return
 * 1 if it is of type `CpStruct` and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is a struct object, 0 otherwise
 */
#define CpStruct_CheckExact(op) Py_IS_TYPE((op), &CpStruct_Type)

/**
 * @brief Checks if the given object is a struct object
 *
 * This macro will check the type of the object and return
 * 1 if it is a struct object and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is a struct object, 0 otherwise
 */
#define CpStruct_Check(op) PyObject_TypeCheck((op), &CpStruct_Type)

#endif