import typing

import funix


@funix.funix(
    widgets={"state": "select"},
    input_layout=[
        [{"markdown": "### Sender information"}],  # row 1
        [
            {"argument": "first_name", "width": 4},
            {"argument": "last_name", "width": 4},
        ],  # row 2
        [{"argument": "address", "width": 7}],  # row 3
        [  # row 4
            {"argument": "city", "width": 4},
            {"argument": "state", "width": 4},
            {"argument": "zip_code", "width": 3},
        ],
        [{"html": "<a href='http://funix.io'>We love Funix</a>"}],  # row 5
    ],
    output_layout=[
        [{"dividing": "zip code is "}],
        [{"return": 2}],
        [{"dividing": "from the town"}],
        [{"return": 0}, {"return": 1}],
    ],
)
def layout_shipping(
    first_name: str = "Funix",
    last_name: str = "Rocks",
    address: str = "1 Freedom Way",
    city: str = "Pythonia",
    state: typing.Literal[
        "ALABAMA",
        "ALASKA",
        "ARIZONA",
        "ARKANSAS",
        "CALIFORNIA",
        "COLORADO",
        "CONNECTICUT",
        "DELAWARE",
        "FLORIDA",
        "GEORGIA",
        "HAWAII",
        "IDAHO",
        "ILLINOIS",
        "INDIANA",
        "IOWA",
        "KANSAS",
        "KENTUCKY",
        "LOUISIANA",
        "MAINE",
        "MARYLAND",
        "MASSACHUSETTS",
        "MICHIGAN",
        "MINNESOTA",
        "MISSISSIPPI",
        "MISSOURI",
        "MONTANA",
        "NEBRASKA",
        "NEVADA",
        "NEW HAMPSHIRE",
        "NEW JERSEY",
        "NEW MEXICO",
        "NEW YORK",
        "NORTH CAROLINA",
        "NORTH DAKOTA",
        "OHIO",
        "OKLAHOMA",
        "OREGON",
        "PENNSYLVANIA",
        "RHODE ISLAND",
        "SOUTH CAROLINA",
        "SOUTH DAKOTA",
        "TENNESSEE",
        "TEXAS",
        "UTAH",
        "VERMONT",
        "VIRGINIA",
        "WASHINGTON",
        "WEST VIRGINIA",
        "WISCONSIN",
        "WYOMING",
    ] = "IOWA",
    zip_code: str = "1984",
) -> str:
    return f"You are {first_name} {last_name}, from the city of {city},  in the state of {state}."
