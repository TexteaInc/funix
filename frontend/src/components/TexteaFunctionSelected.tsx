import { useStore } from "../store";
import { Typography } from "@mui/material";
import React from "react";
import TexteaFunction from "./TexteaFunction/TexteaFunction";

export const TexteaFunctionSelected: React.FC = () => {
  const selected = useStore((store) => store.selectedFunction);
  if (!selected) {
    return <Typography variant="h5">No selected function</Typography>;
  }
  return <TexteaFunction functionName={selected} />;
};
