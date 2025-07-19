# pylint: disable=unused-import, no-name-in-module
import pytest
import caterpillar

if caterpillar.native_support():
    from caterpillar._C import c_Context as Context

    def testc_context_init():
        """Simple tests around the Context class."""
        c1 = Context()
        assert len(c1) == 0

        c1.foo = 1
        assert len(c1) == 1

        c2 = Context(foo=1, bar=2)
        assert len(c2) == 2
        assert c2.foo == 1 and c2.bar == 2

    def testc_context_getattr():
        """Simple tests around the Context class using getattr"""
        c = Context(foo=1, bar=2)

        assert getattr(c, "foo") == 1
        assert getattr(c, "bar") == 2
        # This call will be transferred to the __context_getattr__ function
        assert getattr(c, "foo.__class__") is int

        with pytest.raises(AttributeError):
            # this class is strict when it comes to undefined
            # members
            _ = c.baz

    def testc_context_get_root():
        c = Context(a=1, _root=Context(b=2))
        # context must be another object
        assert c._root is not c

    def testc_context_setattr():
        c = Context(foo=1, bar=2)
        assert c.foo == 1
        assert c.bar == 2

        c.__context_setattr__("foo", 3)
        assert c.foo == 3

        c.baz = Context(a=1, b=2)
        c.__context_setattr__("baz.b", 3)
        assert c.baz.b == 3
