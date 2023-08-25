"""
Test the funix.decorator.magic module.
"""

from inspect import Parameter
from typing import Dict, List, Literal, Optional, TypedDict, Union
from unittest import TestCase, main

from funix.decorator.magic import get_type_dict, get_type_widget_prop


class TestGetTypeDict(TestCase):
    def test_literal(self):
        self.assertEqual(
            get_type_dict(Literal["funix", "is", "the", "best"]),
            {"type": "str", "whitelist": ("funix", "is", "the", "best")},
        )
        self.assertEqual(
            get_type_dict(Literal[1, 2, 3, 4]),
            {"type": "int", "whitelist": (1, 2, 3, 4)},
        )

    def test_optional(self):
        self.assertEqual(
            get_type_dict(Optional[str]), {"type": "str", "optional": True}
        )
        self.assertEqual(get_type_dict(int | None), {"type": "int", "optional": True})
        self.assertEqual(
            get_type_dict(Union[bool, None]), {"type": "bool", "optional": True}
        )

    def test_normal(self):
        self.assertEqual(get_type_dict(bool), {"type": "bool"})
        self.assertEqual(get_type_dict(int), {"type": "int"})
        self.assertEqual(get_type_dict(float), {"type": "float"})
        self.assertEqual(get_type_dict(str), {"type": "str"})
        self.assertEqual(get_type_dict(list), {"type": "list"})
        self.assertEqual(get_type_dict(dict), {"type": "dict"})
        self.assertEqual(get_type_dict(range), {"type": "range"})

    def test_typing_list_and_dict(self):
        self.assertEqual(get_type_dict(List[str]), {"type": "typing.List[str]"})
        self.assertEqual(
            get_type_dict(Dict[str, int]), {"type": "typing.Dict[str, int]"}
        )

    def test_typed_dict(self):
        class TimedLyric(TypedDict):
            lyric: str
            timestamp: int

        self.assertEqual(
            get_type_dict(TimedLyric),
            {
                "type": "typing.Dict",
                "keys": {"lyric": "string", "timestamp": "integer"},
            },
        )

    def test_none(self):
        self.assertEqual(get_type_dict(None), {"type": None})


class TestGetTypeWidgetProp(TestCase):
    def test_single_get_type_widget_prop(self):
        result_int = get_type_widget_prop(
            "int",
            0,
            "",
            {},
            Parameter(
                name="i_can_fly",
                default=Parameter.empty,
                annotation=int,
                kind=Parameter.POSITIONAL_OR_KEYWORD,
            ).annotation,
        )

        self.assertEqual(result_int, {"type": "integer", "widget": ""})

        result_float = get_type_widget_prop(
            "float",
            0,
            "slider(0, 100, 0.1)",
            {},
            Parameter(
                name="this_code_will_not_be_kept_for_100_000_years",
                default=Parameter.empty,
                annotation=float,
                kind=Parameter.POSITIONAL_OR_KEYWORD,
            ).annotation,
        )

        self.assertEqual(
            result_float, {"type": "number", "widget": "slider(0, 100, 0.1)"}
        )

        result_str = get_type_widget_prop(
            "str",
            0,
            "",
            {"str": "password"},
            Parameter(
                name="d2FzdGVfeW91cl90aW1l",
                default="********",
                annotation=str,
                kind=Parameter.POSITIONAL_OR_KEYWORD,
            ).annotation,
        )

        self.assertEqual(result_str, {"type": "string", "widget": "password"})

    def test_dict_get_type_widget_prop(self):
        result_typing_dict = get_type_widget_prop(
            "typing.Dict",
            0,
            "json",
            {},
            Parameter(
                name="partly_cloudy",
                default=Parameter.empty,
                annotation=Dict,
                kind=Parameter.POSITIONAL_OR_KEYWORD,
            ).annotation,
        )

        self.assertEqual(
            result_typing_dict,
            {
                "type": "object",
                "widget": "json",
            },
        )

    def test_list_get_type_widget_prop(self):
        result_sheet = get_type_widget_prop(
            "typing.List[int]",
            0,
            ["sheet"],
            {},
            Parameter(
                name="what_a_big_universe",
                default=Parameter.empty,
                annotation=List[int],
                kind=Parameter.POSITIONAL_OR_KEYWORD,
            ).annotation,
        )

        self.assertEqual(
            result_sheet,
            {
                "type": "array",
                "widget": "sheet",
                "items": {"type": "integer", "widget": ""},
            },
        )

        result_sheet_with_switch = get_type_widget_prop(
            "typing.List[bool]",
            0,
            ["sheet", "switch"],
            {},
            Parameter(
                name="false_and_true",
                default=Parameter.empty,
                annotation=List[bool],
                kind=Parameter.POSITIONAL_OR_KEYWORD,
            ).annotation,
        )

        self.assertEqual(
            result_sheet_with_switch,
            {
                "type": "array",
                "widget": "sheet",
                "items": {"type": "boolean", "widget": "switch"},
            },
        )


if __name__ == "__main__":
    main(verbosity=2)
