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
import sys
import hashlib
import warnings
import zlib

from typing import Any, Callable, Optional, Self, Type

from caterpillar.abc import _ContextLike, _StructLike, _ContextLambda
from caterpillar.context import CTX_OBJECT, CTX_STREAM
from caterpillar.exception import StructException, ValidationError
from caterpillar.shared import Action
from caterpillar.fields.hook import (
    IOHook,
)
from ._base import Field
from .common import Bytes, uint32

DEFAULT_DIGEST_PATH = "digest"

class _DigestValue:
    """
    A placeholder class representing a digest value.

    This class is used as a placeholder for digests or checksum values in
    the context of cryptographic algorithms or other hash-like operations.
    """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Algorithm:
    """
    .. versionadded:: 2.4.0

    A class representing a cryptographic or checksum algorithm.

    This class allows for the creation, updating, and finalization of values using a
    specified algorithm. It abstracts the necessary methods to interact with
    hash algorithms or checksums like SHA256 or CRC32.

    Example usage with SHA256:

    >>> SHA256 = Algorithm(
    ...     create=lambda context: hashlib.sha256(),
    ...     update=lambda algo_obj, data, context: algo_obj.update(data),
    ...     digest=lambda algo_obj, context: algo_obj.digest(),
    ... )

    Example usage with CRC32:

    >>> CRC32 = Algorithm(
    ...     create=lambda context: zlib.crc32(b""),
    ...     update=lambda crc_value, data, context: crc32(data, crc_value),
    ...     digest=lambda crc_value, context: crc_value,
    ... )

    This class can be used to handle both cryptographic algorithms and non-cryptographic checksums.

    :param create: A callable that creates an instance of the algorithm or checksum.
    :type create: Callable[[_ContextLike], Any]
    :param update: A callable that updates the algorithm or checksum with new data.
    :type update: Callable[[Any, bytes, _ContextLike], Any]
    :param digest: A callable that returns the digest or checksum value.
    :type digest: Callable[[Any, _ContextLike], bytes]
    :param name: An optional name for the algorithm.
    :type name: Optional[str]
    """

    __slots__ = ("_create", "_update", "_digest", "name")

    def __init__(
        self,
        create: Callable[[_ContextLike], Any] | None = None,
        update: Callable[[Any, bytes, _ContextLike], Any] | None = None,
        digest: Callable[[Any, _ContextLike], bytes] | None = None,
        name: Optional[str] = None,
    ) -> None:
        self._create = create
        self._update = update
        self._digest = digest
        self.name = name

    def __repr__(self) -> str:
        """
        Return a string representation of the Algorithm instance.

        The representation includes the name of the algorithm, or '<not set>' if no name is provided.

        :return: The string representation of the algorithm.
        :rtype: str
        """
        return f"<{self.__class__.__name__} name={self.name or '<not set>'!r}>"

    def create(self, context: _ContextLike) -> Any:
        """
        Create an instance of the algorithm or checksum using the provided context.

        This method invokes the `create` callable passed during initialization.

        :param context: The context in which to create the algorithm instance.
        :type context: _ContextLike
        :return: An instance of the algorithm or checksum.
        :rtype: Any
        :raises NotImplementedError: If the `create` method is not implemented for this algorithm.
        """
        if self._create is not None:
            return self._create(context)

        raise NotImplementedError("create() is not implemented for this algorithm")

    def update(self, algo_obj: Any, data: bytes, context: _ContextLike) -> Any:
        """
        Update the algorithm or checksum with the given data.

        This method invokes the `update` callable passed during initialization.

        :param algo_obj: The algorithm instance to update (e.g., a SHA256 object).
        :param data: The data to be used for updating the algorithm.
        :param context: The context in which the update takes place.
        :type algo_obj: Any
        :type data: bytes
        :type context: _ContextLike
        :return: The updated algorithm instance or checksum value.
        :rtype: Any
        :raises NotImplementedError: If the `update` method is not implemented for this algorithm.
        """
        if self._update is not None:
            return self._update(algo_obj, data, context)

        raise NotImplementedError("update() is not implemented for this algorithm")

    def digest(self, algo_obj: Any, context: _ContextLike) -> bytes:
        """
        Compute the digest or checksum value from the algorithm instance.

        This method invokes the `digest` callable passed during initialization.

        :param algo_obj: The algorithm instance from which to compute the digest.
        :param context: The context in which the digest operation takes place.
        :type algo_obj: Any
        :type context: _ContextLike
        :return: The computed digest or checksum value.
        :rtype: bytes
        :raises NotImplementedError: If the `digest` method is not implemented for this algorithm.
        """
        if self._digest is not None:
            return self._digest(algo_obj, context)

        raise NotImplementedError("digest() is not implemented for this algorithm")


