.. _byteorder:

**************************
Byteorder and Architecture
**************************

.. py:currentmodule:: caterpillar.byteorder

Byteorder
---------

.. autoclass:: ByteOrder
    :members:

.. autoclass:: DynByteOrder
    :members:

.. autofunction:: byteorder
.. autofunction:: byteorder_is_little

Standard Byteorder Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autodata:: caterpillar.byteorder.Native

.. autodata:: caterpillar.byteorder.BigEndian

.. autodata:: caterpillar.byteorder.LittleEndian

.. autodata:: caterpillar.byteorder.NetEndian

.. autodata:: caterpillar.byteorder.SysNative

.. autodata:: caterpillar.byteorder.Dynamic

.. autodata:: caterpillar.byteorder.LITTLE_ENDIAN_FMT

.. autodata:: caterpillar.byteorder.O_DEFAULT_ENDIAN


Architecture
------------

.. autoclass:: Arch
    :members:

.. autoattribute:: caterpillar.byteorder.system_arch

Standard Architectures
~~~~~~~~~~~~~~~~~~~~~~

.. autoattribute:: caterpillar.byteorder.x86

.. autoattribute:: caterpillar.byteorder.x86_64

.. autoattribute:: caterpillar.byteorder.ARM

.. autoattribute:: caterpillar.byteorder.ARM64

.. autoattribute:: caterpillar.byteorder.AARCH64

.. autoattribute:: caterpillar.byteorder.PowerPC

.. autoattribute:: caterpillar.byteorder.PowerPC64

.. autoattribute:: caterpillar.byteorder.MIPS

.. autoattribute:: caterpillar.byteorder.MIPS64

.. autoattribute:: caterpillar.byteorder.SPARC

.. autoattribute:: caterpillar.byteorder.SPARC64

.. autoattribute:: caterpillar.byteorder.RISC_V64

.. autoattribute:: caterpillar.byteorder.RISC_V

.. autoattribute:: caterpillar.byteorder.AMD

.. autoattribute:: caterpillar.byteorder.AMD64
