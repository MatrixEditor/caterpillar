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
#ifndef CP_MACROS_H
#define CP_MACROS_H

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif

#include <Python.h>

#define _Cp_Name(x) ("caterpillar._C." #x)

#define _Cp_SetObj(varname, value)                                             \
  if (value) {                                                                 \
    Py_XSETREF(varname, Py_NewRef(value));                                     \
  }

#define CpObject_Create(type, format, ...)                                     \
  (PyObject_CallFunction((PyObject*)(type), format, __VA_ARGS__))

#define CpObject_CreateNoArgs(type) (PyObject_CallNoArgs((PyObject*)(type)))
#define CpObject_CreateOneArg(type, arg)                                       \
  (PyObject_CallOneArg(((PyObject*)(type)), (arg)))


#define _Cp_InitNoArgs(type, args, kw) \
  if ((args && PyTuple_Size(args)) || (kw && PyDict_Size(kw))) { \
    PyErr_SetString(PyExc_TypeError, \
                    (#type " cannot be initialized with arguments")); \
    return -1; \
  } \
  return 0;
#endif