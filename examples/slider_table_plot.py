from typing import List # Python native 
import matplotlib.pyplot as plt  # the de facto standard for plotting in Python
from matplotlib.figure import Figure # the matplotlib figure class

import funix
@funix.funix(widgets={"a": "sheet", "b": ["sheet", "slider[0,5,0.2]"]})
def table_plot(
    a: List[int] = [5, 17, 29], b: List[float] = [3.1415, 2.6342, 1.98964]
) -> Figure:
    fig = plt.figure()
    plt.plot(a, b)
    return fig


# Future Implementation

# import pandas   # the de facto standard for tabular data in Python
# import pandera  # the typing library for pandas dataframes

# class MySchema(pandera.DataFrameModel):
#     a: pandera.typing.Series[int]
#     b: pandera.typing.Series[float]

# funix.funix()
# def table_plot(df: pandera.typing.DataFrame[MySchema] = \
#                    pandas.DataFrame({"a": [5, 17, 29], 
#                                      "b": [3.1415, 2.6342, 1.98964]})
#                 ) -> Figure:
#     fig = plt.figure()
#     plt.plot(a, b)
#     return fig
