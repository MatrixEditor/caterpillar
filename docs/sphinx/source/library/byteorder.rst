.. _byteorder:

**************************
Byteorder and Architecture
**************************

.. py:currentmodule:: caterpillar.byteorder

Byteorder
---------

.. autoclass:: ByteOrder
    :members:

.. autofunction:: byteorder(obj, default: Optional[ByteOrder] = None) -> ByteOrder

Standard Byteorder Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoattribute:: caterpillar.byteorder.Native

.. autoattribute:: caterpillar.byteorder.BigEndian

.. autoattribute:: caterpillar.byteorder.LittleEndian

.. autoattribute:: caterpillar.byteorder.NetEndian

.. autoattribute:: caterpillar.byteorder.SysNative




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
