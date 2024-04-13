/* module implementation */
#include "module.h"
#include "atomobj.h"
#include "option.h"

static int
cp_module_clear(PyObject* m)
{
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
  CpModule_SetupType(&CpOption_Type)

  // module setup
  m = PyModule_Create(&CpModule);
  if (!m) {
    return NULL;
  }

  CpModule_AddObject("atom", &CpAtom_Type);
  CpModule_AddObject("Option", &CpOption_Type);
  return m;
}