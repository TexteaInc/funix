import funix


@funix.funix(
    input_layout=[
        [{"markdown": "### Sender information"}],  # row 1
        [
            {"argument": "first_name", "width": 3},
            {"argument": "last_name", "width": 3},
        ],  # row 2
        [{"argument": "address", "width": 6}],  # row 3
        [  # row 4
            {"argument": "city", "width": 2.5},
            {"argument": "state", "width": 2},
            {"argument": "zip_code", "width": 2},
        ],
        [{"html": "<a href='http://funix.io'>We love Funix</a>"}],  # row 5
    ],
    output_layout=[
        [{"divider": "zip code is "}],
        [{"return_index": 2}],
        [{"divider": "from the town"}],
        [{"return_index": [0, 1]}],
    ],
)
def layout_shipping(
    first_name: str, last_name: str, address: str, city: str, state: str, zip_code: str
) -> (str, str, str):
    return city, state, zip_code
