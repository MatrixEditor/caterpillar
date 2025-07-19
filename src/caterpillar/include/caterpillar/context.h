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
#ifndef CP_CONTEXT_H
#define CP_CONTEXT_H

/* Caterpillar Context and ContextPath C implementation */
#include "caterpillar/caterpillarapi.h"

/*context*/

/**
 * @brief C implementation of the Python equivalent.
 *
 * Represents a context object with attribute-style access, which also conforms
 * to the context protocol.
 */
struct _contextobj
{
  /// This object is essentially a dict object with some extra
  /// methods to conform to the Context protocol. Therefore, this
  /// object can be casted into a dictionary directly.
  PyDictObject m_dict;
};

/**
 * @brief Checks if the given object is an context object
 *
 * This macro will check the exact type of the object and return
 * 1 if it is of type `CpContext` and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an context object, 0 otherwise
 */
#define CpContext_CheckExact(op) Py_IS_TYPE((op), &CpContext_Type)

/**
 * @brief Checks if the given object is an context object
 *
 * This macro will check the type of the object and return
 * 1 if it is an context object and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an context object, 0 otherwise
 */
#define CpContext_Check(op) PyObject_TypeCheck((op), &CpContext_Type)

inline static PyObject*
CpContext_GetDict(PyObject* obj)
{
  return Py_NewRef(&_Cp_CAST(CpContextObject*, obj)->m_dict);
}

inline static PyObject*
CpContext_New()
{
  return CpObject_CreateNoArgs(&CpContext_Type);
}

#endif