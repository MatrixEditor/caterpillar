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
#ifndef CP_CONTEXT_H
#define CP_CONTEXT_H

/* Caterpillar Context and ContextPath C implementation */
#include "caterpillar/macros.h"
#include "caterpillar/module.h"

/*context*/

/**
 * @brief C implementation of the Python equivalent.
 *
 * Represents a context object with attribute-style access, which also conforms
 * to the context protocol.
 */
typedef struct _contextobj
{
  /// This object is essentially a dict object with some extra
  /// methods to conform to the Context protocol. Therefore, this
  /// object can be casted into a dictionary directly.
  PyDictObject m_dict;
} CpContextObject;

/// Context object type
PyAPI_DATA(PyTypeObject) CpContext_Type;

/**
 * @brief Checks if the given object is an context object
 *
 * This macro will check the exact type of the object and return
 * 1 if it is of type `CpContext` and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an context object, 0 otherwise
 */
#define CpContext_CheckExact(op) Py_IS_TYPE((op), &CpContext_Type)

/**
 * @brief Checks if the given object is an context object
 *
 * This macro will check the type of the object and return
 * 1 if it is an context object and 0 otherwise.
 *
 * @param op the object to check (must be a Python object pointer)
 * @return 1 if the object is an context object, 0 otherwise
 */
#define CpContext_Check(op) PyObject_TypeCheck((op), &CpContext_Type)

/**
 * @brief Get an attribute from a context by using __context_getattr__.
 *
 * @return the attribute, or NULL on failure
 */
PyAPI_FUNC(PyObject*)
  CpContext_GetAttr(PyObject* ctx, PyObject* key, _modulestate* m);

/**
 * @brief Get an attribute from a context by using __context_getattr__.
 *
 * @return the attribute, or NULL on failure
 */
PyAPI_FUNC(PyObject*) CpContext_GetAttrString(PyObject* ctx, const char* key);

// -----------------------------------------------------------------------------
// unary expression
enum
{
  CpUnaryExpr_OpNeg = 1,
  CpUnaryExpr_OpNot = 2,
  CpUnaryExpr_OpPos = 3
};

/**
 * @brief A simple unary expression (from Python)
 *
 * This is a helper class to support lazy evaluation of unary expressions
 * while parsing data.
 */
typedef struct CpUnaryExpr
{
  /// the operation to perform
  PyObject_HEAD int m_expr;
  /// the value to apply the operation to
  PyObject* m_value;
} CpUnaryExprObject;

/// Unary expression type
PyAPI_DATA(PyTypeObject) CpUnaryExpr_Type;

/**
 * @brief Create a new unary expression
 *
 * @param op the operation to perform
 * @param value the value to apply the operation to
 * @return the new unary expression, or NULL on failure
 */
PyAPI_FUNC(CpUnaryExprObject*) CpUnaryExpr_New(int op, PyObject* value);

// -----------------------------------------------------------------------------
// binary expression
enum
{
  // The first six operations store the same value as defined by Python,
  // minimizing the effort to translate *_richcmp calls into this enum.
  CpBinaryExpr_Op_LT = 0,
  CpBinaryExpr_Op_LE,
  CpBinaryExpr_Op_EQ,
  CpBinaryExpr_Op_NE,
  CpBinaryExpr_Op_GT,
  CpBinaryExpr_Op_GE,
  CpBinaryExpr_OpAdd,
  CpBinaryExpr_OpSub,
  CpBinaryExpr_OpMul,
  CpBinaryExpr_OpFloorDiv,
  CpBinaryExpr_OpTrueDiv,
  CpBinaryExpr_OpMod,
  CpBinaryExpr_OpPow,
  CpBinaryExpr_OpMatMul,
  CpBinaryExpr_OpAnd,
  CpBinaryExpr_OpOr,
  CpBinaryExpr_OpBitXor,
  CpBinaryExpr_OpBitAnd,
  CpBinaryExpr_OpBitOr,
  CpBinaryExpr_OpLShift,
  CpBinaryExpr_OpRShift,
};

/**
 * @brief A simple binary expression (from Python)
 *
 * This is a helper class to support lazy evaluation of binary expressions
 * while parsing data. The operations are defined in the enum above.
 */
typedef struct CpBinaryExpr
{
  /// the operation to perform
  PyObject_HEAD int m_expr;
  /// the left and right values
  PyObject* m_left;
  PyObject* m_right;
} CpBinaryExprObject;

/// Binary expression type
PyAPI_DATA(PyTypeObject) CpBinaryExpr_Type;

/**
 * @brief Create a new binary expression
 *
 * @param op the operation to perform
 * @param left the left value
 * @param right the right value
 * @return the new binary expression, or NULL on failure
 */
PyAPI_FUNC(CpBinaryExprObject*)
  CpBinaryExpr_New(int op, PyObject* left, PyObject* right);

// -----------------------------------------------------------------------------
// context path

/**
 * @brief A simple context path
 *
 * Represents a lambda function for retrieving a value from a Context based on
 * a specified path.
 */
typedef struct CpContextPath
{
  /// the path object
  PyObject_HEAD PyObject* m_path;

  // internal variable to minimize the amount of calls to get the
  // global module state.
  _modulestate* m_state;
} CpContextPathObject;

/// Context path type
PyAPI_DATA(PyTypeObject) CpContextPath_Type;

/**
 * @brief Create a new context path
 *
 * @param path the path object (unicode object)
 * @return the new context path, or NULL on failure
 */
PyAPI_FUNC(CpContextPathObject*) CpContextPath_New(PyObject* path);

/**
 * @brief Create a new context path
 *
 * @param path the path string
 * @return the new context path, or NULL on failure
 */
PyAPI_FUNC(CpContextPathObject*) CpContextPath_FromString(const char* path);

/**
 * @brief Checks if the given object is a context path
 *
 * @param op the object to check
 * @return 1 if the object is a context path, 0 otherwise
 */
#define CpContextPath_CheckExact(op) Py_IS_TYPE((op), &CpContextPath_Type)

/**
 * @brief Checks if the given object is a context path
 *
 * @param op the object to check
 * @return 1 if the object is a context path, 0 otherwise
 */
#define CpContextPath_Check(op) PyObject_TypeCheck((op), &CpContextPath_Type)

#endif