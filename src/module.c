/* module implementation */
#ifndef _CPMODULE
#define _CPMODULE
#endif

#include "caterpillar/caterpillar.h"

#include "caterpillarapi.c"

#define CpModule_AddObject(name, value)                                        \
  Py_INCREF(value);                                                            \
  if (PyModule_AddObject(m, name, (PyObject*)(value)) < 0) {                   \
    Py_DECREF(value);                                                          \
    Py_DECREF(m);                                                              \
    PyErr_SetString(PyExc_RuntimeError, "unable to add '" name "' to module"); \
    return NULL;                                                               \
  }

#define CpModuleState_AddObject(varName, objName, ...)                         \
  state->varName = __VA_ARGS__;                                                \
  if (!state->varName) {                                                       \
    PyErr_SetString(PyExc_RuntimeError,                                        \
                    ("unable to create state object '" objName "'"));          \
    return NULL;                                                               \
  }                                                                            \
  CpModule_AddObject(objName, state->varName);

#define CpModuleState_Set(varName, ...)                                        \
  state->varName = __VA_ARGS__;                                                \
  if (!state->varName) {                                                       \
    PyErr_SetString(PyExc_RuntimeError,                                        \
                    ("unable to create state object '" #varName "'"));         \
    return NULL;                                                               \
  }

/* immortal objects */
static PyObject*
cp_invaliddefault_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  if (PyTuple_GET_SIZE(args) || PyDict_GET_SIZE(kw)) {
    PyErr_SetString(PyExc_TypeError,
                    "InvalidDefaultType does not accept arguments");
    return NULL;
  }

  Py_INCREF(CpInvalidDefault);
  return CpInvalidDefault;
}

static PyObject*
cp_invaliddefault_repr(PyObject* self)
{
  return PyUnicode_FromString("<InvalidDefault>");
}

PyTypeObject CpInvalidDefault_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(InvalidDefaultType),
  .tp_repr = (reprfunc)cp_invaliddefault_repr,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = (newfunc)cp_invaliddefault_new,
};

PyObject _CpInvalidDefault_Object = { _PyObject_EXTRA_INIT{
                                        _Py_IMMORTAL_REFCNT /* ob_refcnt */ },
                                      &CpInvalidDefault_Type /* ob_type */ };

static PyObject*
cp_defaultoption_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  if (PyTuple_GET_SIZE(args) || PyDict_GET_SIZE(kw)) {
    PyErr_SetString(PyExc_TypeError,
                    "InvalidDefaultType does not accept arguments");
    return NULL;
  }

  Py_INCREF(CpDefaultOption);
  return CpDefaultOption;
}

static PyObject*
cp_defaultoption_repr(PyObject* self)
{
  return PyUnicode_FromString("<DefaultSwitchOption>");
}

PyTypeObject CpDefaultOption_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(DefaultOptionType),
  .tp_repr = (reprfunc)cp_defaultoption_repr,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = (newfunc)cp_defaultoption_new,
};

PyObject _CpDefaultOption_Object = { _PyObject_EXTRA_INIT{
                                       _Py_IMMORTAL_REFCNT /* ob_refcnt */ },
                                     &CpDefaultOption_Type /* ob_type */ };

// ------------------------------------------------------------------------------
// module
static PyObject*
cp_core_typeof(PyObject* m, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "obj", NULL };
  PyObject* op = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kwlist, &op)) {
    return NULL;
  }
  return CpTypeOf(op);
}

static PyObject*
cp_core_pack_into(PyObject* m, PyObject* args, PyObject* kw)
{
  PyObject *op = NULL, *atom = NULL, *io = NULL, *globals = PyDict_New(),
           *key = NULL, *value = NULL;
  int res = 0;
  if (!globals) {
    return NULL;
  }
  if (!PyArg_ParseTuple(args, "OOO", &op, &atom, &io)) {
    goto finish;
  }
  if (kw && PyDict_Check(kw)) {
    Py_ssize_t pos = 0;
    while (PyDict_Next(kw, &pos, &key, &value)) {
      if (PyDict_SetItem(globals, key, value) < 0) {
        goto finish;
      }
    }
  }
  if (Py_IsNone(atom)) {
    PyErr_SetString(PyExc_ValueError, "atom not set!");
    goto finish;
  }

  if (Py_IsNone(io)) {
    PyErr_SetString(PyExc_ValueError, "output stream not set!");
    goto finish;
  }
  res = CpPack(op, atom, io, globals);
finish:
  Py_XDECREF(globals);
  return res < 0 ? NULL : Py_None;
}

