import funix 
import matplotlib.pyplot, matplotlib.figure
import numpy 

@funix.funix(
        autorun=True
)
def sine(omega: numpy.arange(0, 1, 0.01)) -> matplotlib.figure.Figure:
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(1, 1, 1)
    x = numpy.linspace(0, 12, 100)
    y = numpy.sin(x*omega)
    ax.plot(x, y)
    return fig