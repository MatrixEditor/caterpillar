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
#ifndef CONSTATOMOBJ_H
#define CONSTATOMOBJ_H

#include "caterpillar/atoms/builtins.h"

struct _constatomobj
{
  CpBuiltinAtom_HEAD

  PyObject *m_value;
  PyObject *m_atom;
};

#define CpConstAtom_NAME "const"
#define CpConstAtom_CheckExact(op) Py_IS_TYPE((op), &CpConstAtom_Type)
#define CpConstAtom_Check(op) PyObject_TypeCheck((op), &CpConstAtom_Type)

#endif