class Digest:
    """A class to handle the creation, updating, and verification of digests
    using a specified algorithm.

    .. versionadded:: 2.4.0

    .. versionchanged:: 2.4.3

        Python 3.14 is **not** supported.

    The `Digest` class allows you to integrate hash or checksum algorithms
    into a struct by installing hooks that manage the digest state during
    packing and unpacking. It supports automatic calculation and validation
    of digests during serialization (packing) and deserialization (unpacking).

    Example usage:

    >>> @struct
    ... class Format:
    ...     with Digest(SHA256, Bytes(32), "sha256", verify=True):
    ...         user_data: Bytes(10)
    ...

    This example defines a struct with a `user_data` field and a `sha256` digest
    field. The `Digest` class automatically calculates the SHA256 checksum of
    `user_data` during packing and validates the checksum during unpacking.

    The resulting struct has the following fields:

    >>> Format.__struct__.fields
    [
        Action(Digest.begin),
        Field('user_data', struct=<Bytes>),
        Action(Digest.end),
        Field('sha256', struct=<Bytes>),
        Action(Digest.verify)
    ]

    The `Action` objects install hooks into the current stream for digest calculation
    and validation. When packing an object, the digest will be updated automatically:

    >>> obj = Format(user_data=b"helloworld" * 10)
    Format(user_data=b"helloworld", sha256=<_DigestValue>)

    On packing, the digest is calculated and included in the serialized output:

    >>> pack(obj, Format)
    b"hello world\\xb9M'\\xb9" ...

    If verification is enabled, unpacking will check the validity of the digest:

    >>> unpack(Format, b"invalid data with sha256")
    Traceback (most recent call last):
    ...
    caterpillar.exception.ValidationError: Failed to verify digest of 'sha256'!
    - Expected: <expected_digest_value>
    - Actual: <actual_digest_value>
    Context-Path: <root>.sha256

    :param algorithm: The checksum or cryptographic algorithm used to generate the digest.
    :type algorithm: Algorithm
    :param struct: The struct to which the digest will be attached.
    :type struct: _StructLike
    :param name: An optional name for the digest field (defaults to 'sha256' or another default name).
    :type name: Optional[str]
    :param verify: Whether to enable verification of the digest upon unpacking. Default is False.
    :type verify: bool
    :param path: Optional path to the digest field in the context, used for accessing and storing the digest.
    :type path: Optional[str]
    """

    def __init__(
        self,
        algorithm: Algorithm,
        struct: _StructLike,
        name: Optional[str] = None,
        verify: bool = False,
        path: Optional[str] = None,
    ) -> None:
        if (sys.version_info.major, sys.version_info.minor) >= (3, 14):
            warnings.warn(
                "Python3.14 breaks support for Digest fields. The hash must be calculated "
                "manually until a fix has been released."
            )

        self.algo = algorithm
        self.name = name or DEFAULT_DIGEST_PATH
        if "." in self.name:
            raise ValueError(
                "Digest name must not contain '.' character. Use path instead."
            )

        # IO will be initialized in self.begin
        self._hook = IOHook(io=None, update=self.update)
        self.struct = struct
        self._digest = None
        self._obj = None
        self._verify = verify
        self.path = path or f"{CTX_OBJECT}.{self.name}"

    def _get_annotations(self, frame: Any) -> dict[str, Any]:
        """
        Retrieve the annotations (i.e., field definitions) from the current frame's local variables.

        :param frame: The current stack frame from which to retrieve annotations.
        :type frame: Any
        :return: A dictionary of annotations for the current struct.
        :rtype: dict[str, Any]
        :raises StructException: If annotations cannot be retrieved from the frame.
        """
        try:
            # This will not work on Python3.14+ but supresses errors
            if "__annotations__" not in frame.f_locals:
                frame.f_locals["__annotations__"] = {}

            return frame.f_locals["__annotations__"]
        except KeyError as exc:
            module = frame.f_locals.get("__module__")
            qualname = frame.f_locals.get("__qualname__")
            msg = f"Could not get annotations in {module} (context={qualname!r})"
            raise StructException(msg) from exc

    def __repr__(self) -> str:
        return f"Digest(algo={self.algo!r}, verify={self._verify!r})"

    def __enter__(self) -> Self:
        """
        Install the start action for the digest field during struct definition.

        This method is used in a `with` block to set up the digest calculation at the beginning.

        :return: The current Digest instance for further use.
        :rtype: Self
        :raises ValueError: If the start action already exists.
        """
        frame = sys._getframe(1)
        annotations = self._get_annotations(frame)
        # 1. install action to create checksum
        start_action_name = f"{self.name}_start"
        if start_action_name in annotations:
            raise ValueError(
                (
                    f"Digest with start action {self.name!r} already exists! "
                    "Make sure that each digest uses a unique name."
                )
            )

        if self.name in annotations:
            raise ValueError(
                (
                    f"Digest with name {self.name!r} already exists "
                    "before the start action. Make sure that each digest "
                    "uses a unique name."
                )
            )

        annotations[start_action_name] = Action(self.begin, self.begin)
        return self

    def __exit__(self, *_) -> None:
        """
        Install the end action for the digest field and finalize the struct field definitions.

        This method is used to finalize the digest field in a `with` block.

        :raises ValueError: If the end action already exists.
        """
        frame = sys._getframe(1)
        annotations = self._get_annotations(frame)
        # 2. add action to finish checksum
        end_action_name = f"{self.name}_end"
        if end_action_name in annotations:
            raise ValueError(
                (
                    f"Digest with end action {self.name!r} already exists! "
                    "Make sure that each checksum uses a unique name."
                )
            )
        annotations[end_action_name] = Action(self.end_pack, self.end_unpack)
        annotations[self.name] = Field(self.struct)
        frame.f_locals[self.name] = _DigestValue()
        if self._verify:
            annotations[f"{self.name}_verify"] = Action(unpack=self.verfiy)

    def begin(self, context: _ContextLike) -> None:
        """
        Initialize the digest calculation at the beginning of packing/unpacking.

        This method sets up the algorithm and prepares the context for checksum calculation.

        :param context: The current context during packing/unpacking.
        :type context: _ContextLike
        """
        self._hook._io = context[CTX_STREAM]
        self._hook.init(context)
        self._obj = self.algo.create(context)

    def end_pack(self, context: _ContextLike) -> None:
        """
        Finalize the digest calculation at the end of packing/unpacking.

        This method calculates the digest and stores it in the context for later use.

        :param context: The current context during packing/unpacking.
        :type context: _ContextLike
        """
        self._digest = self.algo.digest(self._obj, context)
        context.__context_setattr__(self.path or self.name, self._digest)
        self._hook.finish(context)

    def end_unpack(self, context: _ContextLike) -> None:
        """
        Finalize the digest calculation at the end of unpacking.

        This method retrieves the digest from the context and updates the checksum.

        :param context: The current context during unpacking.
        :type context: _ContextLike
        """
        self._digest = self.algo.digest(self._obj, context)
        self._hook.finish(context)

    def update(self, data: bytes, context: _ContextLike) -> None:
        """
        Update the checksum with new data during packing/unpacking.

        This method feeds new data into the algorithm to update the digest.

        :param data: The data to update the checksum with.
        :type data: bytes
        :param context: The current context during packing/unpacking.
        :type context: _ContextLike
        """
        self._obj = self.algo.update(self._obj, data, context) or self._obj

    def verfiy(self, context: _ContextLike) -> None:
        """
        Verify the checksum upon unpacking.

        This method checks if the digest calculated during unpacking matches the expected digest.
        If verification fails, a `ValidationError` is raised.

        :param context: The current context during unpacking.
        :type context: _ContextLike
        :raises ValidationError: If the digest verification fails.
        """
        # we assume self._verify is True
        digest = context.__context_getattr__(self.path or self.name)
        if digest != self._digest:
            digest_raw = digest.hex() if isinstance(digest, bytes) else digest
            expected_digest_raw = (
                self._digest.hex() if isinstance(self._digest, bytes) else self._digest
            )
            raise ValidationError(
                (
                    f"Failed to verify digest of {self.name!r} using "
                    f"algorithm {self.algo.name or '<no name>'} \n"
                    f" - Expected: {expected_digest_raw!r} \n"
                    f" - Actual: {digest_raw!r}"
                ),
                context,
            )


