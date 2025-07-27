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
#ifndef CP_BUILTIN_OFFSET_H
#define CP_BUILTIN_OFFSET_H

#include "caterpillar/atoms/builtin/builtin.h"
#include "caterpillar/caterpillarapi.h"

//------------------------------------------------------------------------------
// Offset
//------------------------------------------------------------------------------
struct _offsetatomobj
{
  CpBuiltinAtom_HEAD;

  /// Stores a reference to the actual parsing struct that will be used
  PyObject* m_atom;
  PyObject* m_offset;
  PyObject* m_whence;

  // -- internal state
  int s_is_number;
  int s_keep_pos;
};

#define PY_SEEK_SET 0
#define PY_SEEK_CUR 1
#define PY_SEEK_END 2

#define CpOffsetAtom_CheckExact(op) Py_IS_TYPE((op), &CpOffsetAtom_Type)
#define CpOffsetAtom_Check(op) PyObject_TypeCheck((op), &CpOffsetAtom_Type)

static inline PyObject*
CpOffsetAtom_New(PyObject* atom, PyObject* offset, int whence)
{
  return CpObject_Create(&CpOffsetAtom_Type, "OOi", atom, offset, whence);
}

static inline PyObject*
CpOffsetAtom_GetAtom(PyObject* pObj)
{
  return Py_XNewRef(_Cp_CAST(CpOffsetAtomObject*, pObj)->m_atom);
}

static inline PyObject*
CpOffsetAtom_GetOffset(PyObject* pObj)
{
  return Py_XNewRef(_Cp_CAST(CpOffsetAtomObject*, pObj)->m_offset);
}

static inline PyObject*
CpOffsetAtom_Whence(PyObject* pObj)
{
  return Py_XNewRef(_Cp_CAST(CpOffsetAtomObject*, pObj)->m_whence);
}

static inline Py_ssize_t
CpOffsetAtom_WhenceAsLong(PyObject* pObj)
{
  PyObject* whence = _Cp_CAST(CpOffsetAtomObject*, pObj)->m_whence;
  return (int)PyLong_AsSsize_t(whence);
}

static inline int
CpOffsetAtom_SetAtom(PyObject* pObj, PyObject* pAtom)
{
  _Cp_CAST(CpOffsetAtomObject*, pObj)->m_atom = Py_NewRef(pAtom);
  return 0;
}

static inline int
CpOffsetAtom_SetOffset(PyObject* pObj, PyObject* pOffset)
{
  _Cp_CAST(CpOffsetAtomObject*, pObj)->m_offset = Py_NewRef(pOffset);
  return 0;
}

static inline int
CpOffsetAtom_SetWhence(PyObject* pObj, PyObject* pWhence)
{
  _Cp_CAST(CpOffsetAtomObject*, pObj)->m_whence = Py_NewRef(pWhence);
  return 0;
}

static inline int
CpOffsetAtom_IsKeepPosition(PyObject* pObj)
{
  return _Cp_CAST(CpOffsetAtomObject*, pObj)->s_keep_pos;
}

static inline void
CpOffsetAtom_SetKeepPosition(PyObject* pObj, int keep_pos)
{
  _Cp_CAST(CpOffsetAtomObject*, pObj)->s_keep_pos = keep_pos;
}

#endif