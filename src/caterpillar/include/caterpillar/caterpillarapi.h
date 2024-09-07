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
#ifndef CATERPILLAR_API_H
#define CATERPILLAR_API_H

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
struct _constatomobj;
typedef struct _constatomobj CpConstAtomObject;

#ifdef _CPMODULE

/*
Here, all publicly exposed types and functions are defined. These declarations
are then used and implemented in the internal API.
*/

extern PyModuleDef CpModule;
extern PyTypeObject CpCAtom_Type;
extern PyTypeObject CpArch_Type;
extern PyTypeObject CpEndian_Type;
extern PyTypeObject CpContext_Type;
extern PyTypeObject CpUnaryExpr_Type;
extern PyTypeObject CpBinaryExpr_Type;
extern PyTypeObject CpContextPath_Type;
extern PyTypeObject CpField_Type;
extern PyTypeObject CpFieldAtom_Type;
extern PyTypeObject CpFieldCAtom_Type;
extern PyTypeObject CpInvalidDefault_Type;
extern PyTypeObject CpDefaultOption_Type;
extern PyObject _CpInvalidDefault_Object;
extern PyObject _CpDefaultOption_Object;
extern PyTypeObject CpAtom_Type;
extern PyTypeObject CpOption_Type;
extern PyTypeObject CpState_Type;
extern PyTypeObject CpLayer_Type;
extern PyTypeObject CpStructFieldInfo_Type;
extern PyTypeObject CpStruct_Type;
extern PyTypeObject CpFloatAtom_Type;
extern PyTypeObject CpIntAtom_Type;
extern PyTypeObject CpBoolAtom_Type;
extern PyTypeObject CpCharAtom_Type;
extern PyTypeObject CpPaddingAtom_Type;
extern PyTypeObject CpStringAtom_Type;
extern PyTypeObject CpConstAtom_Type;
int CpEndian_IsLittleEndian(CpEndianObject* endian, _modulestate* mod);
CpContextObject* CpContext_New(void);
CpUnaryExprObject* CpUnaryExpr_New(int op, PyObject* value);
CpBinaryExprObject* CpBinaryExpr_New(int op, PyObject* left, PyObject* right);
CpContextPathObject* CpContextPath_New(PyObject* path);
CpContextPathObject* CpContextPath_FromString(const char* path);
CpFieldObject* CpField_New(PyObject* atom);
int CpField_HasCondition(CpFieldObject* self);
int CpField_IsEnabled(CpFieldObject* self, PyObject* context);
Py_ssize_t CpField_GetOffset(CpFieldObject* self, PyObject* context);
PyObject* CpField_EvalSwitch(CpFieldObject* self, PyObject* op, PyObject* context);
PyObject* CpField_GetLength(CpFieldObject* self, PyObject* context);
PyObject* CpTypeOf(PyObject* op);
PyObject* CpTypeOf_Field(CpFieldObject* op);
PyObject* CpTypeOf_Common(PyObject* op);
int CpPack(PyObject* op, PyObject* atom, PyObject* io, PyObject* globals);
int CpPack_Field(PyObject* op, CpFieldObject* field, CpLayerObject* layer);
int CpPack_Common(PyObject* op, PyObject* atom, CpLayerObject* layer);
int CpPack_Struct(PyObject* op, CpStructObject* struct_, CpLayerObject* layer);
int _Cp_Pack(PyObject* op, PyObject* atom, CpLayerObject* layer);
int _CpPack_EvalLength(CpLayerObject* layer,PyObject* length,Py_ssize_t size,bool* greedy,Py_ssize_t* dstLength);
PyObject* CpSizeOf(PyObject* op, PyObject* globals);
PyObject* CpSizeOf_Field(CpFieldObject* field, CpLayerObject* layer);
PyObject* CpSizeOf_Struct(CpStructObject* struct_, CpLayerObject* layer);
PyObject* CpSizeOf_Common(PyObject* op, CpLayerObject* layer);
PyObject* _Cp_SizeOf(PyObject* op, CpLayerObject* layer);
PyObject* CpUnpack(PyObject* atom, PyObject* io, PyObject* globals);
PyObject* CpUnpack_Field(CpFieldObject* field, CpLayerObject* layer);
PyObject* CpUnpack_Common(PyObject* op, CpLayerObject* layer);
PyObject* CpUnpack_Struct(CpStructObject* struct_, CpLayerObject* layer);
PyObject* _Cp_Unpack(PyObject* atom, CpLayerObject* layer);
int _CpUnpack_EvalLength(CpLayerObject* layer,PyObject* length,bool* seq_greedy,Py_ssize_t* seq_length);
PyObject* CpUnpack_CAtom(CpCAtomObject* catom, CpLayerObject* layer);
int CpPack_CAtom(PyObject* op, CpCAtomObject* catom, CpLayerObject* layer);
PyObject* CpSizeOf_CAtom(CpCAtomObject* catom, CpLayerObject* layer);
PyObject * CpTypeOf_CAtom(CpCAtomObject* op);
CpStateObject* CpState_New(PyObject* io);
PyObject* CpState_Tell(CpStateObject* self);
PyObject* CpState_Seek(CpStateObject* self, PyObject* offset, int whence);
PyObject* CpState_Read(CpStateObject* self, Py_ssize_t size);
PyObject* CpState_ReadFully(CpStateObject* self);
PyObject* CpState_Write(CpStateObject* self, PyObject* value);
int CpState_SetGlobals(CpStateObject* self, PyObject* globals);
CpLayerObject* CpLayer_New(CpStateObject* state, CpLayerObject* parent);
int CpLayer_Invalidate(CpLayerObject* self);
int CpLayer_SetSequence(CpLayerObject* self,PyObject* sequence,Py_ssize_t length,int8_t greedy);
CpStructFieldInfoObject* CpStructFieldInfo_New(CpFieldObject* field);
int CpStruct_AddFieldInfo(CpStructObject* o, CpStructFieldInfoObject* info);
int CpStruct_AddField(CpStructObject* o, CpFieldObject* field, int exclude);
CpStructObject* CpStruct_New(PyObject* model);
PyObject* CpStruct_GetAnnotations(CpStructObject* o, int eval);
int CpStruct_ReplaceType(CpStructObject* o, PyObject* name, PyObject* type);
int CpStruct_HasOption(CpStructObject* o, PyObject* option);
int CpStructModel_Check(PyObject* model, _modulestate* state);
PyObject* CpStructModel_GetStruct(PyObject* model, _modulestate* state);
int CpIntAtom_Pack(CpIntAtomObject* self, PyObject* op, CpLayerObject* layer);
PyObject* CpIntAtom_Unpack(CpIntAtomObject* self, CpLayerObject* layer);
int CpFloatAtom_Pack(CpFloatAtomObject* self, PyObject* value, CpLayerObject* layer);
PyObject* CpFloatAtom_Unpack(CpFloatAtomObject* self, CpLayerObject* layer);
int CpBoolAtom_Pack(CpBoolAtomObject* self, PyObject* value, CpLayerObject* layer);
PyObject* CpBoolAtom_Unpack(CpBoolAtomObject* self, CpLayerObject* layer);
int CpCharAtom_Pack(CpCharAtomObject* self, PyObject* value, CpLayerObject* layer);
PyObject* CpCharAtom_Unpack(CpCharAtomObject* self, CpLayerObject* layer);
int CpPaddingAtom_Pack(CpPaddingAtomObject* self,PyObject* value,CpLayerObject* layer);
int CpPaddingAtom_PackMany(CpPaddingAtomObject* self,PyObject* value,CpLayerObject* layer);
PyObject* CpPaddingAtom_Unpack(CpPaddingAtomObject* self, CpLayerObject* layer);
PyObject* CpPaddingAtom_UnpackMany(CpPaddingAtomObject* self, CpLayerObject* layer);
int CpStringAtom_Pack(CpStringAtomObject* self,PyObject* value,CpLayerObject* layer);
PyObject* CpStringAtom_Unpack(CpStringAtomObject* self, CpLayerObject* layer);
int CpConstAtom_Pack(CpConstAtomObject* self, PyObject* value, CpLayerObject* layer);
PyObject* CpConstAtom_Unpack(CpConstAtomObject* self, CpLayerObject* layer);

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
#define CpConstAtom_Type (*(PyTypeObject *)Cp_API[27])
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
#define CpIntAtom_Pack (*((int (*)(CpIntAtomObject* self, PyObject* op, CpLayerObject* layer)))Cp_API[120])
#define CpIntAtom_Unpack (*((PyObject* (*)(CpIntAtomObject* self, CpLayerObject* layer)))Cp_API[121])
#define CpFloatAtom_Pack (*((int (*)(CpFloatAtomObject* self, PyObject* value, CpLayerObject* layer)))Cp_API[122])
#define CpFloatAtom_Unpack (*((PyObject* (*)(CpFloatAtomObject* self, CpLayerObject* layer)))Cp_API[123])
#define CpBoolAtom_Pack (*((int (*)(CpBoolAtomObject* self, PyObject* value, CpLayerObject* layer)))Cp_API[124])
#define CpBoolAtom_Unpack (*((PyObject* (*)(CpBoolAtomObject* self, CpLayerObject* layer)))Cp_API[125])
#define CpCharAtom_Pack (*((int (*)(CpCharAtomObject* self, PyObject* value, CpLayerObject* layer)))Cp_API[126])
#define CpCharAtom_Unpack (*((PyObject* (*)(CpCharAtomObject* self, CpLayerObject* layer)))Cp_API[127])
#define CpPaddingAtom_Pack (*((int (*)(CpPaddingAtomObject* self,PyObject* value,CpLayerObject* layer)))Cp_API[128])
#define CpPaddingAtom_PackMany (*((int (*)(CpPaddingAtomObject* self,PyObject* value,CpLayerObject* layer)))Cp_API[129])
#define CpPaddingAtom_Unpack (*((PyObject* (*)(CpPaddingAtomObject* self, CpLayerObject* layer)))Cp_API[130])
#define CpPaddingAtom_UnpackMany (*((PyObject* (*)(CpPaddingAtomObject* self, CpLayerObject* layer)))Cp_API[131])
#define CpStringAtom_Pack (*((int (*)(CpStringAtomObject* self,PyObject* value,CpLayerObject* layer)))Cp_API[132])
#define CpStringAtom_Unpack (*((PyObject* (*)(CpStringAtomObject* self, CpLayerObject* layer)))Cp_API[133])
#define CpConstAtom_Pack (*((int (*)(CpConstAtomObject* self, PyObject* value, CpLayerObject* layer)))Cp_API[134])
#define CpConstAtom_Unpack (*((PyObject* (*)(CpConstAtomObject* self, CpLayerObject* layer)))Cp_API[135])

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