# --- public algorithms ---
def _hash_digest(algo: Algorithm, struct: _StructLike):
    """
    A utility function to create a `Digest` wrapper for a specific hash algorithm and struct.
    The wrapper initializes the digest calculation based on the algorithm provided.

    :param algo: The hash algorithm to be used.
    :type algo: Algorithm
    :param struct: The struct type to use for digest.
    :type struct: _StructLike
    :return: A callable that returns a `Digest` instance.
    :rtype: Callable
    """

    def _wrapper(
        name: Optional[str] = None,
        verify: bool = False,
        path: Optional[str] = None,
    ) -> Digest:
        return Digest(algo, struct, name, verify, path)

    return _wrapper


def _hashlib_algo(func) -> Algorithm:
    """
    Creates an `Algorithm` object from a hash function (e.g., hashlib.sha256).

    :param func: The hash function to be wrapped.
    :type func: Callable
    :return: An `Algorithm` instance that can be used with a Digest.
    :rtype: Algorithm
    """
    return Algorithm(
        create=lambda context: func(),
        update=lambda hash_obj, data, context: hash_obj.update(data),
        digest=lambda hash_obj, context: hash_obj.digest(),
        name=func.__name__,
    )


Crc32_Algo = Algorithm(
    create=lambda context: zlib.crc32(b""),
    update=lambda hash_obj, data, context: zlib.crc32(data, hash_obj),
    digest=lambda hash_obj, context: hash_obj,
    name="crc32",
)
Crc32 = _hash_digest(Crc32_Algo, uint32)

