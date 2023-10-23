import React, { useEffect, useState } from "react";
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { FunctionDetail, FunctionPreview, verifyToken } from "../../shared";
import { Alert, AlertTitle, Box, Grid, Stack } from "@mui/material";
import { useAtom } from "jotai";
import { storeAtom } from "../../store";
import InputPanel from "./InputPanel";
import OutputPanel from "./OutputPanel";
import { Token } from "@mui/icons-material";
import InlineBox from "../Common/InlineBox";

export type FunctionDetailProps = {
  preview: FunctionPreview;
  backend: URL;
};

export type FunixFunctionProps = {
  leftSideBarOpen: boolean;
  rightSideBarOpen: boolean;
};

const FunixFunction: React.FC<FunctionDetailProps & FunixFunctionProps> = ({
  preview,
  backend,
  leftSideBarOpen,
  rightSideBarOpen,
}) => {
  const [detail] = useState<FunctionDetail | null>(() => {
    // no asynchronous, no cache
    const xhr = new XMLHttpRequest();
    xhr.open("GET", new URL(`/param/${preview.id}`, backend).toString(), false);
    xhr.send();
    if (xhr.status === 200) {
      return JSON.parse(xhr.responseText) as FunctionDetail;
    } else {
      return null;
    }
  });
  const [
    { inputOutputWidth, functionSecret, backHistory, backConsensus, appSecret },
    setStore,
  ] = useAtom(storeAtom);
  const [width, setWidth] = useState(inputOutputWidth);
  const [onResizing, setOnResizing] = useState(false);
  const [response, setResponse] = useState<string | null>(null);
  const [verified, setVerified] = useState(!preview.secret);

  useEffect(() => {
    if (preview.secret) {
      const token =
        preview.name in functionSecret
          ? functionSecret[preview.path]
          : appSecret !== null
          ? appSecret
          : "";
      verifyToken(new URL(`/verify/${preview.id}`, backend), token || "")
        .then((result) => {
          setVerified(result);
        })
        .catch(() => {
          setVerified(false);
        });
    }
  }, [functionSecret, preview, appSecret]);

  useEffect(() => {
    if (backHistory === null) return;
    if (backHistory.input !== null) {
      if ("__funix_secret" in backHistory.input) {
        setStore((store) => {
          const newFunctionSecret = store.functionSecret;
          newFunctionSecret[backHistory.functionPath] = backHistory.input
            ? backHistory.input["__funix_secret"]
            : null;
          return {
            ...store,
            functionSecret: newFunctionSecret,
          };
        });
      }
    }
    if (backHistory.output !== null) {
      if (typeof backHistory.output === "string") {
        setResponse(backHistory.output);
      } else {
        setResponse(JSON.stringify(backHistory.output));
      }
      setStore((store) => {
        const newBackConsensus = [...store.backConsensus];
        newBackConsensus[1] = true;
        return {
          ...store,
          backConsensus: newBackConsensus,
        };
      });
    }
  }, [backHistory]);

  useEffect(() => {
    if (backConsensus.every((v) => v)) {
      setStore((store) => ({
        ...store,
        backConsensus: [false, false, false],
        backHistory: null,
      }));
    }
  }, [backConsensus]);

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
  const needSecret = preview.secret;

  const handleResize = (event: PointerEvent) => {
    event.preventDefault();
    const newLeftWidth =
      event.clientX /
      (document.body.clientWidth +
        Number(leftSideBarOpen) * 240 -
        Number(rightSideBarOpen) * 240);
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
    <>
      {needSecret ? (
        functionSecret[preview.path] == null && appSecret == null ? (
          <Alert severity="warning">
            <AlertTitle>Secret required</AlertTitle>
            <InlineBox>
              Now you are in preview mode. To use this function, you need to
              provide a secret. You can click <Token /> to set the secret, or
              add <code>?secret=[token]</code> to the URL.
            </InlineBox>
          </Alert>
        ) : !verified ? (
          <Alert severity="error">
            <AlertTitle>Secret incorrect or waiting for verifying</AlertTitle>
            <InlineBox>
              Now you are in preview mode. Your secret is incorrect or waiting
              backend to verify. You can click <Token /> to reset the secret. If
              you don't know the secret, please contact the author.
            </InlineBox>
          </Alert>
        ) : (
          <></>
        )
      ) : (
        <></>
      )}
      <Stack spacing={2}>
        <Grid container direction={detail.direction}>
          <Grid
            item
            sx={
              detail.direction === "row" || detail.direction === "row-reverse"
                ? {
                    width: `calc(${width[0]} - 16px)`,
                  }
                : undefined
            }
          >
            <InputPanel
              detail={detail}
              backend={backend}
              setResponse={setResponse}
              preview={preview}
            />
          </Grid>
          {detail.direction === "row" || detail.direction === "row-reverse" ? (
            <Grid
              item
              sx={{
                width: "1rem",
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
                    document.body.removeEventListener(
                      "pointermove",
                      handleResize
                    );
                  });
                }}
              />
            </Grid>
          ) : (
            <Grid
              item
              sx={{
                height: "1rem",
              }}
            ></Grid>
          )}
          <Grid
            item
            sx={
              detail.direction === "row" || detail.direction === "row-reverse"
                ? {
                    width: `calc(${width[1]})`,
                  }
                : undefined
            }
          >
            <OutputPanel
              detail={detail}
              backend={backend}
              response={response}
            />
          </Grid>
        </Grid>
      </Stack>
    </>
  );
};

export default React.memo(FunixFunction);
