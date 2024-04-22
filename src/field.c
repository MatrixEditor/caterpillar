/* field implementation */
#include <stdbool.h>

#include "caterpillar/arch.h"
#include "caterpillar/atomobj.h"
#include "caterpillar/field.h"
#include "caterpillar/module.h"
#include "caterpillar/option.h"
#include "structmember.h"

/* impl */
static PyObject*
cp_field_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpFieldObject* self;
  self = (CpFieldObject*)type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->m_name = PyUnicode_FromString("_");
  self->m_atom = NULL;
  self->m_endian = NULL;
  self->m_offset = NULL;
  self->m_arch = NULL;
  self->m_length = NULL;

  Py_XINCREF(CpInvalidDefault);
  self->m_default = CpInvalidDefault;
  self->m_switch = NULL;
  self->m_options = NULL;
  self->m_condition = Py_NewRef(Py_True);

  // internal state
  self->s_size = false;
  self->s_type = false;
  self->s_sequential = false;
  self->s_keep_pos = true;
  return (PyObject*)self;
}

static void
cp_field_dealloc(CpFieldObject* self)
{

  Py_XDECREF(self->m_name);
  Py_XDECREF(self->m_endian);
  Py_XDECREF(self->m_offset);
  Py_XDECREF(self->m_arch);
  Py_XDECREF(self->m_length);
  Py_XDECREF(self->m_default);
  Py_XDECREF(self->m_switch);
  Py_XDECREF(self->m_options);
  Py_XDECREF(self->m_condition);
  Py_XDECREF(self->m_atom);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
cp_field_repr(CpFieldObject* self)
{
  return PyUnicode_FromFormat("<CpField %R>", self->m_name);
}

static int
cp_field_set_length(CpFieldObject* self, PyObject* value, void* closure);

static int
cp_field_set_offset(CpFieldObject* self, PyObject* value, void* closure);

static int
cp_field_init(CpFieldObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "atom",    "name",      "endian",  "offset",
                            "arch",    "length",    "default", "switch",
                            "options", "condition", NULL };
  PyObject *name = NULL, *endian = NULL, *offset = NULL, *arch = NULL,
           *length = NULL, *default_ = NULL, *switch_ = NULL, *options = NULL,
           *condition = NULL, *atom = NULL;
  if (!PyArg_ParseTupleAndKeywords(args,
                                   kw,
                                   "O|UOOOOOOOO",
                                   kwlist,
                                   &atom,
                                   &name,
                                   &endian,
                                   &offset,
                                   &arch,
                                   &length,
                                   &default_,
                                   &switch_,
                                   &options,
                                   &condition))
    return -1;

  _modulestate* state = get_global_module_state();

  _Cp_SetObj(self->m_name, name);
  _Cp_SetObj(self->m_endian, endian);
  _Cp_SetObj(self->m_arch, arch);

  _Cp_SetObj(self->m_default, default_);
  _Cp_SetObj(self->m_switch, switch_);
  _Cp_SetObj(self->m_options, options);
  _Cp_SetObj(self->m_condition, condition);
  _Cp_SetObj(self->m_atom, atom);

  if (!self->m_options) {
    self->m_options = PySet_New(NULL);
    if (!self->m_options)
      return -1;

    if (PySet_Add(self->m_options, state->cp_option__keep_position) < 0) {
      return -1;
    };
  }

  if (!self->m_atom || self->m_atom == Py_None) {
    PyErr_SetString(PyExc_ValueError, "atom is required");
    return -1;
  }

  if (!PyObject_IsInstance(self->m_atom, (PyObject*)&CpAtom_Type)) {
    if (!PyCallable_Check(self->m_atom)) {
      PyErr_SetString(PyExc_ValueError,
                      "atom must be an instace of atom or a callable function");
      return -1;
    }
  }

  if (!self->m_arch) {
    _Cp_SetObj(self->m_arch, state->cp_arch__host);
  }
  if (!self->m_endian) {
    _Cp_SetObj(self->m_endian, state->cp_endian__native);
  }

  if (length)
    if (cp_field_set_length(self, length, NULL) < 0)
      return -1;
  if (offset)
    if (cp_field_set_offset(self, offset, NULL) < 0)
      return -1;

  self->s_size = CpAtom_HasSize(self->m_atom);
  self->s_type = CpAtom_HasType(self->m_atom);
  return 0;
}

