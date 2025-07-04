# Copyright (C) MatrixEditor 2023-2025
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Protocol, runtime_checkable

from caterpillar.exception import UnsupportedOperation
from caterpillar.exception import InvalidValueError
from caterpillar.context import CTX_STREAM
from .common import Memory, Bytes
from ._mixin import get_args, get_kwargs


@runtime_checkable
class Padding(Protocol):  # pylint: disable=missing-class-docstring
    def unpadder(self):
        """Abstract method to get an unpadder for padding."""

    def padder(self):
        """Abstract method to get a padder for padding."""


class Encrypted(Memory):
    """Struct that is able to encrypt/decrypt blocks of memory.

    :param length: Length of the encrypted data.
    :type length: Union[int, _GreedyType, _ContextLambda]
    :param algorithm: Encryption algorithm.
    :type algorithm: Type[algorithms.CipherAlgorithm]
    :param mode: Encryption mode.
    :type mode: Union[Type[modes.Mode], modes.Mode]
    :param padding: Padding scheme for encryption.
    :type padding: Union[Padding, Type[Padding]], optional
    :param algo_args: Additional arguments for the encryption algorithm.
    :type algo_args: Optional[Iterable[_ArgType]], optional
    :param mode_args: Additional arguments for the encryption mode.
    :type mode_args: Optional[Iterable[_ArgType]], optional
    :param padding_args: Additional arguments for the padding scheme.
    :type padding_args: Optional[Iterable[_ArgType]], optional
    :param post: Post-processing structure.
    """

    # REVISIT: this constructor looks ugly
    def __init__(
        self,
        length,
        algorithm,
        mode,
        padding=None,
        algo_args=None,
        mode_args=None,
        padding_args=None,
        post=None,
    ) -> None:
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher
        except ImportError:
            raise UnsupportedOperation(
                (
                    "To use encryption with this framework, the module 'cryptography' "
                    "is required! You can install it via pip or use the packaging "
                    "extra 'crypto' that is available with this library."
                )
            )

        super().__init__(length)
        self._algo = algorithm
        self._algo_args = algo_args
        self._mode = mode
        self._mode_args = mode_args
        self._padding = padding
        self._padding_args = padding_args
        self.post = post

    def algorithm(self, context):
        """
        Get the encryption algorithm instance.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: An instance of the encryption algorithm.
        :rtype: algorithms.CipherAlgorithm
        """
        from cryptography.hazmat.primitives.ciphers import CipherAlgorithm

        return self.get_instance(CipherAlgorithm, self._algo, self._algo_args, context)

    def mode(self, context):
        """
        Get the encryption mode instance.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: An instance of the encryption mode.
        :rtype: modes.Mode
        """
        from cryptography.hazmat.primitives.ciphers import modes

        return self.get_instance(modes.Mode, self._mode, self._mode_args, context)

    def padding(self, context) -> Padding:
        """
        Get the padding scheme instance.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: An instance of the padding scheme.
        :rtype: Padding
        """
        return self.get_instance(Padding, self._padding, self._padding_args, context)

    def get_instance(self, type_, field, args, context):
        """
        Get an instance of a specified type.

        :param type_: The desired type of the instance.
        :type type_: type
        :param field: The field or instance.
        :type field: Any
        :param args: Additional arguments for the instance.
        :type args: Any
        :param context: The current operation context.
        :type context: _ContextLambda
        :return: An instance of the specified type.
        :rtype: Any
        """
        if isinstance(field, type_) or not field:
            return field

        if isinstance(args, dict):
            args, kwargs = (), get_kwargs(args, context)
        else:
            args, kwargs = get_args(args, context), {}
        return field(*args, **kwargs)

    def pack_single(self, obj, context) -> None:
        """
        Pack a single element.

        :param obj: The element to pack.
        :type obj: Any
        :param context: The current operation context.
        :type context: _ContextLike
        """
        from cryptography.hazmat.primitives.ciphers import Cipher

        cipher = Cipher(self.algorithm(context), self.mode(context))
        padding = self.padding(context)

        data = obj if isinstance(obj, bytes) else bytes(obj)
        if padding:
            padder = padding.padder()
            data = padder.update(data) + padder.finalize()

        encryptor = cipher.encryptor()
        super().pack_single(encryptor.update(data) + encryptor.finalize(), context)

    def unpack_single(self, context):
        """
        Unpack a single element.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: The unpacked element as a memoryview.
        :rtype: memoryview
        """
        from cryptography.hazmat.primitives.ciphers import Cipher
        value = super().unpack_single(context)
        cipher = Cipher(self.algorithm(context), self.mode(context))

        decryptor = cipher.decryptor()
        data = decryptor.update(bytes(value)) + decryptor.finalize()

        padding = self.padding(context)
        if padding:
            unpadder = padding.unpadder()
            data = unpadder.update(data) + unpadder.finalize()
        return memoryview(data)


class KeyCipher(Bytes):
    # key: bytes
    # """The key that should be applied.

    # It will be converted automatically to bytes if not given.
    # """

    # key_length: int
    # """Internal attribute to keep track of the key's length"""

    __slots__ = "key", "key_length", "is_lazy"

    def __init__(self, key, length=None) -> None:
        super().__init__(length or ...)
        self.key = self.is_lazy = self.key_length = None
        self.set_key(key)

    def set_key(self, key, context=None) -> None:
        if callable(key) and context is None:
            # context lambda indicates the key will be computed at runtime
            self.key = key
            self.key_length = -1
            self.is_lazy = True
            return

        match key:
            case str():
                self.key = key.encode()
            case int():
                self.key = bytes([key])
            case bytes():
                self.key = key
            case _:
                raise InvalidValueError(
                    f"Expected a valid key type, got {key!r}", context
                )

        self.key_length = len(self.key)
        self.is_lazy = False

    def process(self, obj: bytes, context) -> bytes:
        length = len(obj)
        data = bytearray(length)
        key = self.key
        if self.is_lazy:
            self.set_key(key(context), context)

        self._do_process(obj, data)
        return bytes(data)

    def _do_process(self, src: bytes, dest: bytearray):
        raise NotImplementedError

    def pack_single(self, obj: bytes, context) -> None:
        context[CTX_STREAM].write(self.process(obj, context))

    def unpack_single(self, context) -> bytes:
        obj: bytes = super().unpack_single(context)
        return self.process(obj, context)


class Xor(KeyCipher):
    __slots__ = ()

    def _do_process(self, src: bytes, dest: bytearray):
        for i, e in enumerate(src):
            dest[i] = e ^ self.key[i % self.key_length]


class Or(KeyCipher):
    __slots__ = ()

    def _do_process(self, src: bytes, dest: bytearray):
        for i, e in enumerate(src):
            dest[i] = e | self.key[i % self.key_length]


class And(KeyCipher):
    __slots__ = ()

    def _do_process(self, src: bytes, dest: bytearray):
        for i, e in enumerate(src):
            dest[i] = e & self.key[i % self.key_length]
