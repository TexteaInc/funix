import { Box } from "@mui/material";
import React from "react";

const InlineBox = (props: { children: React.ReactNode }) => {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        flexWrap: "wrap",
        "*": {
          marginX: 1,
        },
      }}
    >
      {props.children}
    </Box>
  );
};

export default InlineBox;
