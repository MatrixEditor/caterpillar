.. _first_steps-docs:


Documenting Structs
===================

Effective documentation is crucial for maintaining a clean and understandable codebase.
*Caterpillar* includes a feature to automatically generate documentation for your
structs. By enabling this feature, you can reduce the need for manual updates and ensure
that your structs are documented consistently. This feature can be activated with
minimal code changes.

To enable the documentation feature globally, you simply need to set the appropriate
flags. Below are the steps to enable it in both environments:


.. tab-set::

    .. tab-item:: Python

        .. code-block:: python
            :caption: Enable documentation feature

            from caterpillar.py import set_struct_flags, S_REPLACE_TYPES

            set_struct_flags(S_REPLACE_TYPES)


    .. tab-item:: Caterpillar C

        .. code-block:: python
            :caption: Enable documentation feature

            from caterpillar.c import STRUCT_OPTIONS, S_REPLACE_TYPES

            STRUCT_OPTIONS.add(S_REPLACE_TYPES)

Once this flag is set, *Caterpillar* will automatically replace the types of fields in
structs with their respective descriptions. For example, the following reST code will
generate simple class documentation for the :code:`NIBHeader`` struct:

.. code-block:: reST

    .. autoclass:: formats.nibarchive.NIBHeader
        :members:

results in:

.. autoclass:: formats.nibarchive.NIBHeader
    :members:

.. tip::
    If you are working with `Sphinx <https://www.sphinx-doc.org/en/master/>`_, you might need
    to enable :code:`autodoc_member_order = 'bysource'` to display all struct members in the
    correct order.

