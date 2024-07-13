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
    (void *) &CpEndian_IsLittleEndian
};

