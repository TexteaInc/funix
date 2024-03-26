from typing import Union

from funix.hint import PreFillEmpty, PreFillType

pre_fill_metadata: dict[str, list[str | int | PreFillEmpty]] = {}
"""
A dict, key is function ID, value is a list of indexes/keys of pre-fill parameters.
"""


def parse_pre_fill(pre_fill: PreFillType):
    global pre_fill_metadata
    for _, from_arg_function_info in pre_fill.items():
        if isinstance(from_arg_function_info, tuple):
            from_arg_function_address = str(id(from_arg_function_info[0]))
            from_arg_function_index_or_key = from_arg_function_info[1]
            if from_arg_function_address in pre_fill_metadata:
                pre_fill_metadata[from_arg_function_address].append(
                    from_arg_function_index_or_key
                )
            else:
                pre_fill_metadata[from_arg_function_address] = [
                    from_arg_function_index_or_key
                ]
        else:
            from_arg_function_address = str(id(from_arg_function_info))
            if from_arg_function_address in pre_fill_metadata:
                pre_fill_metadata[from_arg_function_address].append(PreFillEmpty)
            else:
                pre_fill_metadata[from_arg_function_address] = [PreFillEmpty]


def get_pre_fill_metadata(
    function_id: str,
) -> Union[list[str | int | PreFillEmpty], None]:
    return pre_fill_metadata.get(function_id, None)
