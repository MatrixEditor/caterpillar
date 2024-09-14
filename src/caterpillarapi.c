/* These pointers will be stored in the C-object for use in other
    extension modules
*/

void *Cp_API[] = {
    (void *) &CpModule,
    (void *) &CpAtom_Type,
    (void *) &CpCAtom_Type,
    (void *) &CpArch_Type,
    (void *) &CpEndian_Type,
    (void *) &CpContext_Type,
    (void *) &CpUnaryExpr_Type,
    (void *) &CpBinaryExpr_Type,
    (void *) &CpContextPath_Type,
    (void *) &CpField_Type,
    (void *) &CpFieldAtom_Type,
    (void *) &CpFieldCAtom_Type,
    (void *) &CpInvalidDefault_Type,
    (void *) &CpDefaultOption_Type,
    (void *) &_CpInvalidDefault_Object,
    (void *) &_CpDefaultOption_Object,
    (void *) &CpOption_Type,
    (void *) &CpState_Type,
    (void *) &CpLayer_Type,
    (void *) &CpStructFieldInfo_Type,
    (void *) &CpStruct_Type,
    (void *) &CpFloatAtom_Type,
    (void *) &CpIntAtom_Type,
    (void *) &CpBoolAtom_Type,
    (void *) &CpCharAtom_Type,
    (void *) &CpPaddingAtom_Type,
    (void *) &CpStringAtom_Type,
    (void *) &CpConstAtom_Type,
    (void *) &CpBuiltinAtom_Type,
    (void *) &CpRepeatedAtom_Type,
    (void *) &CpSeqLayer_Type,
    (void *) &CpObjLayer_Type,
    (void *) &CpConditionAtom_Type,
    (void *) &CpSwitchAtom_Type,
    (void *) &CpOffsetAtom_Type,
    (void *) &CpPrimitiveAtom_Type,
    (void *) &CpLengthInfo_Type,
    (void *) &CpBytesAtom_Type,
    (void *) &CpPStringAtom_Type,
    (void *) &CpEnumAtom_Type,
    (void *) &CpVarIntAtom_Type,
    (void *) &CpComputedAtom_Type,
    (void *) &CpLazyAtom_Type,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    (void *) &CpEndian_IsLittleEndian,
    NULL,
    NULL,
    (void *) &CpContext_New,
    (void *) &CpUnaryExpr_New,
    (void *) &CpBinaryExpr_New,
    (void *) &CpContextPath_New,
    (void *) &CpContextPath_FromString,
    (void *) &CpField_New,
    (void *) &CpField_HasCondition,
    (void *) &CpField_IsEnabled,
    (void *) &CpField_GetOffset,
    (void *) &CpField_EvalSwitch,
    (void *) &CpField_GetLength,
    (void *) &CpTypeOf,
    (void *) &CpTypeOf_Field,
    (void *) &CpTypeOf_Common,
    (void *) &CpPack,
    NULL,
    NULL,
    NULL,
    NULL,
    (void *) &_CpPack_EvalLength,
    (void *) &CpSizeOf,
    (void *) &CpSizeOf_Field,
    (void *) &CpSizeOf_Struct,
    (void *) &CpSizeOf_Common,
    (void *) &_Cp_SizeOf,
    (void *) &CpUnpack,
    NULL,
    NULL,
    NULL,
    NULL,
    (void *) &_CpUnpack_EvalLength,
    (void *) &CpUnpack_CAtom,
    (void *) &CpPack_CAtom,
    (void *) &CpSizeOf_CAtom,
    (void *) &CpTypeOf_CAtom,
    (void *) &CpState_New,
    (void *) &CpState_Tell,
    (void *) &CpState_Seek,
    (void *) &CpState_Read,
    (void *) &CpState_ReadSsize_t,
    (void *) &CpState_ReadFully,
    (void *) &CpState_Write,
    (void *) &CpState_SetGlobals,
    (void *) &CpLayer_New,
    NULL,
    (void *) &CpLayer_Invalidate,
    (void *) &CpStructFieldInfo_New,
    (void *) &CpStruct_AddFieldInfo,
    (void *) &CpStruct_AddField,
    (void *) &CpStruct_New,
    (void *) &CpStruct_GetAnnotations,
    (void *) &CpStruct_ReplaceType,
    (void *) &CpStruct_HasOption,
    (void *) &CpStruct_Pack,
    (void *) &CpStruct_Unpack,
    (void *) &CpStruct_SizeOf,
    (void *) &CpStructModel_Check,
    (void *) &CpStructModel_GetStruct,
    (void *) &CpSeqLayer_New,
    (void *) &CpSeqLayer_SetSequence,
    (void *) &CpObjLayer_New,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    (void *) &CpIntAtom_Pack,
    (void *) &CpIntAtom_Unpack,
    (void *) &CpFloatAtom_Pack,
    (void *) &CpFloatAtom_Unpack,
    (void *) &CpBoolAtom_Pack,
    (void *) &CpBoolAtom_Unpack,
    (void *) &CpCharAtom_Pack,
    (void *) &CpCharAtom_Unpack,
    (void *) &CpPaddingAtom_Pack,
    (void *) &CpPaddingAtom_PackMany,
    (void *) &CpPaddingAtom_Unpack,
    (void *) &CpPaddingAtom_UnpackMany,
    (void *) &CpStringAtom_Pack,
    (void *) &CpStringAtom_Unpack,
    (void *) &CpConstAtom_Pack,
    (void *) &CpConstAtom_Unpack,
    (void *) &CpRepeatedAtom_Pack,
    (void *) &CpRepeatedAtom_Unpack,
    (void *) &CpRepeatedAtom_GetLength,
    (void *) &CpConditionAtom_Pack,
    (void *) &CpConditionAtom_Unpack,
    (void *) &CpConditionAtom_IsEnabled,
    (void *) &CpSwitchAtom_GetNext,
    (void *) &CpSwitchAtom_Pack,
    (void *) &CpSwitchAtom_Unpack,
    (void *) &CpOffsetAtom_Pack,
    (void *) &CpOffsetAtom_Unpack,
    (void *) &CpOffsetAtom_GetOffset,
    (void *) &CpBytesAtom_GetLength,
    (void *) &CpBytesAtom_Pack,
    (void *) &CpBytesAtom_Unpack,
    NULL,
    (void *) &CpPStringAtom_Pack,
    (void *) &CpPStringAtom_Unpack,
    (void *) &CpEnumAtom_Pack,
    (void *) &CpEnumAtom_Unpack,
    (void *) &CpVarIntAtom_Pack,
    (void *) &CpVarIntAtom_Unpack,
    (void *) &CpVarIntAtom_BSwap,
    (void *) &CpVarIntAtom_BSwapUnsignedLongLong,
    (void *) &CpVarIntAtom_BSwapLongLong,
    (void *) &CpVarIntAtom_BSwapSsize_t,
    (void *) &CpComputedAtom_Pack,
    (void *) &CpComputedAtom_Unpack,
    (void *) &CpLazyAtom_Pack,
    (void *) &CpLazyAtom_Unpack
};

