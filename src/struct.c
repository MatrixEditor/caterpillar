/* struct and struct-field-info implementation */
#include <stdbool.h>

#include "caterpillar/arch.h"
#include "caterpillar/atomobj.h"
#include "caterpillar/field.h"
#include "caterpillar/parsing.h"
#include "caterpillar/struct.h"
#include <structmember.h>

/* struct-field-info implementation */
static PyObject*
cp_struct_fieldinfo_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpStructFieldInfoObject* self =
    (CpStructFieldInfoObject*)type->tp_alloc(type, 0);
  if (!self) {
    return NULL;
  }
  self->m_field = NULL;
  self->s_excluded = false;
  return (PyObject*)self;
}

static void
cp_struct_fieldinfo_dealloc(CpStructFieldInfoObject* self)
{
  Py_XDECREF(self->m_field);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_struct_fieldinfo_init(CpStructFieldInfoObject* self,
                         PyObject* args,
                         PyObject* kw)
{
  static char* kwlist[] = { "field", "excluded", NULL };
  PyObject* field = NULL;
  int excluded = false;

  if (!PyArg_ParseTupleAndKeywords(
        args, kw, "O|p", kwlist, &field, &excluded)) {
    return -1;
  }

  if (!field) {
    PyErr_SetString(PyExc_ValueError, "field is NULL!");
    return -1;
  }

  if (!CpField_Check(field)) {
    PyErr_SetString(PyExc_ValueError, "field is not a field!");
    return -1;
  }

  Py_XSETREF(self->m_field, (CpFieldObject*)Py_XNewRef(field));
  self->s_excluded = excluded;
  return 0;
}

static PyObject*
cp_struct_fieldinfo_repr(CpStructFieldInfoObject* self)
{
  return PyUnicode_FromFormat("<CpStructFieldInfo of %R>",
                              self->m_field->m_name);
}

/* public API */
CpStructFieldInfoObject*
CpStructFieldInfo_New(CpFieldObject* field)
{
  return (CpStructFieldInfoObject*)CpObject_CreateOneArg(
    &CpStructFieldInfo_Type, (PyObject*)field);
}

/* docs */

/* type */
static PyMemberDef CpStructFieldInfo_Members[] = {
  { "field",
    T_OBJECT,
    offsetof(CpStructFieldInfoObject, m_field),
    READONLY,
    NULL },
  { "excluded",
    T_BOOL,
    offsetof(CpStructFieldInfoObject, s_excluded),
    READONLY,
    NULL },
  { NULL } /* Sentinel */
};

PyTypeObject CpStructFieldInfo_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(fieldinfo),
  sizeof(CpStructFieldInfoObject),         /* tp_basicsize */
  0,                                       /* tp_itemsize */
  (destructor)cp_struct_fieldinfo_dealloc, /* tp_dealloc */
  0,                                       /* tp_vectorcall_offset */
  0,                                       /* tp_getattr */
  0,                                       /* tp_setattr */
  0,                                       /* tp_as_async */
  (reprfunc)cp_struct_fieldinfo_repr,      /* tp_repr */
  0,                                       /* tp_as_number */
  0,                                       /* tp_as_sequence */
  0,                                       /* tp_as_mapping */
  0,                                       /* tp_hash */
  0,                                       /* tp_call */
  0,                                       /* tp_str */
  0,                                       /* tp_getattro */
  0,                                       /* tp_setattro */
  0,                                       /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,                      /* tp_flags */
  NULL,                                    /* tp_doc */
  0,                                       /* tp_traverse */
  0,                                       /* tp_clear */
  0,                                       /* tp_richcompare */
  0,                                       /* tp_weaklistoffset */
  0,                                       /* tp_iter */
  0,                                       /* tp_iternext */
  0,                                       /* tp_methods */
  CpStructFieldInfo_Members,               /* tp_members */
  0,                                       /* tp_getset */
  0,                                       /* tp_base */
  0,                                       /* tp_dict */
  0,                                       /* tp_descr_get */
  0,                                       /* tp_descr_set */
  0,                                       /* tp_dictoffset */
  (initproc)cp_struct_fieldinfo_init,      /* tp_init */
  0,                                       /* tp_alloc */
  (newfunc)cp_struct_fieldinfo_new,        /* tp_new */
  0,                                       /* tp_free */
  0,                                       /* tp_is_gc */
  0,                                       /* tp_bases */
  0,                                       /* tp_mro */
  0,                                       /* tp_cache */
  0,                                       /* tp_subclasses */
  0,                                       /* tp_weaklist */
  0,                                       /* tp_del */
  0,                                       /* tp_version_tag */
  0,                                       /* tp_finalize */
  0,                                       /* tp_vectorcall */
  0,                                       /* tp_watched */
};

