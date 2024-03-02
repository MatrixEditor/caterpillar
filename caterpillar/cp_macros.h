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
#define _Cp_SetObj(varname, value)                                             \
  if (value) {                                                                 \
    Py_XSETREF(varname, Py_NewRef(value));                                     \
  }

#define _CpInit_SetObj(varname, value, cond, msg, ...)                         \
  do {                                                                         \
    if (value) {                                                               \
      if (cond) {                                                              \
        Py_XSETREF(varname, Py_NewRef(value));                                 \
      } else {                                                                 \
        PyErr_Format(PyExc_ValueError,                                         \
                     ("unable to set '%s': " msg),                             \
                     #varname,                                                 \
                     __VA_ARGS__);                                             \
      }                                                                        \
    }                                                                          \
  } while (0);

#define _CpModuleState_Set(varname, ...)                                       \
  state->varname = __VA_ARGS__;                                                \
  if (!state->varname) {                                                       \
    PyErr_SetString(PyExc_RuntimeError,                                        \
                    ("unable to create state object '" #varname "'"));         \
    return NULL;                                                               \
  }

#define _CpModuleState_Def(varname, objname, ...)                              \
  state->varname = __VA_ARGS__;                                                \
  if (!state->varname) {                                                       \
    PyErr_SetString(PyExc_RuntimeError,                                        \
                    ("unable to create state object '" objname "'"));          \
    return NULL;                                                               \
  }                                                                            \
  CpModule_AddObject(objname, state->varname);

#define _Cp_Immortal(name, type)                                               \
  static PyObject name##_Object = {                                            \
    _PyObject_EXTRA_INIT{ _Py_IMMORTAL_REFCNT }, &type                         \
  };

#define PyErr_SetContext(err, context, ...)                                    \
  do {                                                                         \
    PyErr_Format((err), __VA_ARGS__);                                          \
  } while (0);

#define CpState_AppendPath(newpath)                                            \
  Py_SETREF(state->m_path,                                                     \
            PyUnicode_FromFormat("%s.%s",                                      \
                                 _PyUnicode_AsString(state->m_path),           \
                                 _PyUnicode_AsString((newpath))));

#define GETATTR(op, name) PyObject_GetAttr((PyObject*)(op), (name))
#define HASATTR(op, name) PyObject_HasAttr((PyObject*)(op), (name))
#define SETATTR(op, name, value)                                               \
  PyObject_SetAttr((PyObject*)(op), (name), (value))
#define REPR(op, dst)                                                          \
  do {                                                                         \
    dst = PyObject_Repr((PyObject*)(op));                                      \
  } while (0);

#define _cp_assert(cond, error, rvalue, ...)                                   \
  if (!(cond)) {                                                               \
    PyErr_Format((error), __VA_ARGS__);                                        \
    return rvalue;                                                             \
  }

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

// ------------------------------------------------------------------------------
// CpField
// ------------------------------------------------------------------------------
#define CpField_New(op)                                                        \
  (PyObject_CallFunction((PyObject*)&CpField_Type, "O", (op)))

#define CpContext_NewEmpty() (PyObject_CallNoArgs((PyObject*)&CpContext_Type))
#define CpContext_New(op)                                                      \
  (PyObject_CallFunction((PyObject*)&CpContext_Type, "O", (op)))

#define CpObject_Create(type, format, ...)                                     \
  (PyObject_CallFunction((PyObject*)(type), format, __VA_ARGS__))

#define CpObject_CreateNoArgs(type) (PyObject_CallNoArgs((PyObject*)(type)))

// ------------------------------------------------------------------------------
// MATCH-CASE
// ------------------------------------------------------------------------------
#define MATCH
#define CASE_EXACT(type, op) if ((op)->ob_type == (type))
#define CASE(type, op) if (PyObject_IsInstance((op), (PyObject*)(type)))
#define CASE_COND(cond) if (cond)

#define debug(fmt, ...)                                                        \
  printf(("DEBUG:%s:%d " fmt "\n"), __FUNCTION__, __LINE__, __VA_ARGS__)

#endif