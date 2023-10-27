from typing import List # Python native 

import matplotlib.figure, matplotlib.pyplot# the de facto standard for plotting in Python

import funix

# @funix.funix(widgets={"a": "sheet", "b": ["sheet", "slider[0,5,0.2]"]})
# def table_plot(
#     a: List[int] = [5, 17, 29], b: List[float] = [3.1415, 2.6342, 1.98964]
# ) -> Figure:
#     fig = matplotlib.pyplot.figure()
#     matplotlib.pyplot.plot(a, b)
#     return fig


# New Implementation after FEP 11

import pandas   # the de facto standard for tabular data in Python
import pandera  # the typing library for pandas dataframes

class InputSchema(pandera.DataFrameModel):
    a: pandera.typing.Series[int]
    b: pandera.typing.Series[float]

@funix.funix()
def table_and_plot(df: pandera.typing.DataFrame[InputSchema] = \
                   pandas.DataFrame({"a": [5, 17, 29], # default values
                                     "b": [3.1415, 2.6342, 1.98964]})
                ) -> (matplotlib.figure.Figure, pandas.DataFrame):
    fig = matplotlib.pyplot.figure()
    matplotlib.pyplot.plot(df["a"], df["b"])

    output_data_frame = pandas.DataFrame(
        {
            "a-b": df["a"] - df["b"],
            "a+b": df["a"] + df["b"]
        }
    )

    return fig, output_data_frame

    # FIXME: There is a column called ID in the output. Please remove it. 
