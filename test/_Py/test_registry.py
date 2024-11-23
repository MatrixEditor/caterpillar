import pytest

from caterpillar import registry
from caterpillar.fields import uint16, Const


def test_registry_invalid_add():
    # in theory, any value can be added to the registry. However, your static
    # type checker should inform you about the invalid argument.
    registry.annotation_registry.append(None)

    # The result will raise an exception if the added handler is processed
    with pytest.raises(AttributeError):
        registry.to_struct(0x01)

    del registry.annotation_registry[-1]


def test_registry_valid_add():
    # A valid type converter should throw no errors
    @registry.TypeConverter(int)
    def int_converter(annotation, kwargs):
        return Const(annotation, uint16)

    registry.annotation_registry.append(int_converter)
    assert registry.to_struct(int(0x01)).__bits__ == 16
