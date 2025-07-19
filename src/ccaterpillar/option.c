/* option implementation */

#include "caterpillar/caterpillar.h"
#include "private.h"
#include "structmember.h"

/* impl */

static PyObject*
cp_option_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpOptionObject* self;
  if ((self = (CpOptionObject*)type->tp_alloc(type, 0), !self)) {
    return NULL;
  }

  if ((self->name = PyUnicode_FromString(""), !self->name)) {
    return NULL;
  }

  self->value = Py_NewRef(Py_None);
  self->nameHash = 0;
  return (PyObject*)self;
}

static void
cp_option_dealloc(CpOptionObject* self)
{
  Py_XDECREF(self->name);
  Py_XDECREF(self->value);
  self->nameHash = 0;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
cp_option_repr(CpOptionObject* self)
{
  if (Py_IsNone(self->value)) {
    return PyUnicode_FromFormat("<Option %S>", self->name);
  }
  return PyUnicode_FromFormat("<Option %S=%R>", self->name, self->value);
}

static PyObject*
cp_option_richcmp(CpOptionObject* self, PyObject* other, int op)
{
  static const char* _NameAttr = "name";
  if (!PyObject_IsInstance(other, (PyObject*)&CpOption_Type)) {
    // check if name is equal to this object's name
    if (PyObject_HasAttrString(other, _NameAttr)) {
      PyObject* otherName = PyObject_GetAttrString(other, _NameAttr);
      if (!otherName) {
        return NULL;
      }
      return PyObject_RichCompare(self->name, otherName, op);
    }
    return Py_NewRef(Py_False);
  }
  return PyObject_RichCompare(self->name, ((CpOptionObject*)other)->name, op);
}

static Py_hash_t
cp_option_hash(CpOptionObject* self)
{
  return self->nameHash;
}

static int
cp_option_init(CpOptionObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "name", "value", NULL };
  PyObject *name = NULL, *value = NULL;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "U|O", kwlist, &name, &value))
    return -1;

  _Cp_SetObj(self->name, name);
  _Cp_SetObj(self->value, value);

  if (PyUnicode_GET_LENGTH(self->name) == 0) {
    PyErr_SetString(PyExc_ValueError, "name cannot be an empty string");
    return -1;
  }
  self->nameHash = PyObject_Hash(self->name);
  return 0;
}

/* docs */

PyDoc_STRVAR(cp_option_doc, "\
Option(name, value)\n\
--\n\
\n\
Simple customizable user option.");

/* type setup */
static PyMemberDef CpOption_Members[] = {
  { "name",
    T_OBJECT,
    offsetof(CpOptionObject, name),
    READONLY,
    PyDoc_STR("The name of this option (must be unique).") },
  { "value",
    T_OBJECT,
    offsetof(CpOptionObject, value),
    0,
    PyDoc_STR("The value of this option (optional).") },
  { NULL } /* Sentinel */
};

PyTypeObject CpOption_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(Option),
  .tp_basicsize = sizeof(CpOptionObject),
  .tp_dealloc = (destructor)cp_option_dealloc,
  .tp_repr = (reprfunc)cp_option_repr,
  .tp_hash = (hashfunc)cp_option_hash,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_doc = cp_option_doc,
  .tp_richcompare = (richcmpfunc)cp_option_richcmp,
  .tp_members = CpOption_Members,
  .tp_init = (initproc)cp_option_init,
  .tp_new = cp_option_new,
};

/* init */
int
cp_option__mod_types()
{
  CpModule_SetupType(&CpOption_Type, -1);
  return 0;
}

void
cp_option__mod_clear(PyObject* m, _modulestate* state)
{
}

int
cp_option__mod_init(PyObject* m, _modulestate* state)
{
  CpModule_AddObject(CpOption_NAME, &CpOption_Type, -1);
  return 0;
}