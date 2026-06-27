import pytest

from caterpillar import registry
from caterpillar.exception import ValidationError
from caterpillar.fields import uint16, uint32, Bytes, Const, Field
from caterpillar.model import getbits, struct
from caterpillar.byteorder import BigEndian


def test_registry_invalid_add():
    # fmt: off
    # in theory, any value can be added to the registry. However, your static
    # type checker should inform you about the invalid argument.
    registry.annotation_registry.append(None)  # pyright: ignore[reportArgumentType]

    # The result will raise an exception if the added handler is processed
    with pytest.raises(AttributeError):
        _ = registry.to_struct(0x01)

    del registry.annotation_registry[-1]


def test_registry_valid_add():
    # A valid type converter should throw no errors
    @registry.TypeConverter(int)
    def int_converter(annotation: int, kwargs):
        return Const(annotation, uint16)

    registry.annotation_registry.append(int_converter)
    s = registry.to_struct(int(0x01))
    assert getbits(s) == 16


def test_generic_alias_not_treated_as_context_lambda():
    # Subscripting a Generic class (e.g. Field[bytes, Bytes(4)]) yields a
    # callable generic alias. It must not be matched by the callable converter
    # (which would treat it as a context lambda and silently drop its data);
    # to_struct should raise instead.
    with pytest.raises(ValidationError):
        _ = registry.to_struct(Field[bytes, Bytes(4)])


def test_generic_alias_field_annotation_raises():
    # Using such a generic alias as a struct field annotation must fail loudly
    # rather than silently producing a field that drops bytes on pack.
    with pytest.raises(ValidationError):

        @struct(order=BigEndian)
        class Format:
            a: uint32
            reserved: Field[bytes, Bytes(4)]


def test_context_lambda_still_resolves_to_field():
    # Genuine context lambdas (plain callables) must keep resolving to a Field.
    s = registry.to_struct(lambda ctx: uint16)
    assert isinstance(s, Field)
