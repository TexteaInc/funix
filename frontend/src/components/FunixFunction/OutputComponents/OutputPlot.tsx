import { useLayoutEffect, useRef } from "react";
import { Box } from "@mui/material";

export default function OutputPlot(props: {
  plotCode: string;
  indexId: string;
}) {
  const drawLock = useRef(false);

  useLayoutEffect(() => {
    if (drawLock.current) {
      return;
    }
    if (document.querySelector(`#plot-${props.indexId}`)?.innerHTML === "") {
      const plot = JSON.parse(props.plotCode);
      // @ts-expect-error: i got mpld3 here
      mpld3.draw_figure(`plot-${props.indexId}`, plot);
      drawLock.current = true;
    }
  }, []);

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
      <div id={`plot-${props.indexId}`} />
    </Box>
  );
}
