import typing, os, json

import IPython
import ipywidgets
import requests 

import easypost


import funix

@funix.funix(
    argument_labels={
        # "EASYPOST_API_KEY": "EasyPost API key. Do NOT use your production key here. ",
        "from_who": "Sender name",
        "from_address_1": "Sender address 1",
        "from_address_2": "Sender address 2",
        "from_city": "city",
        "from_state": "state",
        "from_zip": "zip code",
        "to_who": "Receiver name",
        "to_address_1": "Receiver address 1",
        "to_address_2": "Receiver address 2",
        "to_city": "city",
        "to_state": "state",
        "to_zip": "zip code",
        "weight": "weight (oz)",
        "L": "length (in)",
        "W": "width (in)",
        "H": "height (in)",
        "value": "value ($)",
        "package": "package type",
    },
    input_layout=[
        [
            {"markdown": "Your EASYPOST API key"},
            {"argument": "EASYPOST_API_KEY", "width": 6},
        ],
        [{"markdown": "### Sender information"}],
        [{"argument": "from_who", "width": 4}],
        [{"argument": "from_address_1", "width": 6}],
        [{"argument": "from_address_2", "width": 6}],
        [
            {"argument": "from_city", "width": 3},
            {"argument": "from_state", "width": 2.5},
            {"argument": "from_zip", "width": 3},
        ],
        [{"markdown": "### Receiver information"}],
        [{"argument": "to_who", "width": 4}],
        [{"argument": "to_address_1", "width": 6}],
        [{"argument": "to_address_2", "width": 6}],
        [
            {"argument": "to_city", "width": 3},
            {"argument": "to_state", "width": 2},
            {"argument": "to_zip", "width": 3},
        ],
        [{"markdown": "### Package information"}],
        [
            {"markdown": "Dimension: ", "width": 2},
            {"argument": "L", "width": 2},
            {"markdown": "x", "width": 0.5},
            {"argument": "W", "width": 2},
            {"markdown": "x", "width": 0.5},
            {"argument": "H", "width": 2},
        ],
        [{"argument": "weight", "width": 2}, {"argument": "value", "width": 2}],
        [{"argument": "package"}],
    ],
)
def easypost_demo(
    EASYPOST_API_KEY: ipywidgets.Password= "12345",
    from_who: str = "Funix Rocks",
    from_address_1: str = "1 Freedom Way",
    from_address_2: str = "",
    from_city: str = "Lubbock",
    from_state: str = "TX",
    from_zip: str = "79409",
    to_who: str = "Funix Sounds",
    to_address_1: str = "1 Python Drive",
    to_address_2: str = "",
    to_city: str = "Ames",
    to_state: str = "IA",
    to_zip: str = "50014",
    weight: int = 3,
    L: float = 6,
    W: float = 8,
    H: float = 0.4,
    value: float = 5,
    package: typing.Literal["Parcel", "Flat", "Letter"] = "Parcel",
) -> typing.Tuple[IPython.display.Markdown, IPython.display.HTML, IPython.display.Image]:
    from_address = {
        "name": from_who,
        "street1": from_address_1,
        "street2": from_address_2,
        "city": from_city,
        "state": from_state,
        "zip": from_zip,
        "country": "USA",
        "phone": "",
    }

    to_address = {
        "name": to_who,
        "street1": to_address_1,
        "street2": to_address_2,
        "city": to_city,
        "state": to_state,
        "zip": to_zip,
        "country": "USA",
        "phone": "",
    }

    parcel = {
        "length": L,
        "width": W,
        "height": H,
        "weight": weight,
        "predefined_package": package,
    }

    #### Using requests 
    # header = {
    #     "Content-Type": "application/json", 
    #     "Authorization": f"Basic {EASYPOST_API_KEY.value}",
    #     # EZTKcc447c394f5640d08193d88779185491hjr0KcWaKXLcCz2LMegntw
    #     }

    # payload = {
    #     "shipment":{
    #         "to_address": to_address,
    #         "from_address": from_address,
    #         "parcel": parcel,
    #     }
    # }

    # response = requests.post(
    #     "https://api.easypost.com/v2/shipments", headers=header, json=payload
    # )
    #### End of using requests

    client = easypost.EasyPostClient(EASYPOST_API_KEY.value)

    try: 
        shipment = client.shipment.create(
            to_address=to_address, 
            from_address=from_address, 
            parcel=parcel
        )
    except Exception as e:
        cost = "100.00"
        tracking_number = "1234565"
        label_url = "https://easypost-files.s3.us-west-2.amazonaws.com/files/postage_label/20230710/e657608f44b6ec482c86742b7b8ea5d74d.png"

        return (
        f"# Ah oh ",
        f'You failed to provide a valid EasyPost API KEY. Hence, a placeholder shipping label is provided below to illustrate how the app is expected to function.',
        label_url,
        # json.loads(str(shipment)),
    )
        

    bought_shipment = client.shipment.buy(shipment.id, rate=shipment.lowest_rate())

    cost = bought_shipment['selected_rate']['rate']
    tracking_number = bought_shipment['tracker']['tracking_code']
    label_url = bought_shipment['postage_label']['label_url']

    return (
        f"The shipment cost you **${cost}**",
        f'Tracking number (click to track):\
        <a href="https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1={tracking_number}">{tracking_number}</a>',
        label_url,
        # json.loads(str(shipment)),
    )
