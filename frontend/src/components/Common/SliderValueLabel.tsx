import { SliderValueLabelProps, Tooltip } from "@mui/material";
import React from "react";

export default function SliderValueLabel(props: SliderValueLabelProps) {
  return (
    <Tooltip
      enterTouchDelay={0}
      placement="top"
      title={props.value}
      sx={{ zIndex: 1500 }}
    >
      {props.children}
    </Tooltip>
  );
}
