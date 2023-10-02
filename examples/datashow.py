import pandas
import pandera
from funix import funix
from matplotlib import pyplot
from matplotlib.figure import Figure


# Data source: 潘绥铭与黄盈盈（2013）。《性之变: 21世纪中国人的性生活》。北京: 中国人民大学出版社。
sexual_repression_data = {
    "age_group": ["18-29", "30-39", "40-49", "50-61"],
    "female": [0.623, 0.754, 0.679, 0.534],
    "male": [0.792, 0.774, 0.755, 0.667],
}


class InputSchema(pandera.DataFrameModel):
    age_group: pandera.typing.Series[str]
    female: pandera.typing.Series[float]
    male: pandera.typing.Series[float]


class OutputSchema(pandera.DataFrameModel):
    age_group: pandera.typing.Series[str]
    average: pandera.typing.Series[float]


def get_mean(array_1: list[float], array_2: list[float]) -> list[float]:
    return [(array_1[i] + array_2[i]) / 2 for i in range(len(array_1))]


@funix()
def input_test(
    data: pandera.typing.DataFrame[InputSchema] = pandas.DataFrame(
        sexual_repression_data
    ),
) -> (Figure, pandas.DataFrame):
    fig = pyplot.figure()
    data_frame = pandas.DataFrame(
        {
            "age_group": data["age_group"],
            "average": get_mean(data["female"], data["male"]),
        }
    )
    pyplot.plot(data["age_group"], data["female"], label="female")
    pyplot.plot(data["age_group"], data["male"], label="male")
    return fig, data_frame
