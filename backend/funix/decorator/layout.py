"""
Layout decorator
"""


def convert_row_item(row_item: dict, item_type: str) -> dict:
    """
    Convert a layout row item(block) to frontend-readable item.

    Parameters:
        row_item (dict): The row item.
        item_type (str): The item type.

    Returns:
        dict: The converted item.
    """
    converted_item = row_item
    converted_item["type"] = item_type
    converted_item["content"] = row_item[item_type]
    converted_item.pop(item_type)
    return converted_item


def handle_input_layout(input_layout: list) -> tuple[list, dict]:
    return_input_layout = []
    decorated_params = {}
    for row in input_layout:
        row_layout = []
        for row_item in row:
            row_item_done = row_item
            for common_row_item_key in ["markdown", "html"]:
                if common_row_item_key in row_item:
                    row_item_done = convert_row_item(row_item, common_row_item_key)
            if "argument" in row_item:
                if row_item["argument"] not in decorated_params:
                    decorated_params[row_item["argument"]] = {}
                decorated_params[row_item["argument"]]["customLayout"] = True
                row_item_done["type"] = "argument"
            elif "divider" in row_item:
                row_item_done["type"] = "divider"
                if isinstance(row_item["divider"], str):
                    row_item_done["content"] = row_item_done["divider"]
                row_item_done.pop("divider")
            row_layout.append(row_item_done)
        return_input_layout.append(row_layout)
    return return_input_layout, decorated_params


def handle_output_layout(output_layout: list) -> tuple[list, list]:
    return_output_layout = []
    return_output_indexes = []
    for row in output_layout:
        row_layout = []
        for row_item in row:
            row_item_done = row_item
            for common_row_item_key in [
                "markdown",
                "html",
                "images",
                "videos",
                "audios",
                "files",
            ]:
                if common_row_item_key in row_item:
                    row_item_done = convert_row_item(row_item, common_row_item_key)
            if "divider" in row_item:
                row_item_done["type"] = "divider"
                if isinstance(row_item["divider"], str):
                    row_item_done["content"] = row_item_done["divider"]
                row_item_done.pop("divider")
            elif "code" in row_item:
                row_item_done = row_item
                row_item_done["type"] = "code"
                row_item_done["content"] = row_item_done["code"]
                row_item_done.pop("code")
            elif "return_index" in row_item:
                row_item_done["type"] = "return_index"
                row_item_done["index"] = row_item_done["return_index"]
                row_item_done.pop("return_index")
                if isinstance(row_item_done["index"], int):
                    return_output_indexes.append(row_item_done["index"])
                elif isinstance(row_item_done["index"], list):
                    return_output_indexes.extend(row_item_done["index"])
            row_layout.append(row_item_done)
        return_output_layout.append(row_layout)
    return return_output_layout, return_output_indexes
