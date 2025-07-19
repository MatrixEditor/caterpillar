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
#ifndef __CP_PRIVATE_H
#define __CP_PRIVATE_H

#include "caterpillar/caterpillar.h"

#define _Cp_NameStr(x) ("caterpillar._C." x)
#define _Cp_Name(x) ("caterpillar._C." #x)

#define _Cp_SetObj(varname, value)                                             \
  if (value) {                                                                 \
    Py_XSETREF(varname, Py_NewRef(value));                                     \
  }

#define _Cp_InitNoArgs(type, args, kw)                                         \
  if ((args && PyTuple_Size(args)) || (kw && PyDict_Size(kw))) {               \
    PyErr_SetString(PyExc_TypeError,                                           \
                    (#type " cannot be initialized with arguments"));          \
    return -1;                                                                 \
  }                                                                            \
  return 0;

#define CpModule_AddObject(name, value, ret)                                  \
  Py_INCREF(value);                                                            \
  if (PyModule_AddObject(m, name, (PyObject*)(value)) < 0) {                   \
    Py_DECREF(value);                                                          \
    Py_DECREF(m);                                                              \
    PyErr_SetString(PyExc_RuntimeError, "unable to add '" name "' to module"); \
    return (ret);                                                              \
  }

#define CpModuleState_AddObject(varName, objName, ret, ...)                    \
  state->varName = __VA_ARGS__;                                                \
  if (!state->varName) {                                                       \
    PyErr_SetString(PyExc_RuntimeError,                                        \
                    ("unable to create state object '" objName "'"));          \
    return (ret);                                                              \
  }                                                                            \
  CpModule_AddObject(objName, state->varName, ret);

#define CpModuleState_Set(varName, ...)                                        \
  state->varName = __VA_ARGS__;                                                \
  if (!state->varName) {                                                       \
    PyErr_SetString(PyExc_RuntimeError,                                        \
                    ("unable to create state object '" #varName "'"));         \
    return NULL;                                                               \
  }

#define _CpEndian_ImplSetByteorder_MethDef(name, docs)                         \
  {                                                                            \
    "__set_byteorder__", (PyCFunction)cp_##name##_set_byteorder,               \
      METH_VARARGS | METH_KEYWORDS, (docs)                                     \
  }

#define _CpEndian_KwArgsGetByteorder(ret)                                      \
  static char* kwlist[] = { "byteorder", NULL };                               \
  PyObject* byteorder = NULL;                                                  \
  if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &byteorder)) {       \
    return ret;                                                                \
  }                                                                            \
  if (!CpEndian_Check(byteorder)) {                                            \
    PyErr_SetString(PyExc_TypeError, "byteorder must be an Endian object");    \
    return ret;                                                                \
  }

#define _CpEndian_ImplSetByteorder(typename, name, field)                      \
  static PyObject* cp_##name##_set_byteorder(                                  \
    typename* self, PyObject* args, PyObject* kw)                              \
  {                                                                            \
    _CpEndian_KwArgsGetByteorder(NULL);                                        \
    PyObject* ret = CpEndian_SetEndian(field, (CpEndianObject*)byteorder);     \
    if (!ret) {                                                                \
      return NULL;                                                             \
    }                                                                          \
    _Cp_SetObj(field, ret);                                                    \
    return Py_NewRef((PyObject*)self);                                         \
  }

#define _CACHED_STRING(state, attr, str, ret)                                  \
  if (((state)->attr = PyUnicode_InternFromString((str))) == NULL)             \
  return (ret)

#define CACHED_STRING_NULL(state, attr, str)                                   \
  _CACHED_STRING(state, attr, str, NULL)

// private module initializer and finalizer
#define _CpDef_ModFn(name)                                                     \
  int name##__mod_init(PyObject* m, _modulestate* state);                      \
  void name##__mod_clear(PyObject* m, _modulestate* state);                    \
  int name##__mod_types(void);

_CpDef_ModFn(cp_context) _CpDef_ModFn(cp_arch) _CpDef_ModFn(cp_option)

#undef _CpDef_ModFn

#endif // __CP_PRIVATE_H