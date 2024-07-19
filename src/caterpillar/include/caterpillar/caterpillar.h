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

#include <stdbool.h>
#include <stdint.h>

// TODO: remove import
#include "macros.h"


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

#ifdef _CPMODULE

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
PyAPI_FUNC(CpContextObject*) CpContext_New(void);
PyAPI_FUNC(CpUnaryExprObject*) CpUnaryExpr_New(int op, PyObject* value);
PyAPI_FUNC(CpBinaryExprObject*) CpBinaryExpr_New(int op, PyObject* left, PyObject* right);
PyAPI_FUNC(CpContextPathObject*) CpContextPath_New(PyObject* path);
PyAPI_FUNC(CpContextPathObject*) CpContextPath_FromString(const char* path);
PyAPI_FUNC(CpFieldObject*) CpField_New(PyObject* atom);
PyAPI_FUNC(int) CpField_HasCondition(CpFieldObject* self);
PyAPI_FUNC(int) CpField_IsEnabled(CpFieldObject* self, PyObject* context);
PyAPI_FUNC(Py_ssize_t) CpField_GetOffset(CpFieldObject* self, PyObject* context);
PyAPI_FUNC(PyObject*) CpField_EvalSwitch(CpFieldObject* self, PyObject* op, PyObject* context);
PyAPI_FUNC(PyObject*) CpField_GetLength(CpFieldObject* self, PyObject* context);
PyAPI_FUNC(PyObject*) CpTypeOf(PyObject* op);
PyAPI_FUNC(PyObject*) CpTypeOf_Field(CpFieldObject* op);
PyAPI_FUNC(PyObject*) CpTypeOf_Common(PyObject* op);
PyAPI_FUNC(int) CpPack(PyObject* op, PyObject* atom, PyObject* io, PyObject* globals);
PyAPI_FUNC(int) CpPack_Field(PyObject* op, CpFieldObject* field, CpLayerObject* layer);
PyAPI_FUNC(int) CpPack_Common(PyObject* op, PyObject* atom, CpLayerObject* layer);
PyAPI_FUNC(int) CpPack_Struct(PyObject* op, CpStructObject* struct_, CpLayerObject* layer);
PyAPI_FUNC(int) _Cp_Pack(PyObject* op, PyObject* atom, CpLayerObject* layer);
PyAPI_FUNC(int) _CpPack_EvalLength(CpLayerObject* layer,PyObject* length,Py_ssize_t size,bool* greedy,Py_ssize_t* dstLength);
PyAPI_FUNC(PyObject*) CpSizeOf(PyObject* op, PyObject* globals);
PyAPI_FUNC(PyObject*) CpSizeOf_Field(CpFieldObject* field, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) CpSizeOf_Struct(CpStructObject* struct_, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) CpSizeOf_Common(PyObject* op, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) _Cp_SizeOf(PyObject* op, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) CpUnpack(PyObject* atom, PyObject* io, PyObject* globals);
PyAPI_FUNC(PyObject*) CpUnpack_Field(CpFieldObject* field, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) CpUnpack_Common(PyObject* op, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) CpUnpack_Struct(CpStructObject* struct_, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) _Cp_Unpack(PyObject* atom, CpLayerObject* layer);
PyAPI_FUNC(int) _CpUnpack_EvalLength(CpLayerObject* layer,PyObject* length,bool* seq_greedy,Py_ssize_t* seq_length);
PyAPI_FUNC(PyObject*) CpUnpack_CAtom(CpCAtomObject* catom, CpLayerObject* layer);
PyAPI_FUNC(int) CpPack_CAtom(PyObject* op, CpCAtomObject* catom, CpLayerObject* layer);
PyAPI_FUNC(PyObject*) CpSizeOf_CAtom(CpCAtomObject* catom, CpLayerObject* layer);
PyAPI_FUNC(PyObject *) CpTypeOf_CAtom(CpCAtomObject* op);
PyAPI_FUNC(CpStateObject*) CpState_New(PyObject* io);
PyAPI_FUNC(PyObject*) CpState_Tell(CpStateObject* self);
PyAPI_FUNC(PyObject*) CpState_Seek(CpStateObject* self, PyObject* offset, int whence);
PyAPI_FUNC(PyObject*) CpState_Read(CpStateObject* self, Py_ssize_t size);
PyAPI_FUNC(PyObject*) CpState_ReadFully(CpStateObject* self);
PyAPI_FUNC(PyObject*) CpState_Write(CpStateObject* self, PyObject* value);
PyAPI_FUNC(int) CpState_SetGlobals(CpStateObject* self, PyObject* globals);
PyAPI_FUNC(CpLayerObject*) CpLayer_New(CpStateObject* state, CpLayerObject* parent);
PyAPI_FUNC(int) CpLayer_Invalidate(CpLayerObject* self);
PyAPI_FUNC(int) CpLayer_SetSequence(CpLayerObject* self,PyObject* sequence,Py_ssize_t length,int8_t greedy);
PyAPI_FUNC(CpStructFieldInfoObject*) CpStructFieldInfo_New(CpFieldObject* field);
PyAPI_FUNC(int) CpStruct_AddFieldInfo(CpStructObject* o, CpStructFieldInfoObject* info);
PyAPI_FUNC(int) CpStruct_AddField(CpStructObject* o, CpFieldObject* field, int exclude);
PyAPI_FUNC(CpStructObject*) CpStruct_New(PyObject* model);
PyAPI_FUNC(PyObject*) CpStruct_GetAnnotations(CpStructObject* o, int eval);
PyAPI_FUNC(int) CpStruct_ReplaceType(CpStructObject* o, PyObject* name, PyObject* type);
PyAPI_FUNC(int) CpStruct_HasOption(CpStructObject* o, PyObject* option);
PyAPI_FUNC(int) CpStructModel_Check(PyObject* model, _modulestate* state);
PyAPI_FUNC(PyObject*) CpStructModel_GetStruct(PyObject* model, _modulestate* state);

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
#define CpEndian_IsLittleEndian (*((int (*)(CpEndianObject* endian, _modulestate* mod)))Cp_API[50])
#define CpContext_New (*((CpContextObject* (*)(void)))Cp_API[53])
#define CpUnaryExpr_New (*((CpUnaryExprObject* (*)(int op, PyObject* value)))Cp_API[54])
#define CpBinaryExpr_New (*((CpBinaryExprObject* (*)(int op, PyObject* left, PyObject* right)))Cp_API[55])
#define CpContextPath_New (*((CpContextPathObject* (*)(PyObject* path)))Cp_API[56])
#define CpContextPath_FromString (*((CpContextPathObject* (*)(const char* path)))Cp_API[57])
#define CpField_New (*((CpFieldObject* (*)(PyObject* atom)))Cp_API[58])
#define CpField_HasCondition (*((int (*)(CpFieldObject* self)))Cp_API[59])
#define CpField_IsEnabled (*((int (*)(CpFieldObject* self, PyObject* context)))Cp_API[60])
#define CpField_GetOffset (*((Py_ssize_t (*)(CpFieldObject* self, PyObject* context)))Cp_API[61])
#define CpField_EvalSwitch (*((PyObject* (*)(CpFieldObject* self, PyObject* op, PyObject* context)))Cp_API[62])
#define CpField_GetLength (*((PyObject* (*)(CpFieldObject* self, PyObject* context)))Cp_API[63])
#define CpTypeOf (*((PyObject* (*)(PyObject* op)))Cp_API[64])
#define CpTypeOf_Field (*((PyObject* (*)(CpFieldObject* op)))Cp_API[65])
#define CpTypeOf_Common (*((PyObject* (*)(PyObject* op)))Cp_API[66])
#define CpPack (*((int (*)(PyObject* op, PyObject* atom, PyObject* io, PyObject* globals)))Cp_API[67])
#define CpPack_Field (*((int (*)(PyObject* op, CpFieldObject* field, CpLayerObject* layer)))Cp_API[68])
#define CpPack_Common (*((int (*)(PyObject* op, PyObject* atom, CpLayerObject* layer)))Cp_API[69])
#define CpPack_Struct (*((int (*)(PyObject* op, CpStructObject* struct_, CpLayerObject* layer)))Cp_API[70])
#define _Cp_Pack (*((int (*)(PyObject* op, PyObject* atom, CpLayerObject* layer)))Cp_API[71])
#define _CpPack_EvalLength (*((int (*)(CpLayerObject* layer,PyObject* length,Py_ssize_t size,bool* greedy,Py_ssize_t* dstLength)))Cp_API[72])
#define CpSizeOf (*((PyObject* (*)(PyObject* op, PyObject* globals)))Cp_API[73])
#define CpSizeOf_Field (*((PyObject* (*)(CpFieldObject* field, CpLayerObject* layer)))Cp_API[74])
#define CpSizeOf_Struct (*((PyObject* (*)(CpStructObject* struct_, CpLayerObject* layer)))Cp_API[75])
#define CpSizeOf_Common (*((PyObject* (*)(PyObject* op, CpLayerObject* layer)))Cp_API[76])
#define _Cp_SizeOf (*((PyObject* (*)(PyObject* op, CpLayerObject* layer)))Cp_API[77])
#define CpUnpack (*((PyObject* (*)(PyObject* atom, PyObject* io, PyObject* globals)))Cp_API[78])
#define CpUnpack_Field (*((PyObject* (*)(CpFieldObject* field, CpLayerObject* layer)))Cp_API[79])
#define CpUnpack_Common (*((PyObject* (*)(PyObject* op, CpLayerObject* layer)))Cp_API[80])
#define CpUnpack_Struct (*((PyObject* (*)(CpStructObject* struct_, CpLayerObject* layer)))Cp_API[81])
#define _Cp_Unpack (*((PyObject* (*)(PyObject* atom, CpLayerObject* layer)))Cp_API[82])
#define _CpUnpack_EvalLength (*((int (*)(CpLayerObject* layer,PyObject* length,bool* seq_greedy,Py_ssize_t* seq_length)))Cp_API[83])
#define CpUnpack_CAtom (*((PyObject* (*)(CpCAtomObject* catom, CpLayerObject* layer)))Cp_API[84])
#define CpPack_CAtom (*((int (*)(PyObject* op, CpCAtomObject* catom, CpLayerObject* layer)))Cp_API[85])
#define CpSizeOf_CAtom (*((PyObject* (*)(CpCAtomObject* catom, CpLayerObject* layer)))Cp_API[86])
#define CpTypeOf_CAtom (*((PyObject * (*)(CpCAtomObject* op)))Cp_API[87])
#define CpState_New (*((CpStateObject* (*)(PyObject* io)))Cp_API[88])
#define CpState_Tell (*((PyObject* (*)(CpStateObject* self)))Cp_API[89])
#define CpState_Seek (*((PyObject* (*)(CpStateObject* self, PyObject* offset, int whence)))Cp_API[90])
#define CpState_Read (*((PyObject* (*)(CpStateObject* self, Py_ssize_t size)))Cp_API[91])
#define CpState_ReadFully (*((PyObject* (*)(CpStateObject* self)))Cp_API[92])
#define CpState_Write (*((PyObject* (*)(CpStateObject* self, PyObject* value)))Cp_API[93])
#define CpState_SetGlobals (*((int (*)(CpStateObject* self, PyObject* globals)))Cp_API[94])
#define CpLayer_New (*((CpLayerObject* (*)(CpStateObject* state, CpLayerObject* parent)))Cp_API[95])
#define CpLayer_Invalidate (*((int (*)(CpLayerObject* self)))Cp_API[96])
#define CpLayer_SetSequence (*((int (*)(CpLayerObject* self,PyObject* sequence,Py_ssize_t length,int8_t greedy)))Cp_API[97])
#define CpStructFieldInfo_New (*((CpStructFieldInfoObject* (*)(CpFieldObject* field)))Cp_API[98])
#define CpStruct_AddFieldInfo (*((int (*)(CpStructObject* o, CpStructFieldInfoObject* info)))Cp_API[99])
#define CpStruct_AddField (*((int (*)(CpStructObject* o, CpFieldObject* field, int exclude)))Cp_API[100])
#define CpStruct_New (*((CpStructObject* (*)(PyObject* model)))Cp_API[101])
#define CpStruct_GetAnnotations (*((PyObject* (*)(CpStructObject* o, int eval)))Cp_API[102])
#define CpStruct_ReplaceType (*((int (*)(CpStructObject* o, PyObject* name, PyObject* type)))Cp_API[103])
#define CpStruct_HasOption (*((int (*)(CpStructObject* o, PyObject* option)))Cp_API[104])
#define CpStructModel_Check (*((int (*)(PyObject* model, _modulestate* state)))Cp_API[105])
#define CpStructModel_GetStruct (*((PyObject* (*)(PyObject* model, _modulestate* state)))Cp_API[106])

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