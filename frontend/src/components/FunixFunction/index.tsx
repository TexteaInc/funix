import React, { useEffect, useState } from "react";
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { FunctionDetail, FunctionPreview } from "../../shared";
import useSWR from "swr";
import { Box, Grid, Stack } from "@mui/material";
import { useAtom } from "jotai";
import { storeAtom } from "../../store";
import InputPanel from "./InputPanel";
import OutputPanel from "./OutputPanel";

export type FunctionDetailProps = {
  preview: FunctionPreview;
  backend: URL;
};

const FunixFunction: React.FC<FunctionDetailProps> = ({ preview, backend }) => {
  const { data: detail } = useSWR<FunctionDetail>(
    new URL(`/param/${preview.path}`, backend).toString()
  );
  const [{ inputOutputWidth, sideBarOpen }, setStore] = useAtom(storeAtom);
  const [width, setWidth] = useState(inputOutputWidth);
  const [onResizing, setOnResizing] = useState(false);
  const [response, setResponse] = useState<string | null>(null);
  useEffect(() => {
    setStore((store) => ({
      ...store,
      inputOutputWidth: width,
    }));
  }, [onResizing]);

  if (detail == null) {
    console.log("Failed to display function detail");
    return <div />;
  } else {
    useEffect(() => {
      setStore((store) => ({
        ...store,
        theme: functionDetail.theme,
      }));
    }, []);
  }

  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const functionDetail = detail!;

  const handleResize = (event: PointerEvent) => {
    event.preventDefault();
    const newLeftWidth = sideBarOpen
      ? event.clientX / (document.body.clientWidth + 240)
      : event.clientX / document.body.clientWidth;
    const newRightWidth = 1 - newLeftWidth;
    setWidth([
      `${(newLeftWidth * 100).toFixed(3)}%`,
      `${(newRightWidth * 100).toFixed(3)}%`,
    ]);
  };

  const resetWidth = () => {
    setWidth(["50%", "50%"]);
    setStore((store) => ({
      ...store,
      inputOutputWidth: ["50%", "50%"],
    }));
  };

  return (
    <Stack spacing={2}>
      <Grid container>
        <Grid
          item
          sx={{
            width: `calc(${width[0]} - 16px)`,
          }}
        >
          <InputPanel
            detail={detail}
            backend={backend}
            setResponse={setResponse}
          />
        </Grid>
        <Grid
          item
          sx={{
            width: "16px",
          }}
        >
          <Box
            id="resize-line"
            sx={{
              height: "100%",
              width: "65%",
              margin: "0 auto",
              backgroundColor: `${onResizing ? "grey.100" : ""}`,
              "&:hover": {
                backgroundColor: "grey.100",
                cursor: "col-resize",
              },
            }}
            onContextMenu={(event) => {
              event.preventDefault();
              resetWidth();
            }}
            onPointerDown={(event) => {
              event.preventDefault();
              setOnResizing(true);
              document.body.style.cursor = "col-resize";
              document.body.addEventListener("pointermove", handleResize);
              document.body.addEventListener("pointerup", () => {
                document.body.style.cursor = "default";
                setOnResizing(false);
                document.body.removeEventListener("pointermove", handleResize);
              });
            }}
          />
        </Grid>
        <Grid
          item
          sx={{
            width: `calc(${width[1]})`,
          }}
        >
          <OutputPanel detail={detail} backend={backend} response={response} />
        </Grid>
      </Grid>
    </Stack>
  );
};

export default React.memo(FunixFunction);
