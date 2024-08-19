#ifdef _CPMODULE
#undef _CPMODULE
#endif

#include "caterpillar/atomobj.h"     /* atom struct */
#include "caterpillar/module.h"      /* module macros */

/* example C atom*/
typedef struct _ExampleCAtom
{
  CpCAtom_HEAD

    int value;
} ExampleCAtom;

static PyObject*
example_c_atom_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  ExampleCAtom* self;
  self = (ExampleCAtom*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;
  self->value = 0;

  // place your custom implementation here
  self->ob_base.ob_pack = (packfunc)NULL;
  return (PyObject*)self;
}

static void
example_c_atom_dealloc(ExampleCAtom* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
example_c_atom_repr(ExampleCAtom* self)
{
  return PyUnicode_FromFormat("<ExampleCAtom %d>", self->value);
}

static int
example_c_atom_init(ExampleCAtom* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "value", NULL };
  int value = 0;
  if (!PyArg_ParseTuple(args, "i", &value))
    return -1;

  self->value = value;
  return 0;
}

PyTypeObject ExampleCAtom_Type = {
  PyVarObject_HEAD_INIT(NULL, 0).tp_name = "example._example.ExampleCAtom",
  .tp_dealloc = (destructor)example_c_atom_dealloc, /* tp_dealloc */
  .tp_repr = (reprfunc)example_c_atom_repr,         /* tp_repr */
  .tp_call = (ternaryfunc)example_c_atom_init,      /* tp_call */
  .tp_flags = Py_TPFLAGS_DEFAULT,                   /* tp_flags */
  .tp_init = (initproc)example_c_atom_init,         /* tp_init */
  .tp_new = (newfunc)example_c_atom_new,            /* tp_new */
};

/* module */

static struct PyModuleDef example_module = {
  PyModuleDef_HEAD_INIT, "_example", "example module", -1, NULL,
};

PyMODINIT_FUNC
PyInit__example(void)
{
  PyObject* m;

  import_caterpillar(); // important!

  m = PyState_FindModule(&example_module);
  if (m) {
    return Py_NewRef(m);
  }

  ExampleCAtom_Type.tp_base = &CpCAtom_Type;
  CpModule_SetupType(&ExampleCAtom_Type);

  m = PyModule_Create(&example_module);
  if (m == NULL)
    return NULL;

  CpModule_AddObject("ExampleCAtom", &ExampleCAtom_Type);

  return m;
}