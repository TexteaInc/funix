import funix 
import matplotlib.pyplot, matplotlib.figure
import numpy 

@funix.funix(
        autorun=True, 
)
def sine(omega: funix.hint.FloatSlider(0, 4, 0.1)) -> matplotlib.figure.Figure:
    fig = matplotlib.pyplot.figure()
    x = numpy.linspace(0, 20, 200)
    y = numpy.sin(x*omega)
    matplotlib.pyplot.plot(x, y, linewidth=5)
    return fig