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
#ifndef CP_PARSING_H
#define CP_PARSING_H

#include "caterpillar/field.h"
#include "caterpillar/macros.h"
#include "caterpillar/state.h"
#include "caterpillar/struct.h"

PyAPI_FUNC(PyObject*) CpTypeOf(PyObject* op);
PyAPI_FUNC(PyObject*) CpTypeOf_Field(CpFieldObject* field);
PyAPI_FUNC(PyObject*) CpTypeOf_Common(PyObject* op);

PyAPI_FUNC(int)
  CpPack(PyObject* op, PyObject* atom, PyObject* io, PyObject* globals);
PyAPI_FUNC(int)
  CpPack_Field(PyObject* op, CpFieldObject* field, CpLayerObject* layer);
PyAPI_FUNC(int)
  CpPack_Common(PyObject* op, PyObject* atom, CpLayerObject* layer);
PyAPI_FUNC(int)
  CpPack_Struct(PyObject* op, CpStructObject* struct_, CpLayerObject* layer);
PyAPI_FUNC(int) _Cp_Pack(PyObject* op, PyObject* atom, CpLayerObject* layer);
PyAPI_FUNC(int)
  _CpPack_EvalLength(CpLayerObject* layer, Py_ssize_t size, bool* greedy, Py_ssize_t* length);

PyAPI_FUNC(PyObject*) CpSizeOf(PyObject* op, PyObject* globals);
PyAPI_FUNC(PyObject*)
  CpSizeOf_Field(CpFieldObject* field, CpLayerObject* layer);
PyAPI_FUNC(PyObject*)
  CpSizeOf_Struct(CpStructObject* struct_, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) CpSizeOf_Common(PyObject* atom, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) _Cp_SizeOf(PyObject* atom, CpLayerObject* layer);

PyAPI_FUNC(PyObject*) CpUnpack(PyObject* atom, PyObject* io, PyObject* globals);
PyAPI_FUNC(PyObject*)
  CpUnpack_Field(CpFieldObject* field, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) CpUnpack_Common(PyObject* atom, CpLayerObject* layer);
PyAPI_FUNC(PyObject*)
  CpUnpack_Struct(CpStructObject* struct_, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) _Cp_Unpack(PyObject* atom, CpLayerObject* layer);
PyAPI_FUNC(int)
  _CpUnpack_EvalLength(CpLayerObject* layer, bool* greedy, Py_ssize_t* length);

#endif