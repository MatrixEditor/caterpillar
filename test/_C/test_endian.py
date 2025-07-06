import pytest
import caterpillar

if caterpillar.native_support():
    from caterpillar.c import c_Arch, c_Endian

    def testc_arch_init():
        c_Arch("name", 32)
        with pytest.raises(TypeError):
            c_Arch()

    def testc_endian_init():
        c_Endian("name", ord("!"))
        with pytest.raises(TypeError):
            c_Endian()

    def testc_arch_repr():
        a = c_Arch("name", 32)
        assert repr(a) == "<Arch 'name' x32>"

    def testc_endian_repr():
        le = c_Endian("name", ord("<"))
        assert repr(le) == "<le>"

        be = c_Endian("name", ord(">"))
        net = c_Endian("name", ord("!"))
        assert repr(be) == "<be>" and repr(net) == "<be>"

        ne = c_Endian("name", ord("="))
        assert repr(ne) == "<native-endian>"

        custom = c_Endian("Custom", ord("/"))
        assert repr(custom) == "<Endian: Custom ch='/'>"

    def test_set_byteorder():
        class A:
            def __set_byteorder__(self, order):
                return self

        class B:
            pass

        a = A()
        b = B()

        # You IDE or whatever type checker you're using should inform you
        # that you can't add an object of type B to a c_Endian, because it
        # doesn't conform to the _SupportsSetEndian protocol.
        e = c_Endian("name", ord("!"))
        with pytest.raises(AttributeError):
            e + b

        # But you can add an object of type A to c_Endian
        d = e + a
        assert d is a
