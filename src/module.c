/* module implementation */
#include "caterpillar/module.h"
#include "caterpillar/arch.h"
#include "caterpillar/atomobj.h"
#include "caterpillar/context.h"
#include "caterpillar/field.h"
#include "caterpillar/option.h"

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
  0,                                /* tp_basicsize */
  0,                                /* tp_itemsize */
  0,                                /* tp_dealloc */
  0,                                /* tp_vectorcall_offset */
  0,                                /* tp_getattr */
  0,                                /* tp_setattr */
  0,                                /* tp_as_async */
  (reprfunc)cp_invaliddefault_repr, /* tp_repr */
  0,                                /* tp_as_number */
  0,                                /* tp_as_sequence */
  0,                                /* tp_as_mapping */
  0,                                /* tp_hash */
  0,                                /* tp_call */
  0,                                /* tp_str */
  0,                                /* tp_getattro */
  0,                                /* tp_setattro */
  0,                                /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,               /* tp_flags */
  0,                                /* tp_doc */
  0,                                /* tp_traverse */
  0,                                /* tp_clear */
  0,                                /* tp_richcompare */
  0,                                /* tp_weaklistoffset */
  0,                                /* tp_iter */
  0,                                /* tp_iternext */
  0,                                /* tp_methods */
  0,                                /* tp_members */
  0,                                /* tp_getset */
  0,                                /* tp_base */
  0,                                /* tp_dict */
  0,                                /* tp_descr_get */
  0,                                /* tp_descr_set */
  0,                                /* tp_dictoffset */
  0,                                /* tp_init */
  0,                                /* tp_alloc */
  (newfunc)cp_invaliddefault_new,   /* tp_new */
  0,                                /* tp_free */
  0,                                /* tp_is_gc */
  0,                                /* tp_bases */
  0,                                /* tp_mro */
  0,                                /* tp_cache */
  0,                                /* tp_subclasses */
  0,                                /* tp_weaklist */
  0,                                /* tp_del */
  0,                                /* tp_version_tag */
  0,                                /* tp_finalize */
  0,                                /* tp_vectorcall */
  0,                                /* tp_watched */
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
  0,                               /* tp_basicsize */
  0,                               /* tp_itemsize */
  0,                               /* tp_dealloc */
  0,                               /* tp_vectorcall_offset */
  0,                               /* tp_getattr */
  0,                               /* tp_setattr */
  0,                               /* tp_as_async */
  (reprfunc)cp_defaultoption_repr, /* tp_repr */
  0,                               /* tp_as_number */
  0,                               /* tp_as_sequence */
  0,                               /* tp_as_mapping */
  0,                               /* tp_hash */
  0,                               /* tp_call */
  0,                               /* tp_str */
  0,                               /* tp_getattro */
  0,                               /* tp_setattro */
  0,                               /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,              /* tp_flags */
  0,                               /* tp_doc */
  0,                               /* tp_traverse */
  0,                               /* tp_clear */
  0,                               /* tp_richcompare */
  0,                               /* tp_weaklistoffset */
  0,                               /* tp_iter */
  0,                               /* tp_iternext */
  0,                               /* tp_methods */
  0,                               /* tp_members */
  0,                               /* tp_getset */
  0,                               /* tp_base */
  0,                               /* tp_dict */
  0,                               /* tp_descr_get */
  0,                               /* tp_descr_set */
  0,                               /* tp_dictoffset */
  0,                               /* tp_init */
  0,                               /* tp_alloc */
  (newfunc)cp_defaultoption_new,   /* tp_new */
  0,                               /* tp_free */
  0,                               /* tp_is_gc */
  0,                               /* tp_bases */
  0,                               /* tp_mro */
  0,                               /* tp_cache */
  0,                               /* tp_subclasses */
  0,                               /* tp_weaklist */
  0,                               /* tp_del */
  0,                               /* tp_version_tag */
  0,                               /* tp_finalize */
  0,                               /* tp_vectorcall */
  0,                               /* tp_watched */
};

PyObject _CpDefaultOption_Object = { _PyObject_EXTRA_INIT{
                                       _Py_IMMORTAL_REFCNT /* ob_refcnt */ },
                                     &CpDefaultOption_Type /* ob_type */ };

// ------------------------------------------------------------------------------
// module

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
    Py_CLEAR(state->cp_arch__host);

    // typing references
    Py_CLEAR(state->typing_any);
    Py_CLEAR(state->typing_list);
    Py_CLEAR(state->typing_union);

    // sttings
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
  }
  return 0;
}

static void
cp_module_free(void* m)
{
  cp_module_clear((PyObject*)m);
}

/* module def */

PyModuleDef CpModule = {
  PyModuleDef_HEAD_INIT, /* m_base */
  _Cp_Name(_core),       /* m_name */
  NULL,                  /* m_doc */
  sizeof(_modulestate),  /* m_size */
  NULL,                  /* m_methods */
  NULL,                  /* m_slots */
  NULL,                  /* m_traverse */
  cp_module_clear,       /* m_clear */
  cp_module_free         /* m_free */
};

/* module init */
PyMODINIT_FUNC
PyInit__core(void)
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
    cp_option__dynamic,
    "S_REPLACE_TYPES",
    CpObject_Create(&CpOption_Type, "s", "struct:replace_types"));
  CpModuleState_AddObject(
    cp_option__dynamic,
    "S_DISCARD_UNNAMED",
    CpObject_Create(&CpOption_Type, "s", "struct:discard_unnamed"));
  CpModuleState_AddObject(cp_option__dynamic,
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

#undef CACHED_STRING

  // setup typing constants
  PyObject* typing = PyImport_ImportModule("typing");
  if (!typing) {
    PyErr_SetString(PyExc_ImportError, "failed to import typing");
    return NULL;
  }

  CpModuleState_Set(typing_any, PyObject_GetAttrString(typing, "Any"));
  CpModuleState_Set(typing_list, PyObject_GetAttrString(typing, "List"));
  CpModuleState_Set(typing_union, PyObject_GetAttrString(typing, "Union"));
  Py_XDECREF(typing);
  return m;
}