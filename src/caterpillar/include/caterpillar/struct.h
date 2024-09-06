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
#include "caterpillar/field.h"

/* Caterpillar Struct C implementation */

/**
 * @brief Internal class used to store information about a field
 */
struct CpStructFieldInfo
{
  PyObject_HEAD

    /// the referenced field object
    CpFieldObject* m_field;

  // Excluded: True if the field is included in the struct
  int8_t s_excluded;

  // TODO: here's space for more settings
};

/// object type
// PyAPI_DATA(PyTypeObject) CpStructFieldInfo_Type;

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

/**
 * @brief Creates a new struct field info object
 *
 * @param field the field object
 * @return the new struct field info object
 */
// PyAPI_FUNC(CpStructFieldInfoObject*)
//   CpStructFieldInfo_New(CpFieldObject* field);

//---------------------------------------------------------------------------
// struct

/**
 * @brief C implementation of the Python equivalent.
 */
struct _structobj
{
  CpFieldAtom_HEAD PyTypeObject* m_model; // underlying class

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

/// Struct object type
// PyAPI_DATA(PyTypeObject) CpStruct_Type;

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

/**
 * @brief Add a field to the struct
 *
 * @param self the struct object
 * @param field the field information
 * @return 1 on success, 0 on failure
 */
// PyAPI_FUNC(int)
//   CpStruct_AddFieldInfo(CpStructObject* self, CpStructFieldInfoObject* field);

/**
 * @brief Add a field to the struct
 *
 * @param self the struct object
 * @param field the field information
 * @param exclude true if the field should be excluded
 * @return 1 on success, 0 on failure
 */
// PyAPI_FUNC(int)
//   CpStruct_AddField(CpStructObject* self, CpFieldObject* field, int exclude);

/**
 * @brief Create a new struct
 *
 * @param model the model object
 * @return the new struct object, or NULL on failure
 */
//PyAPI_FUNC(CpStructObject*) CpStruct_New(PyObject* model);

/**
 * @brief Get the annotations of the struct's model
 *
 * @param op the struct object
 * @param eval true if the annotations should be evaluated
 * @return the annotations, or NULL on failure
 */
// PyAPI_FUNC(PyObject*) CpStruct_GetAnnotations(CpStructObject* op, int eval);

/**
 * @brief Replace the annotation of the struct's model with the given value
 *
 * @param op the struct object
 * @param name the name of the annotation
 * @param value the new value of the annotation
 * @return 1 on success, 0 on failure
 */
// PyAPI_FUNC(int)
//   CpStruct_ReplaceType(CpStructObject* op, PyObject* name, PyObject* value);

/**
 * @brief Checks if the given struct has a given option
 *
 * @param op the object to check
 * @param option the option to check
 * @return 1 if the object has the option, 0 otherwise
 */
// PyAPI_FUNC(int) CpStruct_HasOption(CpStructObject* op, PyObject* option);

/**
 * @brief Checks if the given model stores a struct
 *
 * @param model the model object
 * @param m the module state, may be NULL
 * @return 1 if the model stores a struct, 0 otherwise
 */
// PyAPI_FUNC(int) CpStructModel_Check(PyObject* model, _modulestate* m);

/**
 * @brief Get the struct from the model
 *
 * @param model the model object
 * @param m the module state, may be NULL
 * @return the struct object, or NULL if the model does not store a struct
 */
// PyAPI_FUNC(PyObject*) CpStructModel_GetStruct(PyObject* model, _modulestate* m);
#endif