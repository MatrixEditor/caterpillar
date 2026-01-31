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
# pyright: reportPrivateUsage=false


from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable
from typing_extensions import override

from caterpillar.exception import UnsupportedOperation
from caterpillar.exception import InvalidValueError
from caterpillar.context import CTX_STREAM
from caterpillar.abc import (
    _ContextLambda,
    _ContextLike,
    _GreedyType,
    _StructLike,
    _IT,
    _ArgType,
)

from .common import Memory, Bytes
from ._mixin import get_args, get_kwargs

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.ciphers import (
        modes,
        CipherAlgorithm,
        CipherContext,
    )
    from cryptography.hazmat.primitives.padding import PaddingContext


@runtime_checkable
class Padding(Protocol):  # pylint: disable=missing-class-docstring
    def unpadder(self) -> "PaddingContext":
        """Abstract method to get an unpadder for padding."""
        ...

    def padder(self) -> "PaddingContext":
        """Abstract method to get a padder for padding."""
        ...


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
        length: int | _GreedyType | _ContextLambda[int],
        algorithm: type["CipherAlgorithm"],
        mode: "type[modes.Mode] | modes.Mode",
        padding: Padding | type[Padding] | None = None,
        algo_args: Iterable[_ArgType] | None = None,
        mode_args: Iterable[_ArgType] | None = None,
        padding_args: Iterable[_ArgType] | None = None,
        post: _StructLike | None = None,
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
        self._algo: "type[CipherAlgorithm]" = algorithm
        self._algo_args: Iterable[_ArgType] | None = algo_args
        self._mode: "type[modes.Mode] | modes.Mode" = mode
        self._mode_args: Iterable[_ArgType] | None = mode_args
        self._padding: Padding | type[Padding] | None = padding
        self._padding_args: Iterable[_ArgType] | None = padding_args
        self.post: _StructLike | None = post

    def algorithm(self, context: _ContextLike) -> "CipherAlgorithm":
        """
        Get the encryption algorithm instance.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: An instance of the encryption algorithm.
        :rtype: algorithms.CipherAlgorithm
        """
        # fmt: off
        from cryptography.hazmat.primitives.ciphers import CipherAlgorithm

        return self.get_instance(CipherAlgorithm, self._algo, self._algo_args, context)  # pyright: ignore[reportReturnType]

    def mode(self, context: _ContextLike) -> "modes.Mode | None":
        """
        Get the encryption mode instance.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: An instance of the encryption mode.
        :rtype: modes.Mode
        """
        from cryptography.hazmat.primitives.ciphers import modes

        return self.get_instance(modes.Mode, self._mode, self._mode_args, context)

    def padding(self, context: _ContextLike) -> Padding | None:
        """
        Get the padding scheme instance.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: An instance of the padding scheme.
        :rtype: Padding
        """
        return self.get_instance(Padding, self._padding, self._padding_args, context)

    def get_instance(
        self,
        type_: type[_IT],
        field: _IT | Any | None,
        args: dict[str, _ArgType] | Iterable[_ArgType] | None,
        context: _ContextLike,
    ) -> _IT | None:
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

        return field(*args, **kwargs)  # pyright: ignore[reportCallIssue]

    @override
    def pack_single(
        self, obj: bytes | memoryview | bytearray, context: _ContextLike
    ) -> None:
        """
        Pack a single element.

        :param obj: The element to pack.
        :type obj: Any
        :param context: The current operation context.
        :type context: _ContextLike
        """
        # fmt: off
        from cryptography.hazmat.primitives.ciphers import Cipher

        cipher = Cipher(self.algorithm(context), self.mode(context))
        padding = self.padding(context)

        data = obj if isinstance(obj, bytes) else bytes(obj)
        if padding:
            padder = padding.padder()
            data = padder.update(data) + padder.finalize()

        encryptor: "CipherContext" = cipher.encryptor()  # pyright: ignore[reportAttributeAccessIssue]
        super().pack_single(encryptor.update(data) + encryptor.finalize(), context)

    @override
    def unpack_single(self, context: _ContextLike) -> memoryview:
        """
        Unpack a single element.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: The unpacked element as a memoryview.
        :rtype: memoryview
        """
        # fmt: off
        from cryptography.hazmat.primitives.ciphers import Cipher

        value = super().unpack_single(context)
        cipher = Cipher(self.algorithm(context), self.mode(context))

        decryptor: "CipherContext" = cipher.decryptor()  # pyright: ignore[reportAttributeAccessIssue]
        data: bytes = decryptor.update(bytes(value)) + decryptor.finalize()

        padding = self.padding(context)
        if padding:
            unpadder = padding.unpadder()
            data = unpadder.update(data) + unpadder.finalize()
        return memoryview(data)


_KeyType = int | str | bytes


class KeyCipher(Bytes):
    # key: bytes
    # """The key that should be applied.

    # It will be converted automatically to bytes if not given.
    # """

    # key_length: int
    # """Internal attribute to keep track of the key's length"""

    __slots__: tuple[str, ...] = "key", "key_length", "key_fn"

    def __init__(
        self,
        key: _KeyType | _ContextLambda[_KeyType],
        length: _GreedyType | _ContextLambda[int] | int | None = None,
    ) -> None:
        super().__init__(length or ...)
        self.key: bytes = b""
        self.key_fn: _ContextLambda[_KeyType] | None = None
        self.key_length: int = -1
        self.set_key(key)

    def is_lazy(self) -> bool:
        return self.key_fn is not None

    def set_key(
        self,
        key: _KeyType | _ContextLambda[_KeyType],
        context: _ContextLike | None = None,
    ) -> None:
        if callable(key) and context is None:
            # context lambda indicates the key will be computed at runtime
            self.key_fn = key
            self.key_length = -1
            return

        self.key_fn = None
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

    def process(self, obj: bytes, context: _ContextLike) -> bytes:
        length = len(obj)
        data = bytearray(length)
        if self.key_fn:
            self.set_key(self.key_fn(context), context)

        self._do_process(obj, data)
        return bytes(data)

    def _do_process(self, src: bytes, dest: bytearray) -> None:
        raise NotImplementedError

    @override
    def pack_single(self, obj: bytes, context: _ContextLike) -> None:
        context[CTX_STREAM].write(self.process(obj, context))

    @override
    def unpack_single(self, context: _ContextLike) -> bytes:
        obj: bytes = super().unpack_single(context)
        return self.process(obj, context)


class Xor(KeyCipher):
    __slots__: tuple[()] = ()

    @override
    def _do_process(self, src: bytes, dest: bytearray) -> None:
        for i, e in enumerate(src):
            dest[i] = e ^ self.key[i % self.key_length]


class Or(KeyCipher):
    __slots__: tuple[()] = ()

    @override
    def _do_process(self, src: bytes, dest: bytearray) -> None:
        for i, e in enumerate(src):
            dest[i] = e | self.key[i % self.key_length]


class And(KeyCipher):
    __slots__: tuple[()] = ()

    @override
    def _do_process(self, src: bytes, dest: bytearray) -> None:
        for i, e in enumerate(src):
            dest[i] = e & self.key[i % self.key_length]
