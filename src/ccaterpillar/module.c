/* module implementation */
#ifndef _CPMODULE
#define _CPMODULE
#endif

#include "caterpillar/caterpillar.h"

#include "caterpillarapi.c"
#include "private.h"

// ------------------------------------------------------------------------------
// module
static int
cp_module_clear(PyObject* m)
{
  _modulestate* state = get_module_state(m);
  if (state) {
    /* clear default arch and endian */
    Py_CLEAR(state->cp_endian__native);
    Py_CLEAR(state->cp_endian__little);
    Py_CLEAR(state->cp_endian__big);
    Py_CLEAR(state->cp_arch__host);
  }
  return 0;
}

static void
cp_module_free(void* m)
{
  cp_module_clear((PyObject*)m);
}

/* module def */
static PyMethodDef _module_methods[] = { { NULL } };

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
  CpModule_SetupType(&CpArch_Type);
  CpModule_SetupType(&CpEndian_Type);
  CpModule_SetupType(&CpOption_Type);

  m = PyModule_Create(&CpModule);
  if (!m) {
    return NULL;
  }

  CpModule_AddObject(CpArch_NAME, &CpArch_Type);
  CpModule_AddObject(CpEndian_NAME, &CpEndian_Type);
  CpModule_AddObject(CpOption_NAME, &CpOption_Type);

  /* setup custom intatoms */
#define CpModule_DefAtom(name, ...)                                            \
  {                                                                            \
    PyObject* value = (PyObject*)__VA_ARGS__;                                  \
    if (!value) {                                                              \
      return NULL;                                                             \
    }                                                                          \
    CpModule_AddObject(name, value);                                           \
  }

  /* setup state */
  _modulestate* state = get_module_state(m);

  /* setup arch and endian */
  CpModuleState_AddObject(
    cp_endian__native, "NATIVE_ENDIAN", CpEndian_New("native", '='));
  CpModuleState_AddObject(
    cp_endian__little, "LITTLE_ENDIAN", CpEndian_New("little", '<'));
  CpModuleState_AddObject(
    cp_endian__big, "BIG_ENDIAN", CpEndian_New("big", '>'));
  CpModuleState_AddObject(
    cp_arch__host, "HOST_ARCH", CpArch_New("<host>", sizeof(void*) * 8));

  /* setup options */

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