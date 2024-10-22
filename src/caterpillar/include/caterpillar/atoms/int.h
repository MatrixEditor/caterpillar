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

#include "caterpillar/atoms/builtins.h"

#if PY_3_13_PLUS
// Python3.13 comes with a new API
// https://docs.python.org/3/c-api/long.html#c.PyLong_FromUnsignedNativeBytes
#define CpCompat_PyLong_FromBuffer(buf, len, little_endian, signed_)           \
  (PyObject*)PyLong_FromUnsignedNativeBytes((const void*)(buf),                \
                                            (len),                             \
                                            (little_endian)                    \
                                              ? Py_ASNATIVEBYTES_LITTLE_ENDIAN \
                                              : Py_ASNATIVEBYTES_BIG_ENDIAN)

#define CpCompat_PyLong_AsBuffer(obj, buf, len, little_endian, signed_)        \
  PyLong_AsNativeBytes((obj),                                                  \
                       (void*)(buf),                                           \
                       (len),                                                  \
                       Py_ASNATIVEBYTES_UNSIGNED_BUFFER |                      \
                         ((little_endian) ? Py_ASNATIVEBYTES_LITTLE_ENDIAN     \
                                          : Py_ASNATIVEBYTES_BIG_ENDIAN))
#else

#define CpCompat_PyLong_FromBuffer(buf, len, little_endian, signed_)           \
  (PyObject*)_PyLong_FromByteArray(                                            \
    (unsigned char*)(buf), (len), (little_endian), (signed_))

#define CpCompat_PyLong_AsBuffer(obj, buf, len, little_endian, signed_)        \
  _PyLong_AsByteArray((PyLongObject*)(obj),                                    \
                      (unsigned char*)(buf),                                   \
                      (len),                                                   \
                      (little_endian),                                         \
                      (signed_))

#endif

struct _intatomobj
{
  CpBuiltinAtom_HEAD

    /// Stores the amount of bits this
    /// integer atom has in total
    PyObject* m_byte_count;

  /// Stores the byte count of the
  /// integer atom as native size_t
  /// value.
  size_t _m_byte_count;
  size_t _m_bits;

  /// Stores whether or not the integer
  /// is signed
  int _m_signed;

  /// Stores whether or not the integer
  /// is little endian
  int _m_little_endian;
};

/** @brief Checks if the given object is
 * an integer atom object */
#define CpIntAtom_CheckExact(op) Py_IS_TYPE((op), &CpIntAtom_Type)
/** @brief Checks if the given object is
 * an integer atom object */
#define CpIntAtom_Check(op) (PyObject_TypeCheck((op), &CpIntAtom_Type))

//------------------------------------------------------------------------------
// varint atom

struct _varintatomobj
{
  CpBuiltinAtom_HEAD

    /// Stores whether or not the integer
    /// is little endian
    int _m_little_endian;

  /// Specifies that the last significant
  /// byte will use a ``1`` to identify
  /// the end of the varint. Otherwise,
  /// zero will be used (which is the
  /// default setting).
  int _m_lsb;
};

#define CpVarIntAtom_CheckExact(op) Py_IS_TYPE((op), &CpVarIntAtom_Type)
#define CpVarIntAtom_Check(op) (PyObject_TypeCheck((op), &CpVarIntAtom_Type))

static inline CpVarIntAtomObject*
CpVarIntAtom_New(bool little_endian, bool lsb)
{
  return (CpVarIntAtomObject*)CpObject_Create(
    &CpVarIntAtom_Type, "II", little_endian, lsb);
}

#endif