// ----------------------------------------------------------------------------
// struct

/* private API */
static inline PyObject*
CpStruct_GetMethodResolutionOrder(CpStructObject* self)
{
  // state is optional
  return PyObject_GetAttr((PyObject*)self->m_model, self->s_mod->str___mro__);
}

static PyObject*
CpStruct_GetReverseMRO(CpStructObject* self)
{
  PyObject *mro = CpStruct_GetMethodResolutionOrder(self), *start = NULL,
           *stop = NULL, *step = NULL, *slice = NULL, *result = NULL;
  if (!mro) {
    return NULL;
  }

  start = PyLong_FromSsize_t(-1), stop = PyLong_FromSsize_t(0),
  step = PyLong_FromSsize_t(-1);
  if (!start || !stop || !step) {
    goto cleanup;
  }

  slice = PySlice_New(start, stop, step);
  if (!slice) {
    goto cleanup;
  }

  result = PyObject_GetItem(mro, slice);
cleanup:
  Py_XDECREF(start);
  Py_XDECREF(stop);
  Py_XDECREF(step);
  Py_XDECREF(slice);
  Py_XDECREF(mro);
  return result;
}

static inline int
CpStructModel_SetDefault(CpStructObject* o, PyObject* name, PyObject* value)
{
  if (!name) {
    PyErr_SetString(PyExc_TypeError, "name must be a string");
    return -1;
  }

  return PyObject_SetAttr((PyObject*)o->m_model, name, value);
}

static inline PyObject*
CpStructModel_GetValue(CpStructObject* o, PyObject* instance, PyObject* name)
{
  PyObject* value = PyObject_GetAttr(instance, name);
  if (!value) {
    return NULL;
  }
  return value;
}

static inline PyObject*
CpStructModel_GetDefaultValue(CpStructObject* o, PyObject* name)
{
  PyObject* value = PyObject_GetAttr((PyObject*)o->m_model, name);
  if (!value) {
    PyErr_Clear();
    return Py_NewRef(CpInvalidDefault);
  }
  return value;
}

/* impl */
static PyObject*
cp_struct_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
  CpStructObject* self = (CpStructObject*)type->tp_alloc(type, 0);
  if (!self) {
    return NULL;
  }
  self->m_model = NULL;
  self->m_options = NULL;
  self->m_members = NULL;
  self->s_union = false;
  self->s_kwonly = false;
  self->s_mod = get_global_module_state();
  self->s_alter_type = false;
  self->m_endian = Py_NewRef(self->s_mod->cp_endian__native);
  self->m_arch = Py_NewRef(self->s_mod->cp_arch__host);
  self->m_field_options = PySet_New(NULL);
  if (!self->m_field_options) {
    return NULL;
  }
  self->s_kwonly_init_fields = PyList_New(0);
  if (!self->s_kwonly_init_fields) {
    return NULL;
  }
  self->s_std_init_fields = PyList_New(0);
  if (!self->s_std_init_fields) {
    return NULL;
  }
  return (PyObject*)self;
}

