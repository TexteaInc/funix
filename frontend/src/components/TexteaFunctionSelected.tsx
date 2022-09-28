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
  setTheme: (theme: Record<string, any>) => void;
};

const TexteaFunctionSelected: React.FC<FunctionSelectedProps> = ({
  backend,
  setTheme,
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
        setTheme={setTheme}
      />
    </Suspense>
  );
};

export default TexteaFunctionSelected;
