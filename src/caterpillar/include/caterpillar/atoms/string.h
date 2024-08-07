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
#ifndef STRINGATOMOBJ_H
#define STRINGATOMOBJ_H

#include "caterpillar/caterpillar.h"
#include "caterpillar/field.h"

struct _stringatomobj
{
  CpFieldCAtom_HEAD

    PyObject* m_length;
  PyObject* m_errors;
  PyObject* m_encoding;
};

// PyAPI_DATA(PyTypeObject) CpStringAtom_Type;

#define CpStringAtom_CheckExact(op) Py_IS_TYPE((op), &CpStringAtom_Type)
#define CpStringAtom_Check(op) PyObject_TypeCheck((op), &CpStringAtom_Type)

PyAPI_FUNC(int) CpStringAtom_Pack(CpStringAtomObject* self,
                                  PyObject* value,
                                  CpLayerObject* layer);

PyAPI_FUNC(PyObject*)
  CpStringAtom_Unpack(CpStringAtomObject* self, CpLayerObject* layer);

#endif