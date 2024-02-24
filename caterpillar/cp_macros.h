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
  if (PyModule_AddObject(m, name, (PyObject*)(value)) < 0) {                   \
    Py_DECREF(value);                                                          \
    Py_DECREF(m);                                                              \
    PyErr_SetString(PyExc_RuntimeError, "unable to add '" name "' to module"); \
    return NULL;                                                               \
  }

#define _Cp_Name(x) ("caterpillar." #x)

#define _CpModuleState_Def(varname, objname, ...)                              \
  state->varname = __VA_ARGS__;                                                \
  if (!state->varname) {                                                       \
    PyErr_SetString(PyExc_RuntimeError,                                        \
                    ("unable to create state object '" objname "'"));          \
    return NULL;                                                               \
  }                                                                            \
  CpModule_AddObject(objname, state->varname);

#define _Cp_Immortal(name, type)                                               \
  static PyObject name##_Object = { _PyObject_EXTRA_INIT{ _Py_IMMORTAL_REFCNT }, \
                                  &type };

// ------------------------------------------------------------------------------
// Option related macros
// ------------------------------------------------------------------------------
#define CpModule_AddOption(varname, name, objname)                             \
  _CpModuleState_Def(                                                          \
    varname,                                                                   \
    objname,                                                                   \
    PyObject_CallFunction((PyObject*)&CpOption_Type, "s", name));

#define CpModule_AddGlobalOptions(varname, objname)                            \
  _CpModuleState_Def(varname, objname, PySet_New(NULL));

// ------------------------------------------------------------------------------
// CpArch related macros
// ------------------------------------------------------------------------------
#define CpModule_AddArch(varname, name, size, objname)                         \
  _CpModuleState_Def(                                                          \
    varname,                                                                   \
    objname,                                                                   \
    PyObject_CallFunction((PyObject*)&CpArch_Type, "si", name, size));

#endif