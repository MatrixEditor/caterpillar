/*!! AUTO-GENERATED FILE - DO NOT MODIFY !!*/
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
#ifndef CATERPILLAR_H
#define CATERPILLAR_H

// TODO: remove import
#include "macros.h"

#ifdef _CPMODULE

/* struct and typedefs */

struct _modulestate;
typedef struct _modulestate _modulestate;
struct _endianobj;
typedef struct _endianobj CpEndianObject;
struct _archobj;
typedef struct _archobj CpArchObject;
struct _atomobj;
typedef struct _atomobj CpAtomObject;
struct _catomobj;
typedef struct _catomobj CpCAtomObject;
struct _contextobj;
typedef struct _contextobj CpContextObject;
struct _unaryexpr;
typedef struct _unaryexpr CpUnaryExprObject;
struct _binaryexpr;
typedef struct _binaryexpr CpBinaryExprObject;
struct _contextpath;
typedef struct _contextpath CpContextPathObject;
struct _fieldobj;
typedef struct _fieldobj CpFieldObject;
struct _fieldatomobj;
typedef struct _fieldatomobj CpFieldAtomObject;
struct _fieldcatomobj;
typedef struct _fieldcatomobj CpFieldCAtomObject;
struct _option;
typedef struct _option CpOptionObject;
struct _stateobj;
typedef struct _stateobj CpStateObject;
struct _layerobj;
typedef struct _layerobj CpLayerObject;
struct CpStructFieldInfo;
typedef struct CpStructFieldInfo CpStructFieldInfoObject;
struct _structobj;
typedef struct _structobj CpStructObject;
struct _floatatomobj;
typedef struct _floatatomobj CpFloatAtomObject;
struct _intatomobj;
typedef struct _intatomobj CpIntAtomObject;
struct _boolatomobj;
typedef struct _boolatomobj CpBoolAtomObject;
struct _charatomobj;
typedef struct _charatomobj CpCharAtomObject;
struct _paddingatomobj;
typedef struct _paddingatomobj CpPaddingAtomObject;
struct _stringatomobj;
typedef struct _stringatomobj CpStringAtomObject;

/*
Here, all publicly exposed types and functions are defined. These declarations
are then used and implemented in the internal API.
*/

PyAPI_DATA(PyModuleDef) CpModule;
PyAPI_DATA(PyTypeObject) CpCAtom_Type;
PyAPI_DATA(PyTypeObject) CpArch_Type;
PyAPI_DATA(PyTypeObject) CpEndian_Type;
PyAPI_DATA(PyTypeObject) CpContext_Type;
PyAPI_DATA(PyTypeObject) CpUnaryExpr_Type;
PyAPI_DATA(PyTypeObject) CpBinaryExpr_Type;
PyAPI_DATA(PyTypeObject) CpContextPath_Type;
PyAPI_DATA(PyTypeObject) CpField_Type;
PyAPI_DATA(PyTypeObject) CpFieldAtom_Type;
PyAPI_DATA(PyTypeObject) CpFieldCAtom_Type;
PyAPI_DATA(PyTypeObject) CpInvalidDefault_Type;
PyAPI_DATA(PyTypeObject) CpDefaultOption_Type;
PyAPI_DATA(PyObject) _CpInvalidDefault_Object;
PyAPI_DATA(PyObject) _CpDefaultOption_Object;
PyAPI_DATA(PyTypeObject) CpAtom_Type;
PyAPI_DATA(PyTypeObject) CpOption_Type;
PyAPI_DATA(PyTypeObject) CpState_Type;
PyAPI_DATA(PyTypeObject) CpLayer_Type;
PyAPI_DATA(PyTypeObject) CpStructFieldInfo_Type;
PyAPI_DATA(PyTypeObject) CpStruct_Type;
PyAPI_DATA(PyTypeObject) CpFloatAtom_Type;
PyAPI_DATA(PyTypeObject) CpIntAtom_Type;
PyAPI_DATA(PyTypeObject) CpBoolAtom_Type;
PyAPI_DATA(PyTypeObject) CpCharAtom_Type;
PyAPI_DATA(PyTypeObject) CpPaddingAtom_Type;
PyAPI_DATA(PyTypeObject) CpStringAtom_Type;
PyAPI_FUNC(int) CpEndian_IsLittleEndian(CpEndianObject* endian, _modulestate* mod);

#else

