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
#ifndef CP_STATE_H
#define CP_STATE_H

#include <stdbool.h>
#include <stdint.h>

#include "caterpillar/caterpillarapi.h"

/* advanced parsing state in C */

/**
 * @brief A special class that conforms to the Context protocol used in C
 * packing and unpacking functions.
 *
 * It is meant to be a replacement to the Python `Context` class as it solves
 * a few problems. For instance, there may be global variables passed to the
 * `unpack` function. Instead of copying them into every parsing layer, we just
 * store them in the state object.
 *
 * The state is meant to be accessible from any layer in the parsing process.
 */
struct _stateobj
{
  PyObject_HEAD _modulestate* mod;

  /// The current The input or output stream. This object MUST implement the
  /// stream protocol (read, write, seek and tell).
  PyObject* m_io;

  /// The global namespace for pre-defined context variables. Note that this
  /// object is a `Context` instance.
  PyObject* m_globals;

  /// @note Experimental API
  /// This special member  stores all packed objects that should be placed at
  /// an offset position.
  PyObject* m_offset_table;
};

/**
 * @brief Check whether the given object is a state
 *
 * @param v the object to check
 * @return true if the object is a state
 * @return false if the object is not a state
 */
#define CpState_CheckExact(v) Py_IS_TYPE((v), &CpState_Type)

/**
 * @brief Check whether the given object is a state
 *
 * @param v the object to check
 * @return true if the object is a state
 * @return false if the object is not a state
 */
#define CpState_Check(v) PyObject_TypeCheck((v), &CpState_Type)

//-----------------------------------------------------------------------------
// layer
enum
{
  CpLayerClass_Default = 0,
  CpLayerClass_Sequence = 1,
  CpLayerClass_Object = 2,
};

/**
 * @brief Top level layer class with a reference to its parent and the global
 * parsing state.
 */
struct _layerobj
{
  PyObject_HEAD

    /// The parent layer
    struct _layerobj* m_parent;

  /// the global parsing state
  CpStateObject* m_state;

  /// Although it is optional to provide the current parsing or building path,
  /// it is recommended. All nesting structures implement a behavior that
  /// automatically adds a sub-path while packing or unpacking. Special names
  /// are `"<root>"` for the starting path and `"<NUMBER>"` for greedy sequence
  /// elements
  PyObject* m_path;

  // REVISIT: do we need them?
  /// Lazily loaded context sensitive variables (this field remains NULL until
  /// the first item gets added to it)
  // PyObject *m_locals;

  /// The type of the layer
  int8_t m_class;

  // --- Context sensitive variables ---

  // /// In case a struct is linked to a field, the `Field` instance will always
  // /// set this layer to be accessible from within the underlying struct.
  // PyObject* m_field;

  // /// When packing or unpacking objects, the current object attributes are
  // /// stored within an object context. This is a special context that allows
  // /// access to previously parsed fields or attributes of the input object.
  // To
  // /// minimize the number of calls using this attribute, a shortcut named
  // `this`
  // /// was defined, which automatically inserts a path to the object context.
  // PyObject* m_obj;

  // /// In case a switch-case statement is activated in a field, the layer will
  // /// store the parsed value in this variable temporarily.
  // PyObject* m_value;

  // /// Same as `m_obj` but for the sequential elements.
  // PyObject* m_sequence;

  // /// The length of the current collection.
  // Py_ssize_t m_length;

  // /// When packing or unpacking collections of elements, the current working
  // /// index is given under this layer variable. It is set only in this
  // specific
  // /// situation.
  // Py_ssize_t m_index;

  // // --- Internal state variables ---
  // int8_t s_greedy;
  // int8_t s_sequential;
};

/**
 * @brief Check whether the given object is a layer
 *
 * @param v the object to check
 * @return true if the object is a layer
 * @return false if the object is not a layer
 */
#define CpLayer_CheckExact(v) Py_IS_TYPE((v), &CpLayer_Type)

/**
 * @brief Check whether the given object is a layer
 *
 * @param v the object to check
 * @return true if the object is a layer
 * @return false if the object is not a layer
 */
#define CpLayer_Check(v) PyObject_TypeCheck((v), &CpLayer_Type)
#define CpLayer_HEAD CpLayerObject ob_base;

#define CpLayer_AppendPath(layer, newpath)                                     \
  Py_XSETREF(                                                                  \
    (layer)->m_path,                                                           \
    PyUnicode_FromFormat("%s.%s",                                              \
                         PyUnicode_AsUTF8AndSize((layer)->m_parent             \
                                                   ? (layer)->m_parent->m_path \
                                                   : (layer)->m_path,          \
                                                 NULL),                        \
                         PyUnicode_AsUTF8AndSize((newpath), NULL)));

//-----------------------------------------------------------------------------
// seq layer

struct _seqlayerobj
{
  CpLayer_HEAD

    /// Same as `m_obj` but for the sequential elements.
    PyObject* m_sequence;

  /// The length of the current collection.
  Py_ssize_t m_length;

  /// When packing or unpacking collections of elements, the current working
  /// index is given under this layer variable. It is set only in this specific
  /// situation.
  Py_ssize_t m_index;

  int8_t s_greedy;
};

#define CpSeqLayer_CheckExact(v) Py_IS_TYPE((v), &CpSeqLayer_Type)
#define CpSeqLayer_Check(v) PyObject_TypeCheck((v), &CpSeqLayer_Type)

//-----------------------------------------------------------------------------
// obj layer

struct _objlayerobj
{
  CpLayer_HEAD

    /// When packing or unpacking objects, the current object attributes are
    /// stored within an object context. This is a special context that allows
    /// access to previously parsed fields or attributes of the input object. To
    /// minimize the number of calls using this attribute, a shortcut named
    /// `this` was defined, which automatically inserts a path to the object
    /// context.
      PyObject* m_obj;
};

#define CpObjLayer_CheckExact(v) Py_IS_TYPE((v), &CpObjLayer_Type)
#define CpObjLayer_Check(v) PyObject_TypeCheck((v), &CpObjLayer_Type)

//-----------------------------------------------------------------------------
// field layer

struct _fieldlayerobj
{
  CpLayer_HEAD

    /// In case a struct is linked to a field, the `Field` instance will always
    /// set this layer to be accessible from within the underlying struct.
    PyObject* m_field;
};

#endif