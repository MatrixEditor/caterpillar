/**
 * Copyright (C) MatrixEditor 2024
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
#ifndef CP_MODULE_H
#define CP_MODULE_H

#include "caterpillarapi.h"

/**
 * @brief The internal state for this module.
 *
 * It will store all necessary information about the core module.
 */
struct _modulestate
{
  // global options
  PyObject* cp_option__dynamic;
  PyObject* cp_option__sequential;
  PyObject* cp_option__keep_position;
  PyObject* cp_option__union;
  PyObject* cp_option__eval;
  PyObject* cp_option__discard_unnamed;
  PyObject* cp_option__discard_const;
  PyObject* cp_option__replace_types;
  PyObject* cp_option__slots;

  // global default options
  PyObject* cp_option__global_field_options;
  PyObject* cp_option__global_struct_options;

  // global arch
  PyObject* cp_arch__host;

  // default endian object
  PyObject* cp_endian__native;
  PyObject* cp_endian__big;
  PyObject* cp_endian__little;

  // typing constants
  PyObject* Any_Type;
  PyObject* List_Type;
  PyObject* Optional_Type;
  PyObject* Union_Type;
  PyObject* BytesIO_Type;

  // string constants
  // strings
  PyObject* str_path_delim;
  PyObject* str_tell;
  PyObject* str_seek;
  PyObject* str_write;
  PyObject* str_read;
  PyObject* str_close;
  PyObject* str_strict;
  PyObject* str___pack__;
  PyObject* str___pack_many__;
  PyObject* str___unpack__;
  PyObject* str___unpack_many__;
  PyObject* str___size__;
  PyObject* str___type__;
  PyObject* str___bits__;
  PyObject* str___annotations__;
  PyObject* str___mro__;
  PyObject* str___struct__;
  PyObject* str___slots__;
  PyObject* str___match_args__;
  PyObject* str___weakref__;
  PyObject* str___dict__;
  PyObject* str___qualname__;
  PyObject* str__member_map_;
  PyObject* str__value2member_map_;

  PyObject* str_start;
  PyObject* str_ctx__root;
  PyObject* str_ctx__getattr;
  PyObject* str_bytesio_getvalue;
  PyObject* str_builder_process;
  PyObject* str_pattern_match;
  PyObject* str_cstring_default_pad;
  PyObject* str_utf8;

  // compiled regex for unnamed fields
  PyObject* cp_regex__unnamed;
  PyObject* inspect_getannotations;

  // cached objects
  PyObject* cp_bytes__true;
  PyObject* cp_bytes__false;

  // type handler map
  PyObject* cp_typehandler_map;

  // COMPAT: hashes for all compatibility context objects
  PyObject* str__ctx_parent;
  PyObject* str__ctx_object;
  PyObject* str__ctx_offsets;
  PyObject* str__ctx_stream;
  PyObject* str__ctx_field;
  PyObject* str__ctx_value;
  PyObject* str__ctx_pos;
  PyObject* str__ctx_index;
  PyObject* str__ctx_path;
  PyObject* str__ctx_is_seq;
  PyObject* str__ctx_arch;
};

/**
 * @brief Get the module state object
 *
 * @param module the current module
 * @return _modulestate* the current state
 */
static inline _modulestate*
get_module_state(PyObject* module)
{
  void* state = PyModule_GetState(module);
  assert(state != NULL);
  return (_modulestate*)state;
}

/**
 * @brief Get the module state (globally)
 *
 * @return _modulestate* the current module state
 */
static inline _modulestate*
get_global_module_state(void)
{
  return get_module_state(PyState_FindModule(&CpModule));
}

/* utility macros */
#define CpModule_SetupType(op)                                                 \
  if (PyType_Ready(op) < 0)                                                    \
    return NULL;

#endif