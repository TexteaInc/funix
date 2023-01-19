import { useLayoutEffect } from "react";

export default function OutputPlot(props: {
  plotCode: string;
  indexId: string;
}) {
  useLayoutEffect(() => {
    if (document.querySelector(`#plot-${props.indexId}`)?.innerHTML === "") {
      const scriptElement = document.createElement("script");
      scriptElement.innerHTML = `mpld3.draw_figure("plot-${props.indexId}", ${props.plotCode})`;
      document.body.appendChild(scriptElement);
    }
  }, []);

  return <div id={`plot-${props.indexId}`} />;
}