static PyObject*
cp_core_pack(PyObject* m, PyObject* args, PyObject* kw)
{
  PyObject *op = NULL, *atom = NULL, *globals = PyDict_New(), *key = NULL,
           *value = NULL, *io = NULL;
  int res = 0;
  if (!globals) {
    return NULL;
  }
  _modulestate* state = get_module_state(m);
  io = PyObject_CallNoArgs(state->BytesIO_Type);
  if (!io) {
    return NULL;
  }

  if (!PyArg_ParseTuple(args, "OO", &op, &atom)) {
    goto finish;
  }
  if (kw && PyDict_Check(kw)) {
    Py_ssize_t pos = 0;
    while (PyDict_Next(kw, &pos, &key, &value)) {
      if (PyDict_SetItem(globals, key, value) < 0) {
        goto finish;
      }
    }
  }
  if (Py_IsNone(atom)) {
    PyErr_SetString(PyExc_ValueError, "atom not set!");
    goto finish;
  }

  res = CpPack(op, atom, io, globals);
finish:
  Py_XDECREF(globals);
  if (res < 0) {
    return NULL;
  }

  PyObject* result = PyObject_CallMethodNoArgs(io, state->str_bytesio_getvalue);
  Py_XDECREF(io);
  return result;
}

static PyObject*
cp_core_sizeof(PyObject* m, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "obj", "globals", NULL };
  PyObject *op = NULL, *globals = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "O|O", kwlist, &op, &globals)) {
    return NULL;
  }
  return CpSizeOf(op, globals);
}

static PyObject*
cp_core_unpack(PyObject* m, PyObject* args, PyObject* kw)
{
  PyObject *atom = NULL, *globals = PyDict_New(), *key = NULL, *value = NULL,
           *io = NULL;
  PyObject* res = NULL;
  int wrapped_io = false;
  if (!globals) {
    return NULL;
  }
  _modulestate* state = get_module_state(m);
  if (!PyArg_ParseTuple(args, "OO", &io, &atom)) {
    goto finish;
  }
  if (PyBytes_Check(io)) {
    PyObject* args = Py_BuildValue("(O)", io);
    io = PyObject_CallObject(state->BytesIO_Type, args);
    Py_DECREF(args);
    if (!io) {
      goto finish;
    }
    if (!io) {
      goto finish;
    }
    wrapped_io = true;
  }
  if (kw && PyDict_Check(kw)) {
    Py_ssize_t pos = 0;
    while (PyDict_Next(kw, &pos, &key, &value)) {
      if (PyDict_SetItem(globals, key, value) < 0) {
        goto finish;
      }
    }
  }
  if (Py_IsNone(atom)) {
    PyErr_SetString(PyExc_ValueError, "atom not set!");
    goto finish;
  }

  res = CpUnpack(atom, io, globals);
finish:
  Py_XDECREF(globals);
  if (wrapped_io) {
    Py_XDECREF(io);
  }
  return res;
}

