import { storeAtom } from "../store";
import { Typography } from "@mui/material";
import React, { Suspense } from "react";
import { TexteaFunction } from "./TexteaFunction";
import { useAtom } from "jotai";

export const TexteaFunctionSelected: React.FC = () => {
  const [{ selectedFunction }] = useAtom(storeAtom);
  if (!selectedFunction) {
    return <Typography variant="h5">No selected function</Typography>;
  }
  return (
    <Suspense fallback="loading function detail">
      <TexteaFunction preview={selectedFunction} />
    </Suspense>
  );
};
