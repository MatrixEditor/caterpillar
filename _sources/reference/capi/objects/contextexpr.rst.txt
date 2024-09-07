.. _capi_context-expr:

Context Expressions
===================

Unary Expressions
-----------------

.. c:var:: PyTypeObject CpUnaryExpr_Type

    The type object for the :c:type:`CpUnaryExprObject` class.


.. c:type:: CpUnaryExprObject

    A simple unary expression (from Python).

    This is a helper class to support lazy evaluation of unary expressions
    while parsing data.


.. c:function:: CpUnaryExprObject *CpUnaryExpr_New(int op, PyObject* value)

    Creates a new unary expression. Returns *NULL* if an error occurs.
    The *op* argument should be one of the :c:type:`CpUnaryExpr` constants
    listed below.

    .. c:var:: int CpUnaryExpr_OpNeg = 1
               int CpUnaryExpr_OpNot = 2
               int CpUnaryExpr_OpPos = 3


Binary Expressions
------------------

.. c:var:: PyTypeObject CpBinaryExpr_Type

    The type object for the :c:type:`CpBinaryExprObject` class.


.. c:type:: CpBinaryExprObject

    A simple binary expression (from Python).

    This is a helper class to support lazy evaluation of binary expressions
    while parsing data.


.. c:function:: CpBinaryExprObject *CpBinaryExpr_New(int op, PyObject* left, PyObject* right)

    Creates a new binary expression. Returns *NULL* if an error occurs.
    The *op* argument should be one of the :c:type:`CpBinaryExpr` constants
    listed below.

    .. c:var:: int CpBinaryExpr_Op_LT = 0
               int CpBinaryExpr_Op_LE = 1
               int CpBinaryExpr_Op_EQ = 2
               int CpBinaryExpr_Op_NE = 3
               int CpBinaryExpr_Op_GT = 4
               int CpBinaryExpr_Op_GE = 5
               int CpBinaryExpr_OpAdd = 6
               int CpBinaryExpr_OpSub = 7
               int CpBinaryExpr_OpMul = 8
               int CpBinaryExpr_OpFloorDiv = 9
               int CpBinaryExpr_OpTrueDiv = 10
               int CpBinaryExpr_OpMod = 11
               int CpBinaryExpr_OpPow = 12
               int CpBinaryExpr_OpMatMul = 13
               int CpBinaryExpr_OpAnd = 14
               int CpBinaryExpr_OpOr = 15
               int CpBinaryExpr_OpBitXor = 16
               int CpBinaryExpr_OpBitAnd = 17
               int CpBinaryExpr_OpBitOr = 18
               int CpBinaryExpr_OpLShift = 19
               int CpBinaryExpr_OpRShift = 20

    Note that the first six operations store the same value as defined by Python,
    minimizing the effort to translate \*_richcmp calls into this enum.


