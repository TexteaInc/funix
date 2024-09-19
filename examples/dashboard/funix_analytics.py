import pandas as pd
from io import BytesIO
from funix import funix, funix_class, funix_method
from funix.hint import BytesFile, HTML
from base64 import b64decode
import json
from typing import Tuple
import os
import geoip2.database
from datetime import datetime, timedelta
from pandas import DataFrame
from funix.session import get_global_variable


geolite_2_country_db = os.getenv("GEOLITE_2_COUNTRY_DB_PATH")
if geolite_2_country_db is None:
    raise Exception("Please set `GEOLITE_2_COUNTRY_DB_PATH` environment variable.")


reader = geoip2.database.Reader(geolite_2_country_db)


@funix(disable=True)
def get_all_functions() -> list[str]:
    class_instance = get_global_variable("__FUNIX_Analytics")
    if class_instance is None:
        return []
    return list(class_instance.functions)


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


@funix(disable=True)
def handle_json_line(file: BytesIO) -> pd.DataFrame:
    first_read = pd.read_json(file, lines=True)
    result_dataframe = pd.DataFrame(
        columns=[
            "time",
            "response",
            "ip",
            "url",
            "headers",
            "request",
            "function",
            "file",
        ]
    )
    for i in range(first_read.shape[0]):
        row = first_read.iloc[i]
        result_dataframe.loc[i] = [
            datetime.fromisoformat(row["time"]),
            row["response"],
            row["request"]["ip"],
            row["request"]["url"],
            row["request"]["headers"],
            row["request"]["data"],
            row["request"].get("function", None),
            row["request"].get("file", None),
        ]

    return result_dataframe


@funix_class()
class Analytics:
    @funix_method(title="Load log file", print_to_web=True)
    def __init__(self, file: BytesFile):
        """
        Load your Funix log file (only support jsonl format).
        """
        buffer = BytesIO(file)
        self.df = handle_json_line(buffer)

        self.requests_count = self.df.shape[0]
        self.funix_ids = set()
        self.functions = set()
        self.functions_times = {}

        self.countries = set()
        self.countries_times = {}
        self.error_reports = []

        for _, single_item in self.df.iterrows():
            if "ip" in single_item:
                ip = single_item["ip"]
                try:
                    response = reader.country(ip)
                    country = response.country.name
                except:
                    country = "Unknown"
                self.countries.add(country)
                self.countries_times[country] = self.countries_times.get(country, 0) + 1

            if "function" in single_item and single_item["function"] is not None:
                function = single_item["function"]
                self.functions.add(function)
                self.functions_times[function] = (
                    self.functions_times.get(function, 0) + 1
                )

            if "headers" in single_item and "Cookie" in single_item["headers"]:
                cookie = single_item["headers"]["Cookie"]
                id_ = get_funix_id(cookie)
                if id_ is not None:
                    self.funix_ids.add(id_)

            if (
                "response" in single_item
                and isinstance(single_item["response"], dict)
                and "error_type" in single_item["response"]
            ):
                self.error_reports.append(single_item["response"])

        self.functions_count = len(self.functions)

        print("File loaded successfully.")

    @funix_method(
        title="Dashboard",
        output_layout=[
            [{"return_index": 0}],
            [{"return_index": 1}, {"return_index": 2}],
        ],
        direction="column",
        just_run=True,
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

    @funix_method(disable=True)
    def get_functions_call_details(self, function_name: str, time: datetime) -> list:
        result = []
        for index, row in self.df.iterrows():
            if row["function"] == function_name and row["time"] >= time.replace(
                tzinfo=row["time"].tzinfo
            ):
                result.append(row)
        return result

    @funix_method(
        title="Analyse Function",
        whitelist={
            "time": ["Day", "Week", "Month", "Year"],
        },
    )
    def anal_one_function(
        self, function_name: str, time: str
    ) -> Tuple[HTML, DataFrame]:
        if function_name not in self.functions:
            return create_card("No data", "No data found."), DataFrame()
        time_diff = None
        if time == "Day":
            time_diff = 1
        elif time == "Week":
            time_diff = 7
        elif time == "Month":
            time_diff = 30
        elif time == "Year":
            time_diff = 365

        time_diff = datetime.now() - timedelta(days=time_diff)
        call_details = self.get_functions_call_details(function_name, time_diff)

        if len(call_details) == 0:
            return create_card("No data", "No data found."), DataFrame()

        function_full_call_times = self.df.loc[
            self.df["function"] == function_name
        ].shape[0]
        function_call_times = len(call_details)

        function_call_percent = function_call_times / function_full_call_times * 100

        function_call_card = create_card(
            "Function Call",
            f"{function_call_times} times ({function_call_percent:.2f}%)",
        )

        countries = {}

        for item in call_details:
            ip = item["ip"]
            try:
                response = reader.country(ip)
                country = response.country.name
            except:
                country = "Unknown"
            countries[country] = countries.get(country, 0) + 1

        countries_dataframe = DataFrame(
            {"Country": list(countries.keys()), "Times": list(countries.values())}
        )

        return function_call_card, countries_dataframe
