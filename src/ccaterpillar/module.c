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
    cp_arch__mod_clear(m, state);
    cp_option__mod_clear(m, state);
    cp_context__mod_clear(m, state);
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
#define SETUP_TYPES(name)                                                      \
  if (name##__mod_types() < 0)                                                 \
  return NULL

#define ADD_OBJECTS(name)                                                      \
  if (name##__mod_init(m, state) < 0)                                          \
  return NULL

  SETUP_TYPES(cp_context);
  SETUP_TYPES(cp_arch);
  SETUP_TYPES(cp_option);

  if (cp_context__mod_types() < 0)
    return NULL;

  m = PyModule_Create(&CpModule);
  if (!m) {
    return NULL;
  }

  /* setup state */
  _modulestate* state = get_module_state(m);

  ADD_OBJECTS(cp_context);
  ADD_OBJECTS(cp_arch);
  ADD_OBJECTS(cp_option);

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

#undef SETUP_TYPES
#undef ADD_OBJECTS
}