from unittest import TestCase, main
from unittest.mock import patch

from funix.decorator.runtime import _has_void_constructor, get_or_init_function
from funix.hint import WrapperException


class NoArgCtor:
    def __init__(self):
        self.value = 1


class WithArgCtor:
    def __init__(self, x: int):
        self.value = x


class VariadicCtor:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class TestAutoInitVoidConstructor(TestCase):
    def test_has_void_constructor(self):
        self.assertTrue(_has_void_constructor(NoArgCtor))
        self.assertFalse(_has_void_constructor(WithArgCtor))
        self.assertTrue(_has_void_constructor(VariadicCtor))

    def test_get_or_init_function_existing_instance(self):
        existing = object()
        with patch("funix.decorator.runtime.get_global_variable", return_value=existing):
            got = get_or_init_function("Demo", NoArgCtor, auto_init_when_missing=True)
        self.assertIs(got, existing)

    def test_get_or_init_function_auto_init(self):
        captured = {}

        def _capture_setter(name, value):
            captured["name"] = name
            captured["value"] = value

        with patch("funix.decorator.runtime.get_global_variable", return_value=None):
            with patch("funix.decorator.runtime.set_init_function", side_effect=_capture_setter):
                got = get_or_init_function("Demo", NoArgCtor, auto_init_when_missing=True)

        self.assertIsInstance(got, NoArgCtor)
        self.assertEqual(captured["name"], "Demo")
        self.assertIs(captured["value"], got)

    def test_get_or_init_function_requires_init_when_disabled(self):
        with patch("funix.decorator.runtime.get_global_variable", return_value=None):
            with self.assertRaises(WrapperException):
                get_or_init_function("Demo", WithArgCtor, auto_init_when_missing=False)


if __name__ == "__main__":
    main(verbosity=2)
