from typing import Any

from funix.hint import ConditionalVisibleType


def parse_all_of(
    conditional_visible: ConditionalVisibleType, json_schema_props: dict
) -> list:
    all_of = []
    delete_keys = set()

    for conditional_visible_item in conditional_visible:
        config = {
            "if": {"properties": {}},
            "then": {"properties": {}},
            "required": [],
        }
        if_items: Any = conditional_visible_item["when"]
        then_items = conditional_visible_item["show"]
        for if_item in if_items.keys():
            config["if"]["properties"][if_item] = {"const": if_items[if_item]}
        for then_item in then_items:
            config["then"]["properties"][then_item] = json_schema_props[then_item]
            config["required"].append(then_item)
            delete_keys.add(then_item)
        all_of.append(config)

    for key in delete_keys:
        json_schema_props.pop(key)

    return all_of