static int
cp_module_clear(PyObject* m)
{
  _modulestate* state = get_module_state(m);
  if (state) {
    /* clear dynamic options */
    Py_CLEAR(state->cp_option__dynamic);
    Py_CLEAR(state->cp_option__sequential);
    Py_CLEAR(state->cp_option__keep_position);
    Py_CLEAR(state->cp_option__union);
    Py_CLEAR(state->cp_option__eval);
    Py_CLEAR(state->cp_option__replace_types);
    Py_CLEAR(state->cp_option__discard_unnamed);
    Py_CLEAR(state->cp_option__discard_const);
    Py_CLEAR(state->cp_option__slots);

    /* clear global option defaults */
    Py_CLEAR(state->cp_option__global_field_options);
    Py_CLEAR(state->cp_option__global_struct_options);

    /* clear default arch and endian */
    Py_CLEAR(state->cp_endian__native);
    Py_CLEAR(state->cp_endian__little);
    Py_CLEAR(state->cp_endian__big);
    Py_CLEAR(state->cp_arch__host);

    // typing references
    Py_CLEAR(state->Any_Type);
    Py_CLEAR(state->List_Type);
    Py_CLEAR(state->Union_Type);
    Py_CLEAR(state->Optional_Type);

    // strings
    Py_CLEAR(state->str_path_delim);
    Py_CLEAR(state->str___pack__);
    Py_CLEAR(state->str___unpack__);
    Py_CLEAR(state->str___size__);
    Py_CLEAR(state->str___type__);
    Py_CLEAR(state->str_write);
    Py_CLEAR(state->str_close);
    Py_CLEAR(state->str_read);
    Py_CLEAR(state->str_seek);
    Py_CLEAR(state->str_tell);
    Py_CLEAR(state->str___unpack_many__);
    Py_CLEAR(state->str___pack_many__);
    Py_CLEAR(state->str_start);
    Py_CLEAR(state->str_ctx__root);
    Py_CLEAR(state->str_ctx__getattr);
    Py_CLEAR(state->str_bytesio_getvalue);
    Py_CLEAR(state->str___annotations__);
    Py_CLEAR(state->str_builder_process);
    Py_CLEAR(state->str___mro__);
    Py_CLEAR(state->str___struct__);
    Py_CLEAR(state->str_pattern_match);
    Py_CLEAR(state->str___match_args__);
    Py_CLEAR(state->str___slots__);
    Py_CLEAR(state->str___dict__);
    Py_CLEAR(state->str___weakref__);
    Py_CLEAR(state->str___qualname__);
    Py_CLEAR(state->str_strict);
    Py_CLEAR(state->str__value2member_map_);
    Py_CLEAR(state->str__member_map_);

    Py_CLEAR(state->cp_regex__unnamed);

    Py_CLEAR(state->cp_bytes__false);
    Py_CLEAR(state->cp_bytes__true);
  }
  return 0;
}

static void
cp_module_free(void* m)
{
  cp_module_clear((PyObject*)m);
}

/* module def */
static PyMethodDef _module_methods[] = {
  { "typeof",
    (PyCFunction)cp_core_typeof,
    METH_VARARGS | METH_KEYWORDS,
    "Returns the type of an object." },
  { "pack_into",
    (PyCFunction)cp_core_pack_into,
    METH_VARARGS | METH_KEYWORDS,
    NULL },
  { "pack", (PyCFunction)cp_core_pack, METH_VARARGS | METH_KEYWORDS, NULL },
  { "sizeof", (PyCFunction)cp_core_sizeof, METH_VARARGS | METH_KEYWORDS, NULL },
  { "unpack", (PyCFunction)cp_core_unpack, METH_VARARGS | METH_KEYWORDS, NULL },
  { NULL }
};

PyModuleDef CpModule = {
  PyModuleDef_HEAD_INIT, /* m_base */
  "caterpillar._C",      /* m_name */
  NULL,                  /* m_doc */
  sizeof(_modulestate),  /* m_size */
  _module_methods,       /* m_methods */
  NULL,                  /* m_slots */
  NULL,                  /* m_traverse */
  cp_module_clear,       /* m_clear */
  cp_module_free         /* m_free */
};

