/**
 * Copyright (C) MatrixEditor 2025
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
  // global arch
  PyObject* cp_arch__host;

  // default endian object
  PyObject* cp_endian__native;
  PyObject* cp_endian__big;
  PyObject* cp_endian__little;

  // intern strings
  PyObject* str__path_sep;
  PyObject* str__context_root;
  PyObject* str__fn_rsplit;
  PyObject* str__pack;
  PyObject* str__pack_many;
  PyObject* str__unpack;
  PyObject* str__unpack_many;
  PyObject* str__type;
  PyObject* str__size;
  PyObject* str__bits;
  PyObject* str__context_parent;
  PyObject* str__context_io;
  PyObject* str__context_length;
  PyObject* str__context_index;
  PyObject* str__context_path;
  PyObject* str__context_obj;
  PyObject* str__context_is_seq;
  PyObject* str__context_field;
  PyObject* str__context_offsets;
  PyObject* str__start;
  PyObject* str__value;
  PyObject* str__context_list;
  PyObject* str__struct;
  PyObject* str__io_tell;
  PyObject* str__io_seek;
  PyObject* str__io_read;
  PyObject* str__io_write;
  PyObject* str__io_getvalue;
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
#define CpModule_SetupType(op, ret)                                            \
  if (PyType_Ready(op) < 0)                                                    \
    return (ret);

#endif