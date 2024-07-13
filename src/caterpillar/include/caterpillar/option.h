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
#ifndef CP_OPTION_H
#define CP_OPTION_H

#include "caterpillar.h"

/**
 * @brief Simple option struct that stores a name and a value.
 */
struct _option
{
  /// Name of the option
  PyObject_HEAD PyObject* name;
  /// Value of the option
  PyObject* value;
};

/**
 * @brief Checks if the given object is an option
 *
 * This macro will check the type of the object and return
 * 1 if it is an option and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an option, 0 otherwise
 */
#define CpOption_Check(op) PyObject_TypeCheck((op), &CpOption_Type)

/**
 * @brief Checks if the given object is an option
 *
 * This macro will check the exact type of the object and return
 * 1 if it is of type `CpOptionObject` and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an option, 0 otherwise
 */
#define CpOption_CheckExact(op) Py_TYPE(op) == &CpOption_Type

#endif