/*
All external functions and types are defined here using the same name but as
macro. They all point to the exposed API table storing references to all
internal API functions and types. Their indices are static and defined in
caterpillar_api.py
*/
#define CpModule (*(PyModuleDef *)Cp_API[0])
#define CpCAtom_Type (*(PyTypeObject *)Cp_API[1])
#define CpArch_Type (*(PyTypeObject *)Cp_API[2])
#define CpEndian_Type (*(PyTypeObject *)Cp_API[3])
#define CpContext_Type (*(PyTypeObject *)Cp_API[4])
#define CpUnaryExpr_Type (*(PyTypeObject *)Cp_API[5])
#define CpBinaryExpr_Type (*(PyTypeObject *)Cp_API[6])
#define CpContextPath_Type (*(PyTypeObject *)Cp_API[7])
#define CpField_Type (*(PyTypeObject *)Cp_API[8])
#define CpFieldAtom_Type (*(PyTypeObject *)Cp_API[9])
#define CpFieldCAtom_Type (*(PyTypeObject *)Cp_API[10])
#define CpInvalidDefault_Type (*(PyTypeObject *)Cp_API[11])
#define CpDefaultOption_Type (*(PyTypeObject *)Cp_API[12])
#define _CpInvalidDefault_Object (*(PyObject *)Cp_API[13])
#define _CpDefaultOption_Object (*(PyObject *)Cp_API[14])
#define CpAtom_Type (*(PyTypeObject *)Cp_API[15])
#define CpOption_Type (*(PyTypeObject *)Cp_API[16])
#define CpState_Type (*(PyTypeObject *)Cp_API[17])
#define CpLayer_Type (*(PyTypeObject *)Cp_API[18])
#define CpStructFieldInfo_Type (*(PyTypeObject *)Cp_API[19])
#define CpStruct_Type (*(PyTypeObject *)Cp_API[20])
#define CpFloatAtom_Type (*(PyTypeObject *)Cp_API[21])
#define CpIntAtom_Type (*(PyTypeObject *)Cp_API[22])
#define CpBoolAtom_Type (*(PyTypeObject *)Cp_API[23])
#define CpCharAtom_Type (*(PyTypeObject *)Cp_API[24])
#define CpPaddingAtom_Type (*(PyTypeObject *)Cp_API[25])
#define CpStringAtom_Type (*(PyTypeObject *)Cp_API[26])
#define CpEndian_IsLittleEndian (*((int (*)(CpEndianObject* endian, _modulestate* mod)))Cp_API[30])

/**
 * @brief Public C API for extension modules as reference table
 *
 * All entries in this table point either to internal API functions or to
 * internal API types. Rerved entries are NULL pointers.
 *
 * You usually don't need to modify this table or interact with it directly.
 * All generated macros will implement the interaction for you.
 */
static void** Cp_API = NULL;

/**
 * @brief Imports the Caterpillar C API and prepares the internal API table
 *
 * @return int 0 on success, -1 on failure
 */
static inline int
_import_caterpillar(void)
{
  PyObject* caterpillar = PyImport_ImportModule("caterpillar._C");
  if (caterpillar == NULL)
    return -1;

  PyObject* c_api = PyObject_GetAttrString(caterpillar, "_C_API");
  if (c_api == NULL) {
    PyErr_SetString(PyExc_AttributeError, "_C_API not found");
    return -1;
  }

  if (!PyCapsule_CheckExact(c_api)) {
    PyErr_SetString(PyExc_TypeError, "_C_API is not a capsule");
    Py_DECREF(c_api);
    return -1;
  }

  Cp_API = (void**)PyCapsule_GetPointer(c_api, NULL);
  Py_DECREF(c_api);
  if (Cp_API == NULL) {
    PyErr_SetString(PyExc_AttributeError, "_C_API is NULL pointer");
    return -1;
  }
  return 0;
}

/**
 * @brief Imports the Caterpillar C API and prepares the internal API table
 *
 * @param ret the return value
 * @return the given return value on failure
 */
#define __import_caterpillar__(ret)                                            \
  do {                                                                         \
    if (_import_caterpillar() < 0) {                                           \
      PyErr_Print();                                                           \
      PyErr_SetString(PyExc_ImportError, "Failed to import caterpillar");      \
      return (ret);                                                            \
    }                                                                          \
  } while (0);

/**
 * @brief Imports the Caterpillar C API and prepares the internal API table
 *
 * @return `NULL` on failure, does nothing on success
 */
#define import_caterpillar() __import_caterpillar__(NULL)

/**
 * @brief Public function to programmatically import the C API
 *
 * @return int 0 on success, -1 on failure
 */
static inline int
Cp_ImportCpAPI(void)
{
  if (Cp_API == NULL) {
    __import_caterpillar__(-1);
  }
  return 0;
}

#endif
#endif