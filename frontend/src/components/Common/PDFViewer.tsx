import React from "react";
import { Grid } from "@mui/material";
const PDFViewer = (props: { pdf: string | File }) => {
  const data =
    typeof props.pdf === "string" ? props.pdf : URL.createObjectURL(props.pdf);

  return (
    <>
      <Grid
        container
        direction="row"
        justifyContent="center"
        alignItems="center"
        sx={{
          width: "100%",
          height: "100%",
          overflow: "auto",
        }}
      >
        <object
          data={data}
          type="application/pdf"
          style={{
            width: "100%",
            height: "100%",
          }}
        />
      </Grid>
    </>
  );
};

export default PDFViewer;
