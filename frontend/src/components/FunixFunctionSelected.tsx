import { storeAtom } from "../store";
import {
  Alert,
  Card,
  CardContent,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";
import React, { Suspense, useState } from "react";
import { useAtom } from "jotai";
import FunixFunction from "./FunixFunction";
import { useLocation } from "react-router-dom";

export type FunctionSelectedProps = {
  backend: URL;
  leftSideBarOpen: boolean;
  rightSideBarOpen: boolean;
};

const FunixFunctionSelected: React.FC<FunctionSelectedProps> = ({
  backend,
  leftSideBarOpen,
  rightSideBarOpen,
}) => {
  const [{ selectedFunction }] = useAtom(storeAtom);
  const { pathname } = useLocation();
  const pathParams = useState(
    pathname.split("/").filter((value) => value !== "")
  );

  if (pathParams[0].length !== 0 && !selectedFunction) {
    return <Alert severity="warning">Your function is not found.</Alert>;
  }

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
      <FunixFunction
        preview={selectedFunction}
        key={selectedFunction.path}
        backend={backend}
        leftSideBarOpen={leftSideBarOpen}
        rightSideBarOpen={rightSideBarOpen}
      />
    </Suspense>
  );
};

export default React.memo(FunixFunctionSelected);