/* module init */
PyMODINIT_FUNC
PyInit__C(void)
{
  PyObject* m;
  m = PyState_FindModule(&CpModule);
  if (m) {
    Py_INCREF(m);
    return m;
  }

  // type setup
  CpModule_SetupType(&CpAtom_Type);
  CpCAtom_Type.tp_base = &CpAtom_Type;
  CpModule_SetupType(&CpCAtom_Type);

  CpModule_SetupType(&CpOption_Type);
  CpModule_SetupType(&CpArch_Type);
  CpModule_SetupType(&CpEndian_Type);
  CpModule_SetupType(&CpInvalidDefault_Type);
  CpModule_SetupType(&CpDefaultOption_Type);

  CpContext_Type.tp_base = &PyDict_Type;
  CpModule_SetupType(&CpContext_Type);
  CpModule_SetupType(&CpBinaryExpr_Type);
  CpModule_SetupType(&CpUnaryExpr_Type);
  CpModule_SetupType(&CpContextPath_Type);
  CpModule_SetupType(&CpField_Type);

  CpFieldAtom_Type.tp_base = &CpAtom_Type;
  CpFieldCAtom_Type.tp_base = &CpCAtom_Type;
  CpModule_SetupType(&CpFieldAtom_Type);
  CpModule_SetupType(&CpFieldCAtom_Type);
  CpModule_SetupType(&CpLayer_Type);

  CpSeqLayer_Type.tp_base = &CpLayer_Type;
  CpObjLayer_Type.tp_base = &CpLayer_Type;
  CpModule_SetupType(&CpSeqLayer_Type);
  CpModule_SetupType(&CpObjLayer_Type);
  CpModule_SetupType(&CpState_Type);

  CpModule_SetupType(&CpStructFieldInfo_Type);
  CpModule_SetupType(&CpLengthInfo_Type);

  // builtins setup
  CpPrimitiveAtom_Type.tp_base = &CpAtom_Type;
  CpBuiltinAtom_Type.tp_base = &CpCAtom_Type;
  CpRepeatedAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpConditionAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpSwitchAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpOffsetAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpStruct_Type.tp_base = &CpBuiltinAtom_Type;
  CpBoolAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpFloatAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpIntAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpCharAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpPaddingAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpStringAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpConstAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpBytesAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpPStringAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpEnumAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpVarIntAtom_Type.tp_base = &CpBuiltinAtom_Type;
  CpComputedAtom_Type.tp_base = &CpBuiltinAtom_Type;

  CpModule_SetupType(&CpBuiltinAtom_Type);
  CpModule_SetupType(&CpPrimitiveAtom_Type);
  CpModule_SetupType(&CpRepeatedAtom_Type);
  CpModule_SetupType(&CpConditionAtom_Type);
  CpModule_SetupType(&CpSwitchAtom_Type);
  CpModule_SetupType(&CpOffsetAtom_Type);
  CpModule_SetupType(&CpStruct_Type);
  CpModule_SetupType(&CpIntAtom_Type);
  CpModule_SetupType(&CpFloatAtom_Type);
  CpModule_SetupType(&CpBoolAtom_Type);
  CpModule_SetupType(&CpCharAtom_Type);
  CpModule_SetupType(&CpPaddingAtom_Type);
  CpModule_SetupType(&CpStringAtom_Type);
  CpModule_SetupType(&CpConstAtom_Type);
  CpModule_SetupType(&CpBytesAtom_Type);
  CpModule_SetupType(&CpPStringAtom_Type);
  CpModule_SetupType(&CpEnumAtom_Type);
  CpModule_SetupType(&CpVarIntAtom_Type);
  CpModule_SetupType(&CpComputedAtom_Type);

  // module setup
  m = PyModule_Create(&CpModule);
  if (!m) {
    return NULL;
  }

  CpModule_AddObject("atom", &CpAtom_Type);
  CpModule_AddObject("catom", &CpCAtom_Type);
  CpModule_AddObject("Option", &CpOption_Type);
  CpModule_AddObject("Arch", &CpArch_Type);
  CpModule_AddObject("Endian", &CpEndian_Type);
  CpModule_AddObject("Context", &CpContext_Type);
  CpModule_AddObject("BinaryExpr", &CpBinaryExpr_Type);
  CpModule_AddObject("UnaryExpr", &CpUnaryExpr_Type);
  CpModule_AddObject("ContextPath", &CpContextPath_Type);
  CpModule_AddObject("InvalidDefaultType", &CpInvalidDefault_Type);
  CpModule_AddObject("InvalidDefault", CpInvalidDefault);
  CpModule_AddObject("DefaultOptionType", &CpDefaultOption_Type);
  CpModule_AddObject("DefaultOption", CpDefaultOption);
  CpModule_AddObject("Field", &CpField_Type);
  CpModule_AddObject("fieldatom", &CpFieldAtom_Type);
  CpModule_AddObject("fieldcatom", &CpFieldCAtom_Type);
  CpModule_AddObject("layer", &CpLayer_Type);
  CpModule_AddObject(CpSeqLayer_NAME, &CpSeqLayer_Type);
  CpModule_AddObject(CpObjLayer_NAME, &CpObjLayer_Type);
  CpModule_AddObject("State", &CpState_Type);
  CpModule_AddObject("fieldinfo", &CpStructFieldInfo_Type);
  CpModule_AddObject("Struct", &CpStruct_Type);
  CpModule_AddObject(CpLengthInfo_NAME, &CpLengthInfo_Type);

  CpModule_AddObject(CpPrimitiveAtom_NAME, &CpPrimitiveAtom_Type);
  CpModule_AddObject(CpBuiltinAtom_NAME, &CpBuiltinAtom_Type);
  CpModule_AddObject(CpRepeatedAtom_NAME, &CpRepeatedAtom_Type);
  CpModule_AddObject(CpConditionAtom_NAME, &CpConditionAtom_Type);
  CpModule_AddObject(CpSwitchAtom_NAME, &CpSwitchAtom_Type);
  CpModule_AddObject(CpOffsetAtom_NAME, &CpOffsetAtom_Type);

  CpModule_AddObject(CpIntAtom_NAME, &CpIntAtom_Type);
  CpModule_AddObject(CpFloatAtom_NAME, &CpFloatAtom_Type);
  CpModule_AddObject(CpBoolAtom_NAME, &CpBoolAtom_Type);
  CpModule_AddObject(CpCharAtom_NAME, &CpCharAtom_Type);
  CpModule_AddObject(CpPaddingAtom_NAME, &CpPaddingAtom_Type);
  CpModule_AddObject(CpStringAtom_NAME, &CpStringAtom_Type);
  CpModule_AddObject(CpConstAtom_NAME, &CpConstAtom_Type);
  CpModule_AddObject(CpBytesAtom_NAME, &CpBytesAtom_Type);
  CpModule_AddObject(CpPStringAtom_NAME, &CpPStringAtom_Type);
  CpModule_AddObject(CpEnumAtom_NAME, &CpEnumAtom_Type);
  CpModule_AddObject(CpVarIntAtom_NAME, &CpVarIntAtom_Type);
  CpModule_AddObject(CpComputedAtom_NAME, &CpComputedAtom_Type);

  /* setup custom intatoms */
#define CpModule_DefAtom(name, ...)                                            \
  {                                                                            \
    PyObject* value = (PyObject*)__VA_ARGS__;                                  \
    if (!value) {                                                              \
      return NULL;                                                             \
    }                                                                          \
    CpModule_AddObject(name, value);                                           \
  }

#define CpModule_DefIntAtom(name, bits, signed)                                \
  CpModule_DefAtom(                                                            \
    name, CpObject_Create(&CpIntAtom_Type, "Iii", bits, signed, true));

  CpModule_DefIntAtom("i8", 8, true);
  CpModule_DefIntAtom("u8", 8, false);
  CpModule_DefIntAtom("i16", 16, true);
  CpModule_DefIntAtom("u16", 16, false);
  CpModule_DefIntAtom("i24", 24, true);
  CpModule_DefIntAtom("u24", 24, false);
  CpModule_DefIntAtom("i32", 32, true);
  CpModule_DefIntAtom("u32", 32, false);
  CpModule_DefIntAtom("i64", 64, true);
  CpModule_DefIntAtom("u64", 64, false);
  CpModule_DefIntAtom("i128", 128, true);
  CpModule_DefIntAtom("u128", 128, false);

#define CpModule_DefFloatAtom(name, bits)                                      \
  CpModule_DefAtom(name, CpObject_Create(&CpFloatAtom_Type, "I", bits));

  CpModule_DefFloatAtom("f16", 16);
  CpModule_DefFloatAtom("f32", 32);
  CpModule_DefFloatAtom("f64", 64);

#undef CpModule_DefIntAtom
#undef CpModule_DefAtom

  CpModule_AddObject("boolean", CpObject_CreateNoArgs(&CpBoolAtom_Type));
  CpModule_AddObject("char", CpObject_CreateNoArgs(&CpCharAtom_Type));
  CpModule_AddObject("padding", CpObject_CreateNoArgs(&CpPaddingAtom_Type));
  CpModule_AddObject("varint", CpVarIntAtom_New(true, false));
  CpModule_AddObject("lsbvarint", CpVarIntAtom_New(true, true));

  /* setup state */
  _modulestate* state = get_module_state(m);
  CpModuleState_AddObject(
    cp_option__dynamic,
    "F_DYNAMIC",
    CpObject_Create(&CpOption_Type, "s", "field:dynamic"));
  CpModuleState_AddObject(
    cp_option__sequential,
    "F_SEQUENTIAL",
    CpObject_Create(&CpOption_Type, "s", "field:sequential"));
  CpModuleState_AddObject(
    cp_option__keep_position,
    "F_DYNAMIC",
    CpObject_Create(&CpOption_Type, "s", "field:keep_position"));
  CpModuleState_AddObject(cp_option__union,
                          "S_UNION",
                          CpObject_Create(&CpOption_Type, "s", "struct:union"));
  CpModuleState_AddObject(
    cp_option__eval,
    "S_EVAL_ANNOTATIONS",
    CpObject_Create(&CpOption_Type, "s", "struct:eval_annotations"));
  CpModuleState_AddObject(
    cp_option__replace_types,
    "S_REPLACE_TYPES",
    CpObject_Create(&CpOption_Type, "s", "struct:replace_types"));
  CpModuleState_AddObject(
    cp_option__discard_unnamed,
    "S_DISCARD_UNNAMED",
    CpObject_Create(&CpOption_Type, "s", "struct:discard_unnamed"));
  CpModuleState_AddObject(
    cp_option__discard_const,
    "S_DISCARD_CONST",
    CpObject_Create(&CpOption_Type, "s", "struct:discard_const"));
  CpModuleState_AddObject(cp_option__slots,
                          "S_SLOTS",
                          CpObject_Create(&CpOption_Type, "s", "struct:slots"));

  CpModuleState_AddObject(
    cp_option__global_struct_options, "STRUCT_OPTIONS", PySet_New(NULL));
  CpModuleState_AddObject(
    cp_option__global_struct_options, "FIELD_OPTIONS", PySet_New(NULL));

  /* setup arch and endian */
  CpModuleState_AddObject(cp_endian__native,
                          "NATIVE_ENDIAN",
                          CpObject_Create(&CpEndian_Type, "sb", "native", '='));
  CpModuleState_AddObject(cp_endian__little,
                          "LITTLE_ENDIAN",
                          CpObject_Create(&CpEndian_Type, "sb", "little", '<'));
  CpModuleState_AddObject(cp_endian__big,
                          "BIG_ENDIAN",
                          CpObject_Create(&CpEndian_Type, "sb", "big", '>'));
  CpModuleState_AddObject(
    cp_arch__host,
    "HOST_ARCH",
    CpObject_Create(&CpArch_Type, "si", "<host>", sizeof(void*) * 8));

// intern strings
#define CACHED_STRING(attr, str)                                               \
  if ((state->attr = PyUnicode_InternFromString(str)) == NULL)                 \
  return NULL

  CACHED_STRING(str___pack__, "__pack__");
  CACHED_STRING(str___unpack__, "__unpack__");
  CACHED_STRING(str___unpack_many__, "__unpack_many__");
  CACHED_STRING(str___pack_many__, "__pack_many__");
  CACHED_STRING(str___size__, "__size__");
  CACHED_STRING(str___type__, "__type__");
  CACHED_STRING(str_close, "close");
  CACHED_STRING(str_read, "read");
  CACHED_STRING(str_write, "write");
  CACHED_STRING(str_seek, "seek");
  CACHED_STRING(str_tell, "tell");
  CACHED_STRING(str_start, "start");
  CACHED_STRING(str_ctx__root, "<root>");
  CACHED_STRING(str_ctx__getattr, "__context_getattr__");
  CACHED_STRING(str_bytesio_getvalue, "getvalue");
  CACHED_STRING(str___annotations__, "__annotations__");
  CACHED_STRING(str_builder_process, "process");
  CACHED_STRING(str___mro__, "__mro__");
  CACHED_STRING(str___struct__, "__struct__");
  CACHED_STRING(str_pattern_match, "match");
  CACHED_STRING(str___match_args__, "__match_args__");
  CACHED_STRING(str___slots__, "__slots__");
  CACHED_STRING(str___dict__, "__dict__");
  CACHED_STRING(str___weakref__, "__weakref__");
  CACHED_STRING(str___qualname__, "__qualname__");
  CACHED_STRING(str_path_delim, ".");
  CACHED_STRING(str_strict, "strict");
  CACHED_STRING(str__member_map_, "_member_map_");
  CACHED_STRING(str__value2member_map_, "_value2member_map_");

#undef CACHED_STRING

#define CACHED_BYTES(attr, str, size)                                          \
  if ((state->attr = PyBytes_FromStringAndSize(str, size)) == NULL) {          \
    return NULL;                                                               \
  }

  CACHED_BYTES(cp_bytes__false, "\x00", 1);
  CACHED_BYTES(cp_bytes__true, "\x01", 1);

#undef CACHED_BYTES

  // setup typing constants
  PyObject* typing = PyImport_ImportModule("typing");
  if (!typing) {
    PyErr_SetString(PyExc_ImportError, "failed to import typing");
    return NULL;
  }

  CpModuleState_Set(Any_Type, PyObject_GetAttrString(typing, "Any"));
  CpModuleState_Set(List_Type, PyObject_GetAttrString(typing, "List"));
  CpModuleState_Set(Union_Type, PyObject_GetAttrString(typing, "Union"));
  CpModuleState_Set(Optional_Type, PyObject_GetAttrString(typing, "Optional"));
  Py_XDECREF(typing);

  // regex setup
  PyObject* re = PyImport_ImportModule("re");
  if (!re) {
    goto err;
  }

  PyObject* compile = PyObject_GetAttrString(re, "compile");
  if (!compile) {
    goto err;
  }

  state->cp_regex__unnamed = PyObject_CallFunction(compile, "s", "_[0-9]*$");
  if (!state->cp_regex__unnamed) {
    goto err;
  }

  PyObject* inspect = PyImport_ImportModule("inspect");
  if (!inspect) {
    PyErr_SetString(PyExc_ImportError, "failed to import inspect");
    goto err;
  }

  CpModuleState_Set(inspect_getannotations,
                    PyObject_GetAttrString(inspect, "get_annotations"));
  Py_XDECREF(inspect);

  PyObject* io = PyImport_ImportModule("io");
  if (!io) {
    PyErr_SetString(PyExc_ImportError, "failed to import io");
    goto err;
  }

  CpModuleState_Set(BytesIO_Type, PyObject_GetAttrString(io, "BytesIO"));
  Py_XDECREF(io);

  /*Export API table*/
  PyObject* c_api = PyCapsule_New((void*)Cp_API, NULL, NULL);
  if (c_api == NULL) {
    goto err;
  }

  PyObject* d = PyModule_GetDict(m);
  if (d == NULL) {
    goto err;
  }

  if (PyDict_SetItemString(d, "_C_API", c_api) < 0) {
    goto err;
  }
  Py_DECREF(c_api);
  return m;

err:
  if (!PyErr_Occurred()) {
    PyErr_SetString(PyExc_RuntimeError, "cannot load caterpillar._C module.");
  }
  Py_DECREF(m);
  return NULL;
}