static PyObject*
cp_field_get_length(CpFieldObject* self)
{
  return Py_NewRef(self->m_length ? self->m_length : Py_None);
}

static int
cp_field_set_length(CpFieldObject* self, PyObject* value, void* closure)
{
  if (!value || value == Py_None ||
      (!PyLong_Check(value) && !PyCallable_Check(value) &&
       !PyObject_IsInstance(value, (PyObject*)&PyEllipsis_Type) &&
       !PyObject_IsInstance(value, (PyObject*)&PySlice_Type))) {
    PyErr_SetString(PyExc_TypeError,
                    "length must be an integer, context lambda or a special "
                    "type");
    return -1;
  }

  _Cp_SetObj(self->m_length, value);
  _modulestate* state = get_global_module_state();

  int8_t is_number = PyLong_Check(value);

  if (is_number && PyLong_AsSize_t(self->m_length) <= 1) {
    // remove sequential option automatically
    PySet_Discard(self->m_options, state->cp_option__sequential);
    self->s_sequential = false;
  } else {
    PySet_Add(self->m_options, state->cp_option__sequential);
    self->s_sequential = true;
  }

  if (!is_number) {
    PySet_Add(self->m_options, state->cp_option__dynamic);
  } else {
    PySet_Discard(self->m_options, state->cp_option__dynamic);
  }
  return 0;
}

static PyObject*
cp_field_get_offset(CpFieldObject* self)
{
  return Py_NewRef(self->m_offset ? self->m_offset : Py_None);
}

static int
cp_field_set_offset(CpFieldObject* self, PyObject* value, void* closure)
{
  if (!value || value == Py_None ||
      (!PyLong_Check(value) && !PyCallable_Check(value))) {
    PyErr_SetString(PyExc_TypeError,
                    "offset must be an integer or a context lambda");
    return -1;
  }

  _Cp_SetObj(self->m_offset, value);
  _modulestate* state = get_global_module_state();
  if (PyLong_Check(self->m_offset) && PyLong_AsSize_t(self->m_offset) != -1) {
    PySet_Discard(self->m_options, state->cp_option__keep_position);
    self->s_keep_pos = false;
  } else {
    PySet_Add(self->m_options, state->cp_option__keep_position);
    self->s_keep_pos = true;
  }
  return 0;
}

static PyObject*
cp_field_get_switch(CpFieldObject* self)
{
  return Py_NewRef(self->m_switch ? self->m_switch : Py_None);
}

static int
cp_field_set_switch(CpFieldObject* self, PyObject* value, void* closure)
{
  if (!value || value == Py_None ||
      (!PyCallable_Check(value) && !PyDict_Check(value))) {
    PyErr_SetString(PyExc_TypeError,
                    "switch must be a callable or a dictionary");
    return -1;
  }

  _Cp_SetObj(self->m_switch, value);
  return 0;
}

static PyObject*
cp_field_get_condition(CpFieldObject* self)
{
  return Py_NewRef(self->m_condition ? self->m_condition : Py_None);
}

static int
cp_field_set_condition(CpFieldObject* self, PyObject* value, void* closure)
{
  if (!value || value == Py_None ||
      (!PyCallable_Check(value) && !PyBool_Check(value))) {
    PyErr_SetString(PyExc_TypeError,
                    "condition must be a callable or a boolean");
    return -1;
  }

  _Cp_SetObj(self->m_condition, value);
  return 0;
}

