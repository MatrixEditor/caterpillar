from caterpillar._C import *  # noqa


def struct(cls: type = None, /, **kwargs) -> type:
    """Decorator for new struct classes using the C API.

    >>> @struct
    ... class MyStruct:
    ...     pass

    :param cls: The target class used as the base model.
    :param options: Additional options specifying what to include in the final class.
    :param endian: Optional configuration value for the byte order of a field.
    :param arch: Global architecture definition (will be inferred on all fields).
    :param field_options: Additional field options.
    """
    def wrap(cls) -> type:
        return Struct(cls, alter_model=True, **kwargs).model

    if cls is not None:
        return Struct(cls, alter_model=True, **kwargs).model

    return wrap
