.. _tutorial-advanced-actions:

Actions
=======

Actions are a powerful feature that allow you to perform custom operations on
the struct's state during parsing. Instead of directly parsing or storing a
field's value, you can define actions to modify or interact with the data
processing at different stages.

There are two types of actions you can define:

- **Pack Actions**: These actions are executed before packing data into the struct. They are typically used for operations such as checksum calculation, logging, or any other operation that must occur before serializing the data.
- **Unpack Actions**: These actions are executed before unpacking the data from the struct. They are commonly used for validation, verification, or any operation that needs to happen before deserialization.

An action can be as simple as executing a function during packing or unpacking.
For example:

.. tab-set::
    :sync-group: syntax

    .. tab-item:: Default Syntax
        :sync: default

        .. code-block:: python

            @struct
            class Format:
                _: Action(pack=lambda ctx: print("Hello, World!"))
                a: uint8

    .. tab-item:: Extended Syntax (>=2.8.0)
        :sync: extended

        .. code-block:: python

            @struct
            class Format:
                _: f[None, Action(pack=lambda context: print("Hello, World!"))] = None
                a: uint8_t

In this case, when the struct is packed, it will print :code:`"Hello, World!"` to the
console. Actions like this can be used for logging, validation, or other side
effects that are not tied to the direct data of the struct.

Advanced Usage: Message Digests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::
    This feature has a different syntax in Python 3.14+.

Actions can also be used to perform more complex operations, such as calculating
checksums or cryptographic hash values before or after processing fields. For
example, you can use an action to automatically wrap a sequence of fields with a
specialized message digest like SHA256 (see :class:`~caterpillar.py.Digest`):

.. tab-set::

    .. tab-item:: Python <= 3.13

        .. tab-set::
            :sync-group: syntax

            .. tab-item:: Default Syntax
                :sync: default

                .. code-block:: python

                    @struct
                    class Format:
                        key: b"..."
                        with Sha2_256("hash", verify=True):
                            user_data: Bytes(50)
                        # the 'hash' attribute will be set automatically

            .. tab-item:: Extended Syntax (>=2.8.0)
                :sync: extended

                .. code-block:: python

                    @struct
                    class Format:
                        key: f[bytes, b"..."]
                        with Sha2_256("hash", verify=True):
                            user_data: f[bytes, Bytes(50)]
                        # the 'hash' attribute will be set automatically

    .. tab-item:: Python >= 3.14

       .. tab-set::
            :sync-group: syntax

            .. tab-item:: Default Syntax
                :sync: default

                .. code-block:: python

                    @struct
                    class Format:
                        key: b"..."
                        _hash_begin: DigestField.begin("hash", Sha2_256_Algo)
                        user_data: Bytes(50)
                        # the 'hash' attribute must be set manually
                        hash: DigestField("hash", Bytes(32), verify=True) = None
                        # or
                        hash: Sha2_256_Field("hash", verify=True) = None

            .. tab-item:: Extended Syntax (>=2.8.0)
                :sync: extended

                .. code-block:: python

                    @struct
                    class Format:
                        key: f[bytes, b"..."]
                        _hash_begin: f[None, DigestField.begin("hash", Sha2_256_Algo)] = None
                        user_data: f[bytes, Bytes(50)]
                        # the 'hash' attribute must be set manually
                        hash: f[bytes, DigestField("hash", Bytes(32), verify=True)] = b""
                        # or
                        hash: f[bytes, Sha2_256_Field("hash", verify=True)] = b""



In this example, the :code:`user_data` field is wrapped with the :code:`Sha2_256` digest action.
When the struct is packed, a SHA256 hash is computed for the :code:`user_data` and stored
in the :code:`hash` attribute. If the struct is unpacked and the data has been tampered
with, the verification step will raise an error.

The resulting struct includes the following fields:


.. tab-set::

    .. tab-item:: Python <= 3.13

        .. code-block:: python

            >>> Format.__struct__.fields
            [
                Field('key', struct=<ConstBytes>, ...),
                (Action(Digest.begin), None),
                Field('user_data', struct=<Bytes>, ...),
                (Action(Digest.end_pack, Digest.end_unpack), None),
                Field('hash', struct=<Bytes>, ...),
                (UnpackAction(Digest.verfiy), None)
            ]


    .. tab-item:: Python >= 3.14

        .. code-block:: python

            >>> Format.__struct__.fields
            [
                Field('key', struct=<ConstBytes>, ...),
                (<DigestFieldAction>, None),
                Field('user_data', struct=<Bytes>, ...),
                <DigestField>,
            ]


Here, you can see that:

- The :code:`Digest.begin` and :code:`Digest.[end,begin]_pack` actions are executed around the :code:`user_data` field during packing.
- The :code:`hash` field is automatically calculated and added to the struct.
- During unpacking, the :code:`Digest.verify` action ensures that the hash matches the expected value.

