/* These pointers will be stored in the C-object for use in other
    extension modules
*/

void *Cp_API[] = {
    (void *) &CpModule,
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
    (void *) &CpAtom_Type,
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
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
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
    (void *) &CpPack_Field,
    (void *) &CpPack_Common,
    (void *) &CpPack_Struct,
    (void *) &_Cp_Pack,
    (void *) &_CpPack_EvalLength,
    (void *) &CpSizeOf,
    (void *) &CpSizeOf_Field,
    (void *) &CpSizeOf_Struct,
    (void *) &CpSizeOf_Common,
    (void *) &_Cp_SizeOf,
    (void *) &CpUnpack,
    (void *) &CpUnpack_Field,
    (void *) &CpUnpack_Common,
    (void *) &CpUnpack_Struct,
    (void *) &_Cp_Unpack,
    (void *) &_CpUnpack_EvalLength,
    (void *) &CpUnpack_CAtom,
    (void *) &CpPack_CAtom,
    (void *) &CpSizeOf_CAtom,
    (void *) &CpTypeOf_CAtom,
    (void *) &CpState_New,
    (void *) &CpState_Tell,
    (void *) &CpState_Seek,
    (void *) &CpState_Read,
    (void *) &CpState_ReadFully,
    (void *) &CpState_Write,
    (void *) &CpState_SetGlobals,
    (void *) &CpLayer_New,
    (void *) &CpLayer_Invalidate,
    (void *) &CpLayer_SetSequence
};

