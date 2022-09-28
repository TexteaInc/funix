import { storeAtom } from "../store";
import {
  Alert,
  Card,
  CardContent,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";
import React, { Suspense } from "react";
import { useAtom } from "jotai";
import TexteaFunction from "./TexteaFunction";

export type FunctionSelectedProps = {
  backend: URL;
};

const TexteaFunctionSelected: React.FC<FunctionSelectedProps> = ({
  backend,
}) => {
  const [{ selectedFunction }] = useAtom(storeAtom);
  if (!selectedFunction) {
    return <Alert severity="info">Select a function to start</Alert>;
  }
  const suspenseFallback = (
    <Card>
      <CardContent>
        <Stack direction="row" alignItems="center" spacing={2}>
          <CircularProgress />
          <Typography>Loading selected function …</Typography>
        </Stack>
      </CardContent>
    </Card>
  );
  return (
    <Suspense fallback={suspenseFallback}>
      <TexteaFunction
        preview={selectedFunction}
        key={selectedFunction.path}
        backend={backend}
      />
    </Suspense>
  );
};

export default TexteaFunctionSelected;
