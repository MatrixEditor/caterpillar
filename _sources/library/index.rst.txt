.. _library-index:

*******
Library
*******

*descriptions are WIP*

.. toctree::
   :maxdepth: 1
   :caption: Python API

   byteorder.rst
   options.rst
   context.rst
   exceptions.rst
   model.rst
   registry
   shared
   fields/index.rst
   hooks
   ext_types


.. _library-index-capi:

***********
C Extension
***********

The optional C extension mirrors selected Python APIs for lower overhead in
hot parsing paths. The Python package remains the reference implementation;
native types are documented in the :ref:`reference-index` C API section.

.. toctree::
   :maxdepth: 2
   :caption: C API Python Types


.. ctypes/int.rst
