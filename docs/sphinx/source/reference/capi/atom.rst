.. highlight:: c

.. _reference-capi_atom:

Atom Protocol
=============

Caterpillar provides a special protocol for working with atoms. It is
designed to incorporate packing and unpacking of data streams as well
as calculating its size and measuring its type.

.. versionchanged:: 2.6.0
    Reworked the CAPI and its components.

.. c:type:: CpAtomObject

    All classes that implement capabilities of an *atom* should inherit
    from this class. It stores optional C slots for ``__pack__``,
    ``__pack_many__``, ``__unpack__``, ``__unpack_many__``, ``__size__``,
    ``__type__`` and ``__bits__``. Slots that are not configured raise
    :class:`NotImplementedError` when called through the Python methods.


.. c:var:: PyTypeObject CpAtom_Type

    The type object of the :c:type:`CpAtom` class.


Atoms may be implemented either as native :c:type:`CpAtomObject` subclasses or
as normal Python objects exposing the corresponding special methods. The
``CpAtom_*`` helpers use the native slot when available and fall back to Python
attribute/method lookup otherwise.

.. c:function:: int CpAtom_HasPack(PyObject* o)
                int CpAtom_FastCanPack(PyObject* o, _coremodulestate* state)

    Return ``1`` if the object provides an interface of packing other
    objects and ``0`` otherwise. Note that it returns ``1`` for classes
    with a :meth:`~object.__pack__` method, since the type of objects to
    be packed can not be determined by introspection.

.. c:function:: int CpAtom_HasPackMany(PyObject* o)

    Return ``1`` if the object exposes ``__pack_many__`` and ``0`` otherwise.


.. c:function:: int CpAtom_HasUnpack(PyObject* o)

    Return ``1`` if the object provides an interface of unpacking other
    objects and ``0`` otherwise. Note that it returns ``1`` for classes
    with a :meth:`~object.__unpack__` method, since the type of objects
    to be unpacked can not be determined by introspection.

.. c:function:: int CpAtom_HasUnpackMany(PyObject* o)

    Return ``1`` if the object exposes ``__unpack_many__`` and ``0`` otherwise.


.. c:function:: int CpAtom_HasType(PyObject* o)

    Returns ``1`` if the object provides a method of determining the type
    this object (usually an atom) represents and ``0`` otherwise. As all
    other functions, this one will simply check for the presence of the
    :meth:`~object.__type__` method.


.. c:function:: int CpAtom_HasSize(PyObject* o)

    Searches for :meth:`~object.__size__`, returns ``1`` if it is
    present and ``0`` otherwise.

.. c:function:: int CpAtom_HasBits(PyObject* o)

    Searches for ``__bits__`` and returns ``1`` if present. ``__bits__`` is used
    by bitfield and repeated native atoms and may be implemented as either a
    callable or an integer attribute on Python objects.


