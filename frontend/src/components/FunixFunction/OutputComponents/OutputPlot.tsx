import { Box } from "@mui/material";
import { useRef } from "react";

type PlotCode = {
  fig: number | string;
};

export default function OutputPlot(props: {
  plotCode: PlotCode;
  indexId: string;
  backend: URL;
}) {
  const lock = useRef(false);
  return (
    <Box
      component="div"
      sx={{
        width: "100%",
        height: "auto",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
        }}
        id={`plot-${props.indexId}`}
        ref={(ref) => {
          if (ref) {
            if (lock.current) {
              return;
            }
            lock.current = true;
            const websocket =
              (props.backend.protocol === "https:" ? "wss" : "ws") +
              "://" +
              props.backend.host +
              "/ws-plot/" +
              props.plotCode.fig;

            // @ts-expect-error that's good here
            new mpl.figure(
              props.plotCode.fig,
              new WebSocket(websocket),
              (figure: any, format: string) => {
                window.open(
                  new URL(
                    `/plot-download/${props.plotCode.fig}/${format}`,
                    props.backend,
                  ),
                );
              },
              ref,
            );
          }
        }}
      />
    </Box>
  );
}
