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
#ifndef CP_MACROS_H
#define CP_MACROS_H

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif

#include <Python.h>

#define PY_3_13_PLUS (PY_VERSION_HEX >= 0x030d0000)
#define PY_3_14_PLUS (PY_VERSION_HEX >= 0x030e0000)

// without trailing ;
#define PY_OBJECT_HEAD PyObject ob_base

#define _Cp_CAST(type, obj) ((type)(obj))

/**
 * @brief Creates an object of the given type and returns it.
 *
 * @returns *NULL* if an error occurs.
 *
 */
#define CpObject_Create(type, format, ...)                                     \
  (PyObject_CallFunction((PyObject*)(type), format, __VA_ARGS__))

/**
 * @brief Creates an object of the given type and returns it.
 *
 * @param type the type of the object to create
 * @returns *NULL* if an error occurs.
 */
#define CpObject_CreateNoArgs(type) (PyObject_CallNoArgs((PyObject*)(type)))

/**
 * @brief Creates an object of the given type and returns it.
 *
 * @param type the type of the object to create
 * @param arg the argument to pass to the constructor
 * @returns *NULL* if an error occurs.
 */
#define CpObject_CreateOneArg(type, arg)                                       \
  (PyObject_CallOneArg(((PyObject*)(type)), (arg)))

#endif