static PyObject*
cp_field_as_number_matmul(CpFieldObject* self, PyObject* other)
{
  if (cp_field_set_offset(self, other, NULL) < 0) {
    return NULL;
  }
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_number_or(CpFieldObject* self, PyObject* other)
{
  if (!other || other->ob_type != &CpOption_Type) {
    Py_RETURN_NOTIMPLEMENTED;
  }

  PySet_Add(self->m_options, other);
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_number_xor(CpFieldObject* self, PyObject* other)
{
  if (!other || other->ob_type != &CpOption_Type) {
    Py_RETURN_NOTIMPLEMENTED;
  }

  PySet_Discard(self->m_options, other);
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_number_rshift(CpFieldObject* self, PyObject* other)
{
  if (cp_field_set_switch(self, other, NULL) < 0) {
    return NULL;
  }
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_number_floordiv(CpFieldObject* self, PyObject* other)
{
  if (cp_field_set_condition(self, other, NULL) < 0) {
    return NULL;
  }
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_number_add(CpFieldObject* self, PyObject* other)
{
  if (!other || other->ob_type != &CpEndian_Type) {
    Py_RETURN_NOTIMPLEMENTED;
  }
  _Cp_SetObj(self->m_endian, other);
  return Py_NewRef((PyObject*)self);
}

static PyObject*
cp_field_as_mapping_getitem(CpFieldObject* self, PyObject* key)
{
  // allow multiple dimensions
  if (cp_field_set_length(self, key, NULL) < 0) {
    return NULL;
  }
  return Py_NewRef((PyObject*)self);
}

/* Public API */
int
CpField_HasCondition(CpFieldObject* self)
{
  return !Py_IsTrue(self->m_condition);
}

int
CpField_IsEnabled(CpFieldObject* self, PyObject* context)
{
  if (self->m_condition == NULL) {
    return true;
  }

  if (PyCallable_Check(self->m_condition)) {
    PyObject* result = PyObject_CallOneArg(self->m_condition, context);
    if (result == NULL) {
      return -1;
    }
    int truth = PyObject_IsTrue(result);
    Py_DECREF(result);
    return truth;
  }

  return PyObject_IsTrue(self->m_condition);
}

Py_ssize_t
CpField_GetOffset(CpFieldObject* self, PyObject* context)
{
  Py_ssize_t offset = -1;
  if (self->m_offset != NULL) {

    if (PyCallable_Check(self->m_offset)) {
      PyObject* result = PyObject_CallOneArg(self->m_offset, context);
      if (result == NULL) {
        return -1;
      }
      offset = PyLong_AsSsize_t(result);
      Py_DECREF(result);
    } else {
      offset = PyLong_AsSsize_t(self->m_offset);
    }
  }
  return offset;
}

PyObject*
CpField_EvalSwitch(CpFieldObject* self, PyObject* op, PyObject* context)
{
  if (self->m_switch == NULL) {
    PyErr_SetString(PyExc_TypeError, "field does not have a switch");
    return NULL;
  }

  PyObject* result = NULL;
  if (PyCallable_Check(self->m_switch)) {
    result = PyObject_CallOneArg(self->m_switch, context);
    if (!result)
      return NULL;
  } else {
    result = PyObject_GetItem(self->m_switch, op);
    if (!result) {
      result = PyObject_GetItem(self->m_switch, CpInvalidDefault);
      if (!result)
        return NULL;
    }
  }

  // TODO: check for nested struct
  return result;
}

PyObject*
CpField_GetLength(CpFieldObject* self, PyObject* context)
{
  if (self->m_length == NULL) {
    PyErr_SetString(PyExc_TypeError, "field does not have a length");
    return NULL;
  }

  if (PyCallable_Check(self->m_length)) {
    PyObject* result = PyObject_CallOneArg(self->m_length, context);
    if (!result)
      return NULL;
    return result;
  }
  return Py_NewRef(self->m_length);
}

/* docs */

/* members */
static PyMemberDef CpField_Members[] = {
  { "name", T_OBJECT, offsetof(CpFieldObject, m_name), 0 },
  { "default", T_OBJECT, offsetof(CpFieldObject, m_default), 0 },
  { "options", T_OBJECT, offsetof(CpFieldObject, m_options), 0 },
  { "atom", T_OBJECT, offsetof(CpFieldObject, m_atom), READONLY },
  { "endian", T_OBJECT, offsetof(CpFieldObject, m_endian), 0 },
  { "arch", T_OBJECT, offsetof(CpFieldObject, m_arch), 0 },
  { NULL } /* Sentinel */
};

static PyGetSetDef CpField_GetSetters[] = {
  { "length",
    (getter)cp_field_get_length,
    (setter)cp_field_set_length,
    NULL,
    NULL },
  { "offset",
    (getter)cp_field_get_offset,
    (setter)cp_field_set_offset,
    NULL,
    NULL },
  { "switch",
    (getter)cp_field_get_switch,
    (setter)cp_field_set_switch,
    NULL,
    NULL },
  { "condition",
    (getter)cp_field_get_condition,
    (setter)cp_field_set_condition,
    NULL,
    NULL },
  { NULL } /* Sentinel */
};

static PyNumberMethods CpField_NumberMethods = {
  .nb_matrix_multiply = (binaryfunc)cp_field_as_number_matmul,
  .nb_or = (binaryfunc)cp_field_as_number_or,
  .nb_xor = (binaryfunc)cp_field_as_number_xor,
  .nb_rshift = (binaryfunc)cp_field_as_number_rshift,
  .nb_floor_divide = (binaryfunc)cp_field_as_number_floordiv,
  .nb_add = (binaryfunc)cp_field_as_number_add,
};

static PyMappingMethods CpField_MappingMethods = {
  .mp_subscript = (binaryfunc)cp_field_as_mapping_getitem,
};

static PyMethodDef CpField_Methods[] = {
  //   { "__type__", (PyCFunction)cp_typeof_field, METH_NOARGS },
  { NULL } /* Sentinel */
};

/* type */
PyTypeObject CpField_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(Field),
  sizeof(CpFieldObject),        /* tp_basicsize */
  0,                            /* tp_itemsize */
  (destructor)cp_field_dealloc, /* tp_dealloc */
  0,                            /* tp_vectorcall_offset */
  0,                            /* tp_getattr */
  0,                            /* tp_setattr */
  0,                            /* tp_as_async */
  (reprfunc)cp_field_repr,      /* tp_repr */
  &CpField_NumberMethods,       /* tp_as_number */
  0,                            /* tp_as_sequence */
  &CpField_MappingMethods,      /* tp_as_mapping */
  0,                            /* tp_hash */
  0,                            /* tp_call */
  0,                            /* tp_str */
  0,                            /* tp_getattro */
  0,                            /* tp_setattro */
  0,                            /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,           /* tp_flags */
  NULL,                         /* tp_doc */
  0,                            /* tp_traverse */
  0,                            /* tp_clear */
  0,                            /* tp_richcompare */
  0,                            /* tp_weaklistoffset */
  0,                            /* tp_iter */
  0,                            /* tp_iternext */
  CpField_Methods,              /* tp_methods */
  CpField_Members,              /* tp_members */
  CpField_GetSetters,           /* tp_getset */
  0,                            /* tp_base */
  0,                            /* tp_dict */
  0,                            /* tp_descr_get */
  0,                            /* tp_descr_set */
  0,                            /* tp_dictoffset */
  (initproc)cp_field_init,      /* tp_init */
  0,                            /* tp_alloc */
  (newfunc)cp_field_new,        /* tp_new */
  0,                            /* tp_free */
  0,                            /* tp_is_gc */
  0,                            /* tp_bases */
  0,                            /* tp_mro */
  0,                            /* tp_cache */
  0,                            /* tp_subclasses */
  0,                            /* tp_weaklist */
  0,                            /* tp_del */
  0,                            /* tp_version_tag */
  0,                            /* tp_finalize */
  0,                            /* tp_vectorcall */
  0,                            /* tp_watched */
};