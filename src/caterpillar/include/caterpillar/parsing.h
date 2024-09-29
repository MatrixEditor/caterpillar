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

#include "caterpillar/atomobj.h"
#include "caterpillar/module.h"
#include "caterpillar/state.h"

static inline int
_Cp_Pack(PyObject* op, PyObject* atom, CpLayerObject* layer)
{
  if (CpCAtom_Check(atom)) {
    return CpPack_CAtom(op, (CpCAtomObject*)atom, layer);
  }

  _modulestate* mod = layer->m_state->mod;
  PyObject* result = CpAtom_Pack(atom, mod->str___pack__, op, (PyObject*)layer);
  if (result == NULL) {
    return -1;
  }
  Py_DECREF(result);
  return 0;
}

static inline PyObject*
_Cp_Unpack(PyObject* op, CpLayerObject* layer)
{
  if (CpCAtom_Check(op)) {
    return CpUnpack_CAtom((CpCAtomObject*)op, layer);
  }
  return PyObject_CallMethodOneArg(
    op, layer->m_state->mod->str___unpack__, (PyObject*)layer);
}

#endif