#include "caterpillar/caterpillar.h"
#include "private.h"

#include <structmember.h>

// ------------------------------------------------------------------------------
// length info

static PyObject*
cp_lengthinfo_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpLengthInfoObject* self = NULL;
  if ((self = _Cp_CAST(CpLengthInfoObject*, type->tp_alloc(type, 0)), !self)) {
    return NULL;
  }

  self->m_greedy = 0;
  self->m_length = 0;
  return _Cp_CAST(PyObject*, self);
}

static void
cp_lengthinfo_dealloc(CpLengthInfoObject* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_lengthinfo_init(CpLengthInfoObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "length", "greedy", NULL };
  Py_ssize_t length = 0;
  int greedy = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kw, "|ni", kwlist, &length, &greedy)) {
    return -1;
  }

  self->m_length = length;
  self->m_greedy = greedy;
  return 0;
}

static PyObject*
cp_lengthinfo_repr(CpLengthInfoObject* self)
{
  if (self->m_greedy) {
    return PyUnicode_FromString("<LengthInfo [greedy]>");
  }
  return PyUnicode_FromFormat("<LengthInfo [%d]>", self->m_length);
}

static PyMemberDef CpLengthInfo_Members[] = {
  { "length", T_PYSSIZET, offsetof(CpLengthInfoObject, m_length), 0, NULL },
  { "greedy", T_BOOL, offsetof(CpLengthInfoObject, m_greedy), 0, NULL },
  { NULL } /* Sentinel */
};

PyTypeObject CpLengthInfo_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_NameStr(CpLengthInfo_NAME),
  .tp_basicsize = sizeof(CpLengthInfoObject),
  .tp_dealloc = (destructor)cp_lengthinfo_dealloc,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_new = (newfunc)cp_lengthinfo_new,
  .tp_init = (initproc)cp_lengthinfo_init,
  .tp_repr = (reprfunc)cp_lengthinfo_repr,
  .tp_doc = NULL,
};

/* init */
int
cp_lengthinfo__mod_types()
{
  CpModule_SetupType(&CpLengthInfo_Type, -1);
  return 0;
}

void
cp_lengthinfo__mod_clear(PyObject* m, _modulestate* state)
{
}

int
cp_lengthinfo__mod_init(PyObject* m, _modulestate* state)
{
  CpModule_AddObject(CpLengthInfo_NAME, &CpLengthInfo_Type, -1);
  return 0;
}