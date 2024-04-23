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

#include "caterpillar/macros.h"
#include "caterpillar/module.h"

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
typedef struct _stateobj
{
  PyObject_HEAD;
  _modulestate* mod;

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
} CpStateObject;

/// State object type
PyAPI_DATA(PyTypeObject) CpState_Type;

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

/**
 * @brief Creates a new state object
 *
 * @param io the input or output stream object
 * @return the new state object, or NULL on failure
 */
PyAPI_FUNC(CpStateObject*) CpState_New(PyObject* io);

/**
 * @brief Returns the current position in the input stream
 *
 * @return the current position
 */
PyAPI_FUNC(PyObject*) CpState_Tell(CpStateObject* self);

/**
 * @brief Sets the current position in the input stream
 *
 * @param pos the new position
 * @return the new position
 */
PyAPI_FUNC(PyObject*)
  CpState_Seek(CpStateObject* self, PyObject* pos, int whence);

/**
 * @brief Reads the given number of bytes from the input stream
 *
 * @param size the number of bytes to read
 * @return the read bytes
 */
PyAPI_FUNC(PyObject*) CpState_Read(CpStateObject* self, Py_ssize_t size);

/**
 * @brief Writes the given bytes to the output stream
 *
 * @param bytes the bytes to write
 * @return the number of bytes written
 */
PyAPI_FUNC(PyObject*) CpState_Write(CpStateObject* self, PyObject* bytes);

/**
 * @brief Sets the global namespace for pre-defined context variables
 *
 * @param globals the new global namespace
 * @return the new global namespace
 */
PyAPI_FUNC(int) CpState_SetGlobals(CpStateObject* self, PyObject* globals);

//-----------------------------------------------------------------------------
// layer

// forward declaration is necessary here
struct _layerobj;

/**
 * @brief TODO
 */
typedef struct _layerobj
{
  PyObject_HEAD;

  /// The parent layer
  struct _layerobj* m_parent;

  /// the global parsing state
  CpStateObject* m_state;

  // --- Context sensitive variables ---

  /// In case a struct is linked to a field, the `Field` instance will always
  /// set this layer to be accessible from within the underlying struct.
  PyObject* m_field;

  /// When packing or unpacking objects, the current object attributes are
  /// stored within an object context. This is a special context that allows
  /// access to previously parsed fields or attributes of the input object. To
  /// minimize the number of calls using this attribute, a shortcut named `this`
  /// was defined, which automatically inserts a path to the object context.
  PyObject* m_obj;

  /// In case a switch-case statement is activated in a field, the layer will
  /// store the parsed value in this variable temporarily.
  PyObject* m_value;

  /// Although it is optional to provide the current parsing or building path,
  /// it is recommended. All nesting structures implement a behavior that
  /// automatically adds a sub-path while packing or unpacking. Special names
  /// are `"<root>"` for the starting path and `"<NUMBER>"` for greedy sequence
  /// elements
  PyObject* m_path;

  /// Same as `m_obj` but for the sequential elements.
  PyObject* m_sequence;

  /// The length of the current collection.
  Py_ssize_t m_length;

  /// When packing or unpacking collections of elements, the current working
  /// index is given under this layer variable. It is set only in this specific
  /// situation.
  Py_ssize_t m_index;

  // --- Internal state variables ---
  int8_t s_greedy;
  int8_t s_sequential;
} CpLayerObject;

/// Layer type
PyAPI_DATA(PyTypeObject) CpLayer_Type;

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

/**
 * @brief Creates a new layer object
 *
 * @param parent the parent layer (may be NULL)
 * @param state the global parsing state
 * @return the new layer object, or NULL on failure
 */
PyAPI_FUNC(CpLayerObject*)
  CpLayer_New(CpStateObject* state, CpLayerObject* parent);

/**
 * @brief Invalidates the layer
 *
 * @param layer the layer to invalidate
 * @return 0 on success, -1 on failure
 */
PyAPI_FUNC(int) CpLayer_Invalidate(CpLayerObject* layer);

/**
 * @brief Applies the given sequence to the layer
 *
 * @param layer the layer to apply the sequence to
 * @param sequence the sequence to apply
 * @param length the length of the sequence
 * @param greedy whether the sequence is greedy
 * @return 0 on success, -1 on failure
 */
PyAPI_FUNC(int) CpLayer_SetSequence(CpLayerObject* layer,
                                    PyObject* sequence,
                                    Py_ssize_t length,
                                    int8_t greedy);

#define CpLayer_AppendPath(layer, newpath)                                     \
  Py_XSETREF(                                                                  \
    (layer)->m_path,                                                           \
    PyUnicode_FromFormat("%s.%s",                                              \
                         _PyUnicode_AsString((layer)->m_parent                 \
                                               ? (layer)->m_parent->m_path     \
                                               : (layer)->m_path),             \
                         _PyUnicode_AsString((newpath))));

#endif