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
#ifndef CP_FIELD_H
#define CP_FIELD_H

#include "atomobj.h"

/* Caterpillar Field definition */

/**
 * @brief C implementation of the Python equivalent.
 *
 * Represents a field in a data structure.
 */
struct _fieldobj
{
  PyObject_HEAD

  /// The name of this field
  PyObject* m_name;

  /// Stores a reference to the actual parsing struct that will be used
  /// to parse or build our data. This attribute is never null.
  PyObject* m_atom;

  /// An automatically inferred or explicitly specified byte order. Note that
  /// this attribute may have no impact on the underlying struct. The default
  /// byte order is `NATIVE_ENDIAN`.
  PyObject* m_endian;

  /// Using the `@` operator an offset can be assigned to a field. If set, the
  /// stream will be reset and set to the original position.
  ///
  /// The minus one indicates that no offset has been associated with this
  /// field.
  ///
  /// @see CpField_GetOffset
  PyObject* m_offset;

  /// Additional options that can be enabled using the logical OR operator
  /// `|`.
  ///
  /// Note that there are default options that will be set automatically:
  ///  * `field:keep_position`:
  ///    Persists the streams position after parsing data using the
  ///    underlying struct. In relation to `offset`, this option will reset
  ///    the stream to its original position if deactivated.
  ///  * `field:dynamic`:
  ///    Specifies that this field does not store a constant size.
  ///  * `field:sequential`:
  ///    An automatic flag that indicates this field stores a sequential
  ///    struct.
  PyObject* m_options;

  /// A constant or dynamic value to represent the amount of structs. Zero
  /// indicates there are no sequence types associated with this field.
  PyObject* m_length;

  /// An extra attribute that stores additional options that can be translates
  /// as a switch statement.
  PyObject* m_switch;

  /// Given optional execution this attribute should be used to return a boolean
  /// value that decides whether the value of this field should be set. Using
  /// `//` the condition can be set during class declaration.
  PyObject* m_condition;

  /// The field's architecture (inferred or explicitly specified).
  PyObject* m_arch;

  /// The configured default value.
  PyObject* m_default;

  // internal state variables
  int8_t s_size;
  int8_t s_type;
  int8_t s_sequential;
  int8_t s_keep_pos;
};

/// Field type
// PyAPI_DATA(PyTypeObject) CpField_Type;

/**
 * @brief Check whether the given object is afield
 *
 * @param v the object to check
 * @return true if the object is a field
 * @return false if the object is not a field
 */
#define CpField_CheckExact(v) Py_IS_TYPE((v), &CpField_Type)

/**
 * @brief Check whether the given object is a field
 *
 * @param v the object to check
 * @return true if the object is a field
 * @return false if the object is not a field
 */
#define CpField_Check(v) PyObject_TypeCheck((v), &CpField_Type)

// -----------------------------------------------------------------------------
// field atom

/**
 * @brief C implementation of the Python equivalent (FieldMixin).
 *
 * A simple mixin to support operators used to create `Field` instances.
 */
struct _fieldatomobj
{
  CpAtom_HEAD
};

/// Field atom type
// PyAPI_DATA(PyTypeObject) CpFieldAtom_Type;

/**
 * @brief Check whether the given object is a field atom
 *
 * @param v the object to check
 * @return true if the object is a field atom
 * @return false if the object is not a field atom
 */
#define CpFieldAtom_CheckExact(v) Py_IS_TYPE((v), &CpFieldAtom_Type)

/**
 * @brief Check whether the given object is a field atom
 *
 * @param v the object to check
 * @return true if the object is a field atom
 * @return false if the object is not a field atom
 */
#define CpFieldAtom_Check(v) PyObject_TypeCheck((v), &CpFieldAtom_Type)

#define CpFieldAtom_HEAD CpFieldAtomObject ob_base;

// -----------------------------------------------------------------------------
// field C atom
struct _fieldcatomobj
{
  CpCAtom_HEAD
};

/**
 * @brief Check whether the given object is a field C atom
 *
 * @param v the object to check
 * @return true if the object is a field C atom
 * @return false if the object is not a field C atom
 */
#define CpFieldCAtom_CheckExact(v) Py_IS_TYPE((v), &CpFieldCAtom_Type)

/**
 * @brief Check whether the given object is a field C atom
 *
 * @param v the object to check
 * @return true if the object is a field C atom
 * @return false if the object is not a field C atom
 */
#define CpFieldCAtom_Check(v) PyObject_TypeCheck((v), &CpFieldCAtom_Type)

#define CpFieldCAtom_HEAD CpFieldCAtomObject ob_base;
#define CpFieldCAtom_CATOM(x) (x)->ob_base.ob_base

#endif