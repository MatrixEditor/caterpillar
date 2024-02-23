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

#define CpType_Ready(op)                                                       \
  if (PyType_Ready(op) < 0)                                                    \
    return NULL;

#define CpModule_AddObject(name, value)                                        \
  Py_INCREF(value);                                                            \
  if (PyModule_AddObject(m, name, (PyObject *)(value)) < 0) {                  \
    Py_DECREF(value);                                                          \
    Py_DECREF(m);                                                              \
    return NULL;                                                               \
  }

#define CpModule_AddObjectRef(name, value)                                     \
  if (PyModule_AddObjectRef(m, name, (PyObject *)value) < 0) {                 \
    Py_DECREF(m);                                                              \
    return NULL;                                                               \
  }

#define _Cp_Name(x) ("caterpillar." #x)

// ------------------------------------------------------------------------------
// Option related macros
// ------------------------------------------------------------------------------
#define CpModule_AddOption(varname, name, objname)                             \
  state->varname =                                                             \
      PyObject_CallFunction((PyObject *)&CpOption_Type, "s", name);            \
  if (state->varname) {                                                        \
    return NULL;                                                               \
  }                                                                            \
  CpModule_AddObject(objname, state->varname);

#endif