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
#ifndef LENGTHINFO_H
#define LENGTHINFO_H

#include "caterpillarapi.h"

// ---------------------------------------------------------------------------
// Length Hint

struct _lengthinfoobj
{
  PY_OBJECT_HEAD;

  Py_ssize_t m_length;
  int m_greedy;
};

static inline PyObject*
CpLengthInfo_New(Py_ssize_t pLength, int pGreedy)
{
  return CpObject_Create(&CpLengthInfo_Type, "ni", pLength, pGreedy);
}

static inline Py_ssize_t
CpLengthInfo_Length(PyObject* pObj)
{
  return _Cp_CAST(CpLengthInfoObject*, pObj)->m_length;
}

static inline int
CpLengthInfo_IsGreedy(PyObject* pObj)
{
  return _Cp_CAST(CpLengthInfoObject*, pObj)->m_greedy;
}

static inline void
CpLengthInfo_SetGreedy(PyObject* pObj, int pGreedy)
{
  _Cp_CAST(CpLengthInfoObject*, pObj)->m_greedy = pGreedy;
}

static inline PyObject*
CpLengthInfo_LengthAsLong(PyObject* pObj)
{
  return PyLong_FromSsize_t(_Cp_CAST(CpLengthInfoObject*, pObj)->m_length);
}

static inline int
CpLengthInfo_SetLength(PyObject* pObj, Py_ssize_t pLength)
{
  if (pLength < 0) {
    PyErr_SetString(PyExc_ValueError, "New length must not be negative!");
    return -1;
  }
  _Cp_CAST(CpLengthInfoObject*, pObj)->m_length = pLength;
  return 0;
}

static inline int
CpLengthInfo_SetLengthFromLong(PyObject* pObj, PyObject* pLengthObj)
{
  Py_ssize_t vLength = 0;
  if (!pLengthObj) {
    PyErr_SetString(PyExc_ValueError, "New length must not be NULL!");
    return -1;
  }

  vLength = PyLong_AsSsize_t(pLengthObj);
  PyErr_Clear();
  return CpLengthInfo_SetLength(pObj, vLength);
}

#endif // LENGTHINFO_H