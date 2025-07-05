/* These pointers will be stored in the C-object for use in other
    extension modules
*/

void *Cp_API[] = {
    (void *) &CpModule,
    (void *) &CpArch_Type,
    (void *) &CpEndian_Type,
    (void *) &CpEndian_IsLittleEndian
};

