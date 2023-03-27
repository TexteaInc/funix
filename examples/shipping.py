import typing, os

import easypost
easypost.api_key = os.getenv("EASYPOST_API_KEY")

import funix 

@funix.funix(
    argument_labels={
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
    widgets={"package": "radio", "EASYPOST_API_KEY": "password"},
    input_layout=[
        [{"markdown": "Your EASYPOST API key (optional)"}, {"argument":"EASYPOST_API_KEY", "width": 6}],
        [{"markdown": "### Sender information"}], 
        [{"argument": "from_who", "width": 4}], 
        [{"argument": "from_address_1", "width": 6}],
        [{"argument": "from_address_2", "width": 6}],
        [{"argument": "from_city", "width": 2}, {"argument": "from_state", "width": 2}, {"argument": "from_zip", "width": 2}],
        [{"markdown": "### Receiver information"}],
        [{"argument": "to_who", "width": 4}],
        [{"argument": "to_address_1", "width": 6}],
        [{"argument": "to_address_2", "width": 6}],
        [{"argument": "to_city", "width": 2}, {"argument": "to_state", "width": 2}, {"argument": "to_zip", "width": 2}],
        [{"markdown": "### Package information"}],
        [{"markdown":"Dimension: ", "width":2}, {"argument": "L", "width": 2}, {"markdown":"x", "width": 0.5}, {"argument": "W", "width": 2}, {"markdown":"x", "width":0.5}, {"argument": "H", "width": 2}],
        [{"argument": "weight", "width": 2}, {"argument": "value", "width": 2}],
        [{"argument": "package"}],
        ],
)
def easypost_demo(
    EASYPOST_API_KEY: str = "",
    from_who: str = "Forrest Bao", 
    from_address_1: str = "2500 Broadway", 
    from_address_2: str = "",
    from_city: str = "Lubbock", 
    from_state: str = "TX", 
    from_zip: str = "79409",
    to_who: str = "Forrest Bao",
    to_address_1: str = "2434 Osborn Drive", 
    to_address_2: str = "",
    to_city: str = "Ames", 
    to_state: str = "IA", 
    to_zip: str = "50014",
    weight: int = 3, 
    L: float=6, W: float=8, H: float=0.4, 
    value: float=5,
    package: typing.Literal["Parcel", "Flat", "Letter"] = "Flat",
)  -> typing.Tuple[funix.hint.HTML, funix.hint.Image ]:
    from_address = {
        "name": from_who,
        "street1": from_address_1,
        "street2": from_address_2,
        "city": from_city,
        "state": from_state,
        "zip": from_zip,
        "country": "USA",
        "phone": ""
    }

    to_address = {
        "name": to_who,
        "street1": to_address_1,
        "street2": to_address_2,
        "city": to_city,
        "state": to_state,
        "zip": to_zip,
        "country": "USA",
        "phone": ""
    }

    parcel = {
        "length": L,
        "width": W,
        "height": H,
        "weight": weight
    }

    if os.getenv("EASYPOST_API_KEY") == None or EASYPOST_API_KEY != "":
        easypost.api_key = EASYPOST_API_KEY

    shipment = easypost.Shipment.create(
        to_address = to_address,
        from_address = from_address,
        parcel = parcel
    )
    shipment.buy(rate=shipment.lowest_rate())

    print (shipment.tracking_code, shipment.postage_label.label_url)

    return f'Tracking number (click to track):\
         <a href="https://tools.usps.com/go/TrackConfirmAction?\
            tLabels={shipment.tracking_code}">{shipment.tracking_code}</a>', \
        shipment.postage_label.label_url