static void
cp_struct_dealloc(CpStructObject* self)
{
  Py_XDECREF(self->m_model);
  Py_XDECREF(self->m_options);
  Py_XDECREF(self->m_members);
  Py_XDECREF(self->m_endian);
  Py_XDECREF(self->m_arch);
  Py_XDECREF(self->m_field_options);
  Py_XDECREF(self->s_kwonly_init_fields);
  Py_XDECREF(self->s_std_init_fields);
  self->s_kwonly = false;
  self->s_mod = NULL;
  self->s_union = false;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
cp_struct_prepare(CpStructObject* self);

static int
cp_struct_import_bases(CpStructObject* self);

static int
cp_struct_process_annotation(CpStructObject* self,
                             PyObject* name,
                             PyObject* annotation,
                             PyObject* default_value,
                             int exclude);

static int
cp_struct_create_type(CpStructObject* self);

static int
cp_struct_add_slots(CpStructObject* self);

static int
cp_struct_init(CpStructObject* self, PyObject* args, PyObject* kw)
{
  static char* kwlist[] = { "model",         "options",     "endian", "arch",
                            "field_options", "alter_model", NULL };
  PyObject *model = NULL, *options = NULL, *endian = NULL, *arch = NULL,
           *field_options = NULL;
  int alter_model = false;
  if (!PyArg_ParseTupleAndKeywords(args,
                                   kw,
                                   "O|OOOOp",
                                   kwlist,
                                   &model,
                                   &options,
                                   &endian,
                                   &arch,
                                   &field_options,
                                   &alter_model)) {
    return -1;
  }

  if (!model || !PyType_Check(model)) {
    PyErr_Format(PyExc_TypeError, "model %R must be a type", model);
    return -1;
  }
  if (CpStructModel_Check(model, self->s_mod)) {
    PyErr_SetString(PyExc_TypeError, "model must not be a struct container");
    return -1;
  }

  Py_XSETREF(self->m_model, (PyTypeObject*)Py_NewRef(model));
  if (!options) {
    self->m_options = PySet_New(NULL);
    if (!self->m_options) {
      return -1;
    }
  } else {
    if (!PySet_Check(options)) {
      PyErr_SetString(PyExc_TypeError, "options must be a set");
      return -1;
    }
    Py_XSETREF(self->m_options, Py_NewRef(options));
  }

  if (_PySet_Update(self->m_options,
                    self->s_mod->cp_option__global_struct_options) < 0) {
    return -1;
  };

  self->s_alter_type = alter_model;
  self->s_union =
    PySet_Contains(self->m_options, self->s_mod->cp_option__union);

  self->m_members = PyDict_New();
  if (!self->m_members) {
    return -1;
  }

  if (endian) {
    if (endian->ob_type == &CpEndian_Type) {
      _Cp_SetObj(self->m_endian, endian);
    } else {
      PyErr_SetString(PyExc_TypeError, "endian must be an Endian instance");
      return -1;
    }
  }

  if (arch) {
    if (arch->ob_type == &CpArch_Type) {
      _Cp_SetObj(self->m_arch, arch);
    } else {
      PyErr_SetString(PyExc_TypeError, "arch must be an Arch instance");
      return -1;
    }
  }

  if (field_options) {
    if (!PySet_Check(field_options)) {
      PyErr_SetString(PyExc_TypeError, "field_options must be a set");
      return -1;
    }
    Py_XSETREF(self->m_field_options, Py_NewRef(field_options));
  }
  return cp_struct_prepare(self);
}

static int
cp_struct_prepare(CpStructObject* self)
{
  // Generic struct implementation:
  // 1. Process all base classes and import fields from them. All fields
  //    means that that also "excluded" fields will be imported to this
  //    object.
  //
  // 2. Process all annotations from the given model. The annotations will
  //    be evaluated first by the *inspect* module and then copied to get
  //    converted to CpField instances.
  //
  // 3. The third and last step involves the tricky part about native type
  //    creation. It will add "__slots__" if desired and create a new class
  //    based on the current with the same fields and same base classes.
  _modulestate* state = self->s_mod;
  int res = 0, had_default = false;

  // First, create a set[str] that will store all field names that won't be
  // visible in the final class but are used in the struct representation.
  //
  // Fields of this category are: unnamed fields and constant fields (if
  // the according option allows to discard them).
  PyObject* discardable = PySet_New(NULL);
  if (!discardable) {
    return -1;
  }

  // As described in step (1), we first import fields from base classes that
  // themselfs store a struct instance (conforming to the StructContainer
  // protocol).
  res = cp_struct_import_bases(self);
  if (res < 0) {
    return -1;
  }

  // As described in step (2), we then import all annotations from the
  // model. Before that, we need to check whether to evaluate the
  // placed annotations.
  int eval = PySet_Contains(self->m_options, state->cp_option__eval);
  if (eval < 0) {
    return -1;
  }
  PyObject *model_annotations = CpStruct_GetAnnotations(self, eval),
           *name = NULL, *annotation = NULL;
  if (!model_annotations) {
    return -1;
  }

  // The structure of a class annotation may be as follows:
  //
  //  class Format:
  //    [ with <condition>: ]
  //        <name>: <type> [ = <default> ]
  //
  // Where <type> can be any object conforming to the Atom protocol, or a
  // special variant of:
  //
  //  - Any type conforming to the StructContainer protocol
  //  - Constants: str, bytes
  //  - Callables that conform to the ContextLambda protocol
  //  - Enum types
  //
  // More detailed information on how each annotation is processed can be
  // found in the cp_struct_process_annotation().
  Py_ssize_t pos = 0;
  while ((res = PyDict_Next(model_annotations, &pos, &name, &annotation))) {
    if (res < 0) {
      return -1;
    }
    PyObject *default_ = NULL, *atom = annotation;
    int excluded = false;

    default_ = CpStructModel_GetDefaultValue(self, name);
    if (!default_) {
      Py_XDECREF(discardable);
      return -1;
    }
    // Constant values that are not in the form of fields. A special case are
    // definitions using the 'Const' class for example.
    if (CpField_Check(annotation)) {
      atom = annotation;
      // SPECIAL CASE: If the field has a condition linked to it, a default
      // value of None is inferred.
      if (CpField_HasCondition((CpFieldObject*)annotation) &&
          Cp_IsInvalidDefault(default_)) {
        _Cp_SetObj(default_, Py_None);
      }
    }

    // SPECIAL CASE: If this struct is a union, we will infer None as the
    // default value (if none has been set already)
    if (self->s_union && Cp_IsInvalidDefault(default_)) {
      _Cp_SetObj(default_, Py_None);
    }

    if (!Cp_IsInvalidDefault(default_)) {
      had_default = true;
    } else {
      if (had_default) {
        // By default, we allow definitions of classes with positional
        // arguments. That feature will be disabled if a non-default
        // field definition follows a field with a default value.
        self->s_kwonly = true;
      }
    }

    // Next, we check whether the field should be excluded from the
    // final model type.
    if ((res = PySet_Contains(self->m_options,
                              state->cp_option__discard_unnamed))) {
      if (res < 0) {
        Py_XDECREF(default_);
        Py_XDECREF(discardable);
        return -1;
      }
      // Definition 'unnamed fields':
      // Unnamed fields refer to fields in a struct or sequence which names
      // begin with an underscore followed by zero or more numeric digits.
      PyObject* match_ = PyObject_CallMethodObjArgs(
        state->cp_regex__unnamed, state->str_pattern_match, name, NULL);
      if (!match_) {
        Py_XDECREF(default_);
        Py_XDECREF(discardable);
        return -1;
      }
      if (!Py_IsNone(match_)) {
        excluded = true;
      }
      Py_XDECREF(match_);
    } else
      excluded = false;

    if (excluded) {
      PySet_Add(discardable, name);
    }

    res =
      cp_struct_process_annotation(self, name, annotation, default_, excluded);
    Py_XSETREF(default_, NULL);
    if (res < 0) {
      Py_XDECREF(discardable);
      return -1;
    }
  }

  // before we create the new type, discard all marked fields
  PyObject* annotations =
    PyObject_GetAttr((PyObject*)self->m_model, state->str___annotations__);
  if (!annotations) {
    Py_XDECREF(discardable);
    return -1;
  }

  PyObject* iter = PyObject_GetIter(discardable);
  if (!iter) {
    Py_XDECREF(discardable);
    Py_XDECREF(annotations);
    return -1;
  }

  PyObject* item = NULL;
  while ((item = PyIter_Next(iter))) {
    if (PyDict_DelItem(annotations, item)) {
      Py_XDECREF(discardable);
      Py_XDECREF(annotations);
      return -1;
    }
  }
  Py_XDECREF(iter);
  Py_XDECREF(discardable);
  Py_XDECREF(annotations);
  return self->s_alter_type ? cp_struct_create_type(self) : 0;
}

static int
cp_struct_import_bases(CpStructObject* self)
{
  // We will inspect all base classes in reverse order and selectively
  // utilize classes that store a struct instance.
  PyObject* bases = CpStruct_GetReverseMRO(self);
  if (!bases) {
    return -1;
  }

  // All object references here are borrowed.
  PyObject *base = NULL, *field = NULL, *name = NULL;
  CpStructObject* struct_ = NULL;
  Py_ssize_t bases_length = PyTuple_GET_SIZE(bases);
  for (Py_ssize_t i = 0; i < bases_length; i++) {
    // For simplicity, we will discard all invalid base classes
    // that can't be displayed as types, e.g. partial template
    // types.
    base = PyTuple_GetItem(bases, i);
    if (!PyType_Check(base)) {
      continue;
    }

    if (!CpStructModel_Check(base, self->s_mod)) {
      continue;
    }

    // NOTE:
    // Importing all fields instead of the entire struct here. This
    // action will just add fields to this object using the order of
    // the given struct.
    struct_ = (CpStructObject*)CpStructModel_GetStruct(base, self->s_mod);
    if (!struct_) {
      return -1;
    }

    while (PyDict_Next(struct_->m_members, NULL, &name, &field)) {
      // The check for duplicates is done in the called function.
      if (CpStruct_AddFieldInfo(self, (CpStructFieldInfoObject*)field) < 0) {
        Py_XDECREF(struct_);
        return -1;
      }
    }
    Py_XDECREF(struct_);
  }
  return 0;
}

static int
cp_struct_process_annotation(CpStructObject* self,
                             PyObject* name,
                             PyObject* annotation,
                             PyObject* default_value,
                             int exclude)
{
  // As described before in cp_struct_prepare, a field definition follows
  // the following schema:
  //
  //    <name>: <annotation> [ = <default> ]
  //
  // Where the name is a string, the annotation is an object conforming that
  // is convertible to a CpField object, and the default value can be any
  // object.
  // It is worthwhile to note that the default value specified here will be
  // assigned to the created field instance. There is no destinction between
  // class-level defaults and field-level defaults.
  CpFieldObject* field = NULL;
  _modulestate* state = self->s_mod;

  {
    // 1. Annotated field:
    // The annotation is already a CpField object, so we don't need to convert
    // it. Note thate we check against the *exact* type, which means that we
    // will not accept any subclass of CpField.
    if (CpField_CheckExact(annotation)) {
      field = (CpFieldObject*)Py_NewRef(annotation);
    }

    // 2. Atom object or protocol
    // The annotation is an instance of a subclass of the CpAtom class OR it
    // conforms to the Atom protocol.
    //
    // The annotation conforms to the Atom protocol. Note that we check here
    // only against packing, unpacking and size calculation. The type function
    // is optional and won't be covered here.
    else if (CpAtom_Check(annotation)) {
      field = (CpFieldObject*)CpField_New(annotation);
      if (!field) {
        return -1;
      }
    }

    // 3. Type
    // Here, the annotation may be a custom struct type or an enum type.
    // Currently, only struct container are supported.
    else if (PyType_Check(annotation)) {
      if (CpStructModel_Check(annotation, state)) {
        PyObject* struct_ = CpStructModel_GetStruct(annotation, state);
        if (!struct_) {
          return -1;
        }
        field = (CpFieldObject*)CpField_New(struct_);
        Py_XDECREF(struct_);
        if (!field) {
          return -1;
        }
      }
    }

    // 4. Callable
    // The annotation is a callable object and conforms to the ContextLambda
    // protocol. Note that we assume the right function signature.
    else if (PyCallable_Check(annotation)) {
      field = (CpFieldObject*)CpField_New(annotation);
      if (!field) {
        return -1;
      }
    }
  }

  // Currently, there is no extension support for other types. That is
  // a future feature.
  if (!field) {
    PyErr_Format(
      PyExc_ValueError,
      ("Field %R could not be created, because the placed annotation does not "
       "conform to any of the supported types.\n"
       "annotation: %R"),
      name,
      annotation);
    return -1;
  }

  _Cp_SetObj(field->m_arch, self->m_arch);
  _Cp_SetObj(field->m_endian, self->m_endian);
  _Cp_SetObj(field->m_default, default_value);
  _Cp_SetObj(field->m_name, name);
  if (_PySet_Update(field->m_options, self->m_field_options) < 0) {
    Py_XDECREF(field);
    return -1;
  }

  int res = CpStruct_AddField(self, field, exclude);
  if (res < 0) {
    Py_XDECREF(field);
    return -1;
  }

  if (!Cp_IsInvalidDefault(default_value)) {
    if (CpStructModel_SetDefault(self, field->m_name, default_value) < 0) {
      Py_XDECREF(field);
      return -1;
    }
  }

  // Lastly, we replace the field from the internal model type if it
  // is enabled.
  res = PySet_Contains(self->m_options, state->cp_option__replace_types);
  if (res < 0) {
    Py_XDECREF(field);
    return -1;
  }

  if (res) {
    PyObject* type = CpTypeOf_Field(field);
    if (!type) {
      Py_XDECREF(field);
      return -1;
    }
    if (CpStruct_ReplaceType(self, name, type) < 0) {
      Py_XDECREF(type);
      Py_XDECREF(field);
      return -1;
    }
  }
  return res;
}

static int
_cp_struct_model__init__(PyObject* self, PyObject* args, PyObject* kwnames)
{
  CpStructObject* struct_ =
    (CpStructObject*)CpStructModel_GetStruct(self, NULL);
  if (!struct_) {
    return -1;
  }

  CpStructFieldInfoObject* info = NULL;
  PyObject *key = NULL, *value = NULL;
  Py_ssize_t pos = 0, argc = PyTuple_Size(args),
             stdc = PyList_Size(struct_->s_std_init_fields),
             kwonlyc = PyList_Size(struct_->s_kwonly_init_fields);

  // First, we will iterate over all positional arguments.
  for (Py_ssize_t i = 0; i < stdc; i++) {
    // NOTE here: borrowed reference
    info =
      (CpStructFieldInfoObject*)PyList_GetItem(struct_->s_std_init_fields, i);
    if (!info) {
      return -1;
    }

    if (i >= argc) {
      // If the current positional field is defined as a keyword argument,
      // we should retrieve it from the keyword arguments.
      if (!kwnames || !PyDict_Contains(kwnames, info->m_field->m_name)) {
        Py_XDECREF(struct_);
        PyErr_Format(PyExc_ValueError,
                     ("Missing argument for positional field %R"),
                     info->m_field->m_name);
        return -1;
      }

      value = PyDict_GetItem(kwnames, info->m_field->m_name);
    } else
      value = PyTuple_GetItem(args, i);

    if (!value) {
      Py_XDECREF(struct_);
      return -1;
    }

    // as we store a borrowed reference in 'value', we don't need
    // to decref it.
    if (PyObject_SetAttr(self, info->m_field->m_name, value) < 0) {
      Py_XDECREF(struct_);
      return -1;
    }
  }

  // If no keyword arguments were provided, we are still not done, because
  // default values have to be placed.
  for (Py_ssize_t i = 0; i < kwonlyc; i++) {
    // NOTE here: borrowed reference
    info = (CpStructFieldInfoObject*)PyList_GetItem(
      struct_->s_kwonly_init_fields, i);
    if (!info) {
      Py_XDECREF(struct_);
      return -1;
    }

    // A custom value is only provided if it is in the given keyword
    // arguments.
    if (!kwnames || !PyDict_Contains(kwnames, info->m_field->m_name)) {
      value = info->m_field->m_default;
    } else {
      value = PyDict_GetItem(kwnames, info->m_field->m_name);
    }

    if (!value) {
      Py_XDECREF(struct_);
      return -1;
    }

    // same as before, we don't need to decref the value
    if (PyObject_SetAttr(self, info->m_field->m_name, value) < 0) {
      Py_XDECREF(struct_);
      return -1;
    }
  }

  Py_XDECREF(struct_);
  return 0;
}

static int
cp_struct_create_type(CpStructObject* self)
{
  // At this point, we've already processed all annotated elements
  // of our model. Only if S_SLOTS is enabled, we have to create
  // a new type. Otherwise, we simply create __match_args__
  // and replace the __init__ attribute.
  //
  // TODO: Add support for S_SLOTS
  _modulestate* state = self->s_mod;
  PyObject* dict = self->m_model->tp_dict;
  if (!dict) {
    PyErr_SetString(PyExc_TypeError, "Model is not initialized");
    return -1;
  }

  // Before modifying the actual type, make sure, the struct is
  // stored in the target model.
  if (PyDict_SetItem(dict, state->str___struct__, (PyObject*)self) < 0) {
    return -1;
  }

  if (CpStruct_HasOption(self, state->cp_option__slots)) {
    if (cp_struct_add_slots(self) < 0) {
      return -1;
    }
  }
  self->m_model->tp_init = (initproc)_cp_struct_model__init__;
  return 0;
}

static PyObject*
_cp_struct_inherited_slots(CpStructObject* self)
{
  _modulestate* state = self->s_mod;
  PyObject *inherited_slots = NULL, *mro = NULL, *base_type = NULL,
           *base_types = NULL, *type_slots = NULL, *res = NULL;

  mro = PyObject_GetAttr((PyObject*)self->m_model, state->str___mro__);
  if (!mro) {
    res = NULL;
    goto cleanup;
  }

  base_types = PyTuple_GetSlice(mro, 1, -1);
  if (!base_types) {
    res = NULL;
    goto cleanup;
  }
  inherited_slots = PySet_New(NULL);
  if (!inherited_slots) {
    res = NULL;
    goto cleanup;
  }

  // collect inherited slots
  Py_ssize_t size = PyTuple_GET_SIZE(base_types);
  for (Py_ssize_t i = 0; i < size; i++) {
    base_type = PyTuple_GetItem(base_types, i);
    if (!base_type) {
      res = NULL;
      goto cleanup;
    }

    if (!PyType_Check(base_type)) {
      continue;
    }

    type_slots =
      PyDict_GetItem(((PyTypeObject*)base_type)->tp_dict, state->str___slots__);
    if (!type_slots) {
      res = NULL;
      goto cleanup;
    }

    if (PyUnicode_Check(type_slots)) {
      if (PySet_Add(inherited_slots, type_slots) < 0) {
        res = NULL;
        goto cleanup;
      }
    } else if (PyIter_Check(type_slots)) {
      if (_PySet_Update(inherited_slots, type_slots) < 0) {
        res = NULL;
        goto cleanup;
      }
    } else {
      PyErr_Format(PyExc_ValueError, "Invalid type for slots: %R", type_slots);
      res = NULL;
      goto cleanup;
    }
  }
  res = Py_NewRef(inherited_slots);

cleanup:
  Py_XDECREF(mro);
  Py_XDECREF(inherited_slots);
  Py_XDECREF(base_types);
  return res;
}

static int
cp_struct_add_slots(CpStructObject* self)
{
  _modulestate* state = self->s_mod;
  PyObject *dict = NULL, *inherited_slots = NULL, *slots = NULL, *qualname;
  int res = 0;

  // Make sure, the model type does not already have __slots__
  if (PyObject_HasAttr((PyObject*)self->m_model, state->str___slots__)) {
    PyErr_Format(
      PyExc_ValueError, "Model type %R already has __slots__", self->m_model);
    return -1;
  }

  // We create a new custom class dictionary which will be later passed
  // on to the type creation.
  dict = PyDict_New();
  if (!dict) {
    res = -1;
    goto cleanup;
  }
  if (PyDict_Merge(dict, self->m_model->tp_dict, true) < 0) {
    res = -1;
    goto cleanup;
  }

  // We have to check against overlapping slots, if any.
  inherited_slots = _cp_struct_inherited_slots(self);
  if (!inherited_slots) {
    res = -1;
    goto cleanup;
  }

  // collect slots
  slots = PyList_New(0);
  if (!slots) {
    res = -1;
    goto cleanup;
  }

  PyObject* name = NULL;
  Py_ssize_t pos = 0;
  while (PyDict_Next(self->m_members, &pos, &name, NULL)) {
    if (!PySet_Contains(inherited_slots, name)) {
      if (PyList_Append(slots, name) < 0) {
        res = -1;
        goto cleanup;
      }
    }
  }

  // Get rid of the __dict__ attribute
  PyObject* tmp = _PyDict_Pop(dict, state->str___dict__, NULL);
  Py_XDECREF(tmp);

  // removes existing __weakref__ descriptor - we don't need it,
  // because it belongs to the previous type.
  tmp = _PyDict_Pop(dict, state->str___weakref__, NULL);
  Py_XDECREF(tmp);

  PyObject* tuple = PyList_AsTuple(slots);
  if (!tuple) {
    res = -1;
    goto cleanup;
  }

  if (PyDict_SetItem(dict, state->str___slots__, tuple) < 0) {
    res = -1;
    goto cleanup;
  }

  if (PyObject_HasAttr((PyObject*)self->m_model, state->str___qualname__)) {
    qualname =
      PyObject_GetAttr((PyObject*)self->m_model, state->str___qualname__);
    if (!qualname) {
      res = -1;
      goto cleanup;
    }
  }

  PyObject* new_type = PyObject_CallFunction((PyObject*)&PyType_Type,
                                             "sOO",
                                             self->m_model->tp_name,
                                             self->m_model->tp_bases,
                                             dict);
  if (!new_type) {
    res = -1;
    goto cleanup;
  }

  Py_XSETREF(self->m_model, (PyTypeObject*)new_type);
  if (qualname) {
    if (PyObject_SetAttr(
          (PyObject*)self->m_model, state->str___qualname__, qualname) < 0) {
      res = -1;
      goto cleanup;
    }
  }
  res = 0;

cleanup:
  Py_XDECREF(inherited_slots);
  Py_XDECREF(dict);
  Py_XDECREF(slots);
  Py_XDECREF(qualname);
  return res;
}

static PyObject*
cp_struct_repr(CpStructObject* self)
{
  return PyUnicode_FromFormat("<CpStruct of '%s'>", self->m_model->tp_name);
}

/* public API */
int
CpStruct_AddFieldInfo(CpStructObject* o, CpStructFieldInfoObject* info)
{
  if (!info) {
    PyErr_SetString(PyExc_TypeError, "info must be a set");
    return -1;
  }

  CpFieldObject* field = info->m_field;
  if (PyMapping_HasKey(o->m_members, field->m_name)) {
    PyErr_Format(
      PyExc_ValueError, "field with name %R already exists", field->m_name);
    return -1;
  }

  if (!info->s_excluded) {
    PyObject* list = Cp_IsInvalidDefault(field->m_default)
                       ? o->s_std_init_fields
                       : o->s_kwonly_init_fields;

    if (PyList_Append(list, (PyObject*)info) < 0) {
      return -1;
    }
  }
  return PyObject_SetItem(o->m_members, field->m_name, (PyObject*)info);
}

int
CpStruct_AddField(CpStructObject* o, CpFieldObject* field, int exclude)
{
  if (!field) {
    PyErr_SetString(PyExc_TypeError, "field must be a Field");
    return -1;
  }

  CpStructFieldInfoObject* info = CpStructFieldInfo_New(field);
  if (!info) {
    return -1;
  }
  info->s_excluded = exclude;
  int res = CpStruct_AddFieldInfo(o, info);
  return res;
}

PyObject*
CpStruct_GetAnnotations(CpStructObject* o, int eval)
{
  PyObject* args = Py_BuildValue("(O)", o->m_model);
  if (!args) {
    return NULL;
  }

  PyObject* kwargs = Py_BuildValue("{s:i}", "eval_str", eval);
  if (!kwargs) {
    Py_XDECREF(args);
    return NULL;
  }
  PyObject* result =
    PyObject_Call((PyObject*)o->s_mod->inspect_getannotations, args, kwargs);
  Py_XDECREF(args);
  Py_XDECREF(kwargs);
  return result;
}

int
CpStruct_HasOption(CpStructObject* o, PyObject* option)
{
  return PySet_Contains(o->m_options, option);
}

PyObject*
CpStructModel_GetStruct(PyObject* model, _modulestate* state)
{
  if (!model) {
    PyErr_SetString(PyExc_TypeError, "model must be a type");
    return NULL;
  }

  PyObject* dict = model->ob_type == &PyType_Type
                     ? ((PyTypeObject*)model)->tp_dict
                     : model->ob_type->tp_dict;

  if (!state) {
    return PyMapping_GetItemString(dict, "__struct__");
  } else {
    return PyObject_GetItem(dict, state->str___struct__);
  }
}

int
CpStructModel_Check(PyObject* model, _modulestate* state)
{
  PyObject* dict = NULL;
  if (!model) {
    return 0;
  } else if (Py_IS_TYPE(model, &PyType_Type)) {
    dict = ((PyTypeObject*)model)->tp_dict;
  } else {
    dict = model->ob_type->tp_dict;
  }
  return dict && PyDict_Contains(dict, state->str___struct__);
}

int
CpStruct_ReplaceType(CpStructObject* o, PyObject* name, PyObject* type)
{
  if (!name) {
    PyErr_SetString(PyExc_TypeError, "name must be a string");
    return -1;
  }
  // We have to use direct attribute access here as inspect copies the
  // dictionary before returning.
  PyObject* annotations =
    PyObject_GetAttr((PyObject*)o->m_model, o->s_mod->str___annotations__);
  if (!annotations) {
    return -1;
  }

  if (PyDict_SetItem(annotations, name, type) < 0) {
    Py_XDECREF(annotations);
    return -1;
  }
  Py_XDECREF(annotations);
  return 0;
}

/* docs */

/* members */
static PyMemberDef CpStruct_Members[] = {
  { "model", T_OBJECT, offsetof(CpStructObject, m_model), READONLY, NULL },
  { "members", T_OBJECT, offsetof(CpStructObject, m_members), READONLY, NULL },
  { "options", T_OBJECT, offsetof(CpStructObject, m_options), 0, NULL },
  { NULL } /* Sentinel */
};

/* type */

PyTypeObject CpStruct_Type = {
  PyVarObject_HEAD_INIT(NULL, 0) _Cp_Name(Struct),
  sizeof(CpStructObject),                   /* tp_basicsize */
  0,                                        /* tp_itemsize */
  (destructor)cp_struct_dealloc,            /* tp_dealloc */
  0,                                        /* tp_vectorcall_offset */
  0,                                        /* tp_getattr */
  0,                                        /* tp_setattr */
  0,                                        /* tp_as_async */
  (reprfunc)cp_struct_repr,                 /* tp_repr */
  0,                                        /* tp_as_number */
  0,                                        /* tp_as_sequence */
  0,                                        /* tp_as_mapping */
  0,                                        /* tp_hash */
  0,                                        /* tp_call */
  0,                                        /* tp_str */
  0,                                        /* tp_getattro */
  0,                                        /* tp_setattro */
  0,                                        /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
  NULL,                                     /* tp_doc */
  0,                                        /* tp_traverse */
  0,                                        /* tp_clear */
  0,                                        /* tp_richcompare */
  0,                                        /* tp_weaklistoffset */
  0,                                        /* tp_iter */
  0,                                        /* tp_iternext */
  0,                                        /* tp_methods */
  CpStruct_Members,                         /* tp_members */
  0,                                        /* tp_getset */
  0,                                        /* tp_base */
  0,                                        /* tp_dict */
  0,                                        /* tp_descr_get */
  0,                                        /* tp_descr_set */
  0,                                        /* tp_dictoffset */
  (initproc)cp_struct_init,                 /* tp_init */
  0,                                        /* tp_alloc */
  (newfunc)cp_struct_new,                   /* tp_new */
  0,                                        /* tp_free */
  0,                                        /* tp_is_gc */
  0,                                        /* tp_bases */
  0,                                        /* tp_mro */
  0,                                        /* tp_cache */
  0,                                        /* tp_subclasses */
  0,                                        /* tp_weaklist */
  0,                                        /* tp_del */
  0,                                        /* tp_version_tag */
  0,                                        /* tp_finalize */
  0,                                        /* tp_vectorcall */
  0,                                        /* tp_watched */
};