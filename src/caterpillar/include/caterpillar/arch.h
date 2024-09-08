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
#ifndef CP_ARCH_H
#define CP_ARCH_H

#include "caterpillarapi.h"

/**
 * @brief Configuration class that represents an architecture.
 *
 * This class/struct will be used by pointer atoms to represent
 * an architecture with its pointer size.
 */
struct _archobj
{
  /// The name of the architecture
  PyObject_HEAD PyObject* name;
  /// The pointer size of the architecture
  int pointer_size;
};

/**
 * @brief Checks if the given object is an architecture object
 *
 * This macro will check the exact type of the object and return
 * 1 if it is of type `CpArchObject` and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an architecture object, 0 otherwise
 */
#define CpArch_CheckExact(op) Py_IS_TYPE((op), &CpArch_Type)

/**
 * @brief Checks if the given object is an architecture object
 *
 * This macro will check the type of the object and return
 * 1 if it is an architecture object and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an architecture object, 0 otherwise
 */
#define CpArch_Check(op) PyObject_TypeCheck((PyObject*)(op), &CpArch_Type)

/**
 * @brief Configuration class that represents endian configuration.
 */
struct _endianobj
{
  /// The human readable name of this endian
  PyObject_HEAD PyObject* name;
  /// struct format character
  char id;
};

/**
 * @brief Checks if the given object is an endian object
 *
 * This macro will check the exact type of the object and return
 * 1 if it is of type `CpEndianObject` and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an endian object, 0 otherwise
 */
#define CpEndian_CheckExact(op) Py_IS_TYPE((op), &CpEndian_Type)

/**
 * @brief Checks if the given object is an endian object
 *
 * This macro will check the type of the object and return
 * 1 if it is an endian object and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an endian object, 0 otherwise
 */
#define CpEndian_Check(op) PyObject_TypeCheck((PyObject*)(op), &CpEndian_Type)

/**
 * @brief Set the byteorder of the given object
 *
 * @param op the object to set
 * @param endian the new byteorder
 * @return 0 on success, -1 on error
 */
inline int
CpEndian_SetEndian(PyObject* op, CpEndianObject* endian)
{
  PyObject* attr = PyObject_GetAttrString(op, "__set_byteorder__");
  if (!attr) {
    return -1;
  }
  PyObject* ret = PyObject_CallOneArg(attr, (PyObject*)endian);
  if (!ret) {
    return -1;
  }
  Py_DECREF(ret);
  Py_DECREF(attr);
  return 0;
}

#define _CpEndian_ImplSetByteorder(name, field)                                \
  static PyObject* cp_##name##_set_byteorder(                                  \
    CpFloatAtomObject* self, PyObject* args, PyObject* kw)                     \
  {                                                                            \
    static char* kwlist[] = { "byteorder", NULL };                             \
    PyObject* byteorder = NULL;                                                \
    if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &byteorder)) {     \
      return NULL;                                                             \
    }                                                                          \
    if (!CpEndian_Check(byteorder)) {                                          \
      PyErr_SetString(PyExc_TypeError, "byteorder must be an Endian object");  \
      return NULL;                                                             \
    }                                                                          \
    field = CpEndian_IsLittleEndian((CpEndianObject*)byteorder,                \
                                    get_global_module_state());                \
    Py_RETURN_NONE;                                                            \
  }

#define _CpEndian_ImplSetByteorder_MethDef(name, docs)                         \
  {                                                                            \
    "__set_byteorder__", (PyCFunction)cp_##name##_set_byteorder, METH_VARARGS, \
      (docs)                                                                   \
  }

#endif