Adler_Algo = Algorithm(
    create=lambda context: zlib.adler32(b""),
    update=lambda hash_obj, data, context: zlib.adler32(data, hash_obj),
    digest=lambda hash_obj, context: hash_obj,
    name="adler32",
)
Adler = _hash_digest(Adler_Algo, uint32)

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives import hmac

    def _cryptography_hash_algo(cls: Type[hashes.HashAlgorithm]):
        """
        Creates an `Algorithm` from a cryptography `hashes.HashAlgorithm` class.

        :param cls: The cryptography hash algorithm class (e.g., `hashes.SHA256`).
        :param args: Additional arguments for initializing the algorithm.
        :param kwargs: Additional keyword arguments for initializing the algorithm.
        :return: An `Algorithm` instance.
        """
        return Algorithm(
            create=lambda context: hashes.Hash(cls()),
            update=lambda hash_obj, data, context: hash_obj.update(data),
            digest=lambda hash_obj, context: hash_obj.finalize(),
            name=getattr(cls, "name"),
        )

    Sha1_Algo = _cryptography_hash_algo(hashes.SHA1)
    Sha2_224_Algo = _cryptography_hash_algo(hashes.SHA224)
    Sha2_256_Algo = _cryptography_hash_algo(hashes.SHA256)
    Sha2_384_Algo = _cryptography_hash_algo(hashes.SHA384)
    Sha2_512_Algo = _cryptography_hash_algo(hashes.SHA512)
    Sha3_224_Algo = _cryptography_hash_algo(hashes.SHA3_224)
    Sha3_256_Algo = _cryptography_hash_algo(hashes.SHA3_256)
    Sha3_384_Algo = _cryptography_hash_algo(hashes.SHA3_384)
    Sha3_512_Algo = _cryptography_hash_algo(hashes.SHA3_512)
    Md5_Algo = _cryptography_hash_algo(hashes.MD5)

    Sha1 = _hash_digest(Sha1_Algo, Bytes(20))
    Sha2_224 = _hash_digest(Sha2_224_Algo, Bytes(28))
    Sha2_256 = _hash_digest(Sha2_256_Algo, Bytes(32))
    Sha2_384 = _hash_digest(Sha2_384_Algo, Bytes(48))
    Sha2_512 = _hash_digest(Sha2_512_Algo, Bytes(64))
    Sha3_224 = _hash_digest(Sha3_224_Algo, Bytes(28))
    Sha3_256 = _hash_digest(Sha3_256_Algo, Bytes(32))
    Sha3_384 = _hash_digest(Sha3_384_Algo, Bytes(48))
    Sha3_512 = _hash_digest(Sha3_512_Algo, Bytes(64))
    Md5 = _hash_digest(Md5_Algo, Bytes(16))

    class HMACAlgorithm(Algorithm):
        """
        HMAC (Hash-based Message Authentication Code) algorithm implementation.

        This class wraps an HMAC algorithm using a specified hash function and key.
        """

        def __init__(
            self,
            key: bytes | _ContextLambda,
            algorithm: hashes.HashAlgorithm,
        ) -> None:
            super().__init__(name=f"hmac_{algorithm.name}")
            self._key = key
            self._algorithm = algorithm

        def create(self, context: _ContextLike) -> Any:
            """
            Creates an HMAC object with the provided key and algorithm.
            """
            key = self._key(context) if callable(self._key) else self._key
            return hmac.HMAC(key, self._algorithm)

        def update(self, algo_obj: Any, data: bytes, context: _ContextLike) -> Any:
            """
            Updates the HMAC object with new data.
            """
            return algo_obj.update(data)

        def digest(self, algo_obj: Any, context: _ContextLike) -> Any:
            """
            Finalizes the HMAC object and returns the computed digest.
            """
            return algo_obj.finalize()

    class HMAC(Digest):
        """
        HMAC Digest handler, used to create and verify HMACs based on a provided key and algorithm.
        """

        def __init__(
            self,
            key: bytes | _ContextLambda,
            algorithm: hashes.HashAlgorithm,
            name: Optional[str] = None,
            verify: bool = False,
            path: Optional[str] = None,
        ) -> None:
            super().__init__(
                HMACAlgorithm(key, algorithm),
                Bytes(algorithm.digest_size),
                name,
                verify,
                path,
            )

except ImportError:
    Sha1_Algo = _hashlib_algo(hashlib.sha1)
    Sha2_224_Algo = _hashlib_algo(hashlib.sha224)
    Sha2_256_Algo = _hashlib_algo(hashlib.sha256)
    Sha2_384_Algo = _hashlib_algo(hashlib.sha384)
    Sha2_512_Algo = _hashlib_algo(hashlib.sha512)
    Sha3_224_Algo = _hashlib_algo(hashlib.sha3_224)
    Sha3_256_Algo = _hashlib_algo(hashlib.sha3_256)
    Sha3_384_Algo = _hashlib_algo(hashlib.sha3_384)
    Sha3_512_Algo = _hashlib_algo(hashlib.sha3_512)

    Md5_Algo = _hashlib_algo(hashlib.md5)
    Sm3_Algo = None

    Sha1 = _hash_digest(Sha1_Algo, Bytes(32))
    Sha2_224 = _hash_digest(Sha2_224_Algo, Bytes(28))
    Sha2_256 = _hash_digest(Sha2_256_Algo, Bytes(32))
    Sha2_384 = _hash_digest(Sha2_384_Algo, Bytes(48))
    Sha2_512 = _hash_digest(Sha2_512_Algo, Bytes(64))
    Sha3_224 = _hash_digest(Sha3_224_Algo, Bytes(28))
    Sha3_256 = _hash_digest(Sha3_256_Algo, Bytes(32))
    Sha3_384 = _hash_digest(Sha3_384_Algo, Bytes(48))
    Sha3_512 = _hash_digest(Sha3_512_Algo, Bytes(64))
    Md5 = _hash_digest(Md5_Algo, Bytes(16))
    Sm3 = None

    HMACAlgorithm = None
    HMAC = None
