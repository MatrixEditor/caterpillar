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
#ifndef INTATOMOBJ_H
#define INTATOMOBJ_H

#include "caterpillar/caterpillarapi.h"
#include "caterpillar/field.h"

struct _intatomobj
{
  CpFieldCAtom_HEAD

    /// Stores the amount of bits this integer atom
    /// has in total
    PyObject* m_byte_count;

  /// Stores the byte count of the integer atom as native
  /// size_t value.
  size_t _m_byte_count;
  size_t _m_bits;

  /// Stores whether or not the integer is signed
  int _m_signed;

  /// Stores whether or not the integer is little endian
  int _m_little_endian;
};

/// Integer atom object type
// PyAPI_DATA(PyTypeObject) CpIntAtom_Type;

/** @brief Checks if the given object is an integer atom object */
#define CpIntAtom_CheckExact(op) Py_IS_TYPE((op), &CpIntAtom_Type)
/** @brief Checks if the given object is an integer atom object */
#define CpIntAtom_Check(op) (PyObject_IsInstance((op), &CpIntAtom_Type))

PyAPI_FUNC(int)
  CpIntAtom_Pack(CpIntAtomObject* self, PyObject* value, CpLayerObject* layer);

PyAPI_FUNC(PyObject*)
  CpIntAtom_Unpack(CpIntAtomObject* self, CpLayerObject* layer);
#endif