from typing import List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import pandas 
import pandera, pandera.typing 

import funix
@funix.funix(widgets={"a": "sheet", "b": ["sheet", "slider[0,5,0.2]"]})
def table_plot(
    a: List[int] = [5, 17, 29], b: List[float] = [3.1415, 2.6342, 1.98964]
) -> Figure:
    fig = plt.figure()
    plt.plot(a, b)
    return fig



# Future implementation 

# class MySchema(pandera.DataFrameModel):
#     a: Series[int]
#     b: Series[float]

# def table_plot(df: pandera.typing.DataFrame[MySchema] = \
#                    pandas.DataFrame[{"a": [5, 17, 29], 
#                                      "b": [3.1415, 2.6342, 1.98964]}])\
#             -> Figure:
#     fig = plt.figure()
#     plt.plot(a, b)
#     return fig
