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
#ifndef CP_OPTION_H
#define CP_OPTION_H

#include "caterpillarapi.h"

/**
 * @brief Represents a simple option object with a name and a value.
 *
 * The `_optionobj` struct stores an option's name and its corresponding
 * value. This structure is used to encapsulate key-value configuration
 * pairs or settings.
 */
struct _optionobj
{

  PY_OBJECT_HEAD;

  /// Name of the option
  PyObject* name;
  Py_hash_t nameHash;

  /// Value of the option
  PyObject* value;
};

/**
 * @brief Check if an object is an instance of `CpOptionObject` or its
 * subclasses.
 *
 * Evaluates whether the specified Python object is an instance of
 * `CpOptionObject` or any of its subclasses. Returns 1 if true, 0 otherwise.
 *
 * @param op Python object to check.
 * @return 1 if the object is an instance of `CpOptionObject`; 0 otherwise.
 */
#define CpOption_Check(op) PyObject_TypeCheck((op), &CpOption_Type)

/**
 * @brief Check if an object is exactly of type `CpOptionObject`.
 *
 * Evaluates whether the specified Python object is an exact instance
 * of `CpOptionObject`. Returns 1 if true, 0 otherwise.
 *
 * @param op Python object to check.
 * @return 1 if the object is exactly a `CpOptionObject`; 0 otherwise.
 */
#define CpOption_CheckExact(op) Py_IS_TYPE(op, &CpOption_Type)

/**
 * @brief Create a new `CpOptionObject` instance.
 *
 * Constructs a new option object with the specified name. The initial
 * value is set separately using `CpOption_SetValue`.
 *
 * @param name Name of the option.
 * @return A new `CpOptionObject` instance on success; NULL on failure.
 */
static inline PyObject*
CpOption_New(PyObject* name)
{
  return CpObject_CreateOneArg(&CpOption_Type, name);
}

/**
 * @brief Set the value of an option object.
 *
 * Updates the value associated with the specified option object.
 * Both the option and value must be valid Python objects.
 *
 * @param option A valid `CpOptionObject` instance.
 * @param value New value to associate with the option.
 * @return 0 on success; -1 on failure.
 */
static inline int
CpOption_SetValue(PyObject* option, PyObject* value)
{
  if (!option || !value) {
    PyErr_SetString(PyExc_ValueError, "Option or value is NULL!");
    return -1;
  }

  Py_XSETREF(_Cp_CAST(CpOptionObject*, option)->value, Py_NewRef(value));
  return 0;
}

/**
 * @brief Retrieve the value of an option object.
 *
 * Returns a new reference to the value associated with the specified
 * option object.
 *
 * @param option A valid `CpOptionObject` instance.
 * @return New reference to the value; NULL if the option is invalid.
 */
static inline PyObject*
CpOption_GetValue(PyObject* option)
{
  if (!option) {
    PyErr_SetString(PyExc_ValueError,
                    "Option is NULL when fetching option value!");
    return NULL;
  }
  return Py_NewRef(_Cp_CAST(CpOptionObject*, option)->value);
}

/**
 * @brief Retrieve the name of an option object.
 *
 * Returns a new reference to the name associated with the specified
 * option object.
 *
 * @param option A valid `CpOptionObject` instance.
 * @return New reference to the name; NULL if the option is invalid.
 */
static inline PyObject*
CpOption_GetName(PyObject* option)
{
  if (!option) {
    PyErr_SetString(PyExc_ValueError,
                    "Option is NULL when fetching option name!");
    return NULL;
  }
  return Py_NewRef(_Cp_CAST(CpOptionObject*, option)->name);
}

#endif