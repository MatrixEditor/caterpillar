import pytest
import caterpillar

if caterpillar.native_support():
    from caterpillar.c import c_Option
    from caterpillar.py import Flag, Field

    def testc_option_init():
        option = c_Option("name")
        assert option.name == "name"

        option2 = c_Option("name", value=3)
        assert option2.name == "name"
        assert option2.value == 3
        # The equality check will be based on the name attribute
        assert option2 == option

        with pytest.raises(ValueError):
            # The name MUST NOT be empty
            c_Option("")

    def testc_option_compat():
        flag = Flag("name")
        option = c_Option("name")

        # All flags and options will be treated the same way
        assert flag == option

    def testc_option_field_compat():
        f = Field(lambda context: 1, flags={c_Option("name")})
        assert f.has_flag(c_Option("name"))
