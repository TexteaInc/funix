import pandas as pd
from io import BytesIO
from funix import funix, funix_class, funix_method
from funix.hint import BytesFile, HTML
from base64 import b64decode
import json
from typing import Tuple
import os
import geoip2.database
from pandas import DataFrame


geolite_2_country_db = os.getenv("GEOLITE_2_COUNTRY_DB_PATH")
if geolite_2_country_db is None:
    raise Exception("Please set `GEOLITE_2_COUNTRY_DB_PATH` environment variable.")


reader = geoip2.database.Reader(geolite_2_country_db)


@funix(disable=True)
def get_funix_id(cookie: str) -> str | None:
    try:
        split_cookie = cookie.split("; ")
        for item in split_cookie:
            name, value = item.split("=")
            if name.strip() == "session":
                result = value.strip()
                base64_json = result.split(".")[0]
                decoded_json = b64decode(base64_json + "==").decode("utf-8")
                return json.loads(decoded_json)["__funix_id"]
        return None
    except:
        return None


@funix(disable=True)
def create_card(title: str, content: str) -> HTML:
    return f"""<div style='box-shadow: 0 .25rem .5rem 0 rgba(0, 0, 0, 0.2); margin: 0rem .25rem'>
<div style='padding: .125rem 1rem'>
<span style='font-weight: bold; font-size: 1.25rem;'>{title}</span>
<br />
<p>{content}</p>
</div></div>"""


@funix(disable=True)
def create_max_full_flex_box(children: list[HTML]) -> HTML:
    return f"""<div style='display: flex; flex-wrap: wrap; flex-direction: row;'>
{"".join([f"<div style='flex: 1'>{child}</div>" for child in children])}
</div>"""


@funix_class()
class Analytics:
    @funix_method(title="Load log file", print_to_web=True)
    def __init__(self, file: BytesFile):
        """
        Load your Funix log file (only support jsonl format).
        """
        buffer = BytesIO(file)
        self.df = pd.read_json(buffer, lines=True)

        self.requests_count = self.df.shape[0]
        self.funix_ids = set()
        self.functions = set()
        self.functions_times = {}

        self.countries = set()
        self.countries_times = {}

        for request in self.df["request"]:
            if "ip" in request:
                ip = request["ip"]
                try:
                    response = reader.country(ip)
                    country = response.country.name
                except:
                    country = "Unknown"
                self.countries.add(country)
                self.countries_times[country] = self.countries_times.get(country, 0) + 1
            if "function" in request:
                function = request["function"]
                self.functions.add(function)
                self.functions_times[function] = (
                    self.functions_times.get(function, 0) + 1
                )

            if "headers" in request and "Cookie" in request["headers"]:
                cookie = request["headers"]["Cookie"]
                id_ = get_funix_id(cookie)
                if id_ is not None:
                    self.funix_ids.add(id_)
        self.functions_count = len(self.functions)
        self.error_reports = []
        for response in self.df["response"]:
            if isinstance(response, dict) and "error_type" in response:
                self.error_reports.append(response)

        print("File loaded successfully.")

    @funix_method(
        title="Dashboard",
        output_layout=[
            [{"return_index": 0}],
            [{"return_index": 1}, {"return_index": 2}],
        ],
        direction="column",
    )
    def dashboard(self) -> Tuple[HTML, DataFrame, DataFrame]:
        """
        Show the dashboard.
        """
        requests_card = create_card("Requests", f"{self.requests_count} requests")
        functions_card = create_card(
            "Function Calls", f"{self.functions_count} functions"
        )
        error_percent = len(self.error_reports) / self.requests_count * 100
        error_reports_card = create_card(
            "Error", f"{len(self.error_reports)} errors ({error_percent:.2f}%)"
        )
        users_card = create_card("Users", f"{len(self.funix_ids)} users")

        top_functions = sorted(
            self.functions_times.items(), key=lambda x: x[1], reverse=True
        )[:5]

        functions_names = [item[0] for item in top_functions]
        functions_times = [item[1] for item in top_functions]
        functions_data = DataFrame(
            {"Function": functions_names, "Times": functions_times}
        )

        top_countries = sorted(
            self.countries_times.items(), key=lambda x: x[1], reverse=True
        )[:5]

        countries_names = [item[0] for item in top_countries]
        countries_times = [item[1] for item in top_countries]
        countries_data = DataFrame(
            {"Country": countries_names, "Times": countries_times}
        )

        return (
            create_max_full_flex_box(
                [requests_card, functions_card, error_reports_card, users_card]
            ),
            functions_data,
            countries_data,
        )
