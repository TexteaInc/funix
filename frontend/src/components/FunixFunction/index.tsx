import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  callFunctionRaw,
  FunctionDetail,
  FunctionPreview,
  verifyToken,
} from "../../shared";
import { Alert, AlertTitle, Box, Grid, Stack } from "@mui/material";
import { useAtom } from "jotai";
import InputPanel from "./InputPanel";
import OutputPanel from "./OutputPanel";
import { Token } from "@mui/icons-material";
import InlineBox from "../Common/InlineBox";
import _ from "lodash";
import {
  appSecretAtom,
  backConsensusAtom,
  backHistoryAtom,
  callableDefaultAtom,
  functionSecretAtom,
  lastAtom,
  showFunctionTitleAtom,
  themeAtom,
} from "../../store";
// import useSWR from "swr";

export type FunctionDetailProps = {
  preview: FunctionPreview;
  backend: URL;
};

const FunixFunction: React.FC<FunctionDetailProps> = ({ preview, backend }) => {
  // const { data: detail } = useSWR<FunctionDetail>(
  //   new URL(`/param/${preview.id}`, backend).toString()
  // );
  const [detail, setDetail] = useState<FunctionDetail | null>(null);

  const [functionSecret, setFunctionSecret] = useAtom(functionSecretAtom);
  const [backHistory, setBackHistory] = useAtom(backHistoryAtom);
  const [backConsensus, setBackConsensus] = useAtom(backConsensusAtom);
  const [appSecret] = useAtom(appSecretAtom);
  const [last] = useAtom(lastAtom);
  const [callableDefault, setCallableDefault] = useAtom(callableDefaultAtom);
  const [, setShowFunctionTitle] = useAtom(showFunctionTitleAtom);
  const [, setTheme] = useAtom(themeAtom);

  const [width, setWidth] = useState(preview.width);
  const [onResizing, setOnResizing] = useState(false);
  const [response, setResponseState] = useState<string | null>(null);
  const [verified, setVerified] = useState(!preview.secret);
  const queryLock = useRef(false);
  const [warning, setWarning] = useState(false);
  const [outdated, setOutdatedState] = useState(false);

  const setResponse = useCallback(
    (value: React.SetStateAction<string | null>) => {
      setResponseState(value);
    },
    [],
  );

  const setOutdated = useCallback((value: React.SetStateAction<boolean>) => {
    setOutdatedState(value);
  }, []);

  useEffect(() => {
    if (preview.secret) {
      const token =
        preview.path in functionSecret
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
    const timer = setTimeout(() => {
      if (detail === null) {
        setWarning(true);
      }
    }, 5000);
    return () => clearTimeout(timer);
  }, [detail]);

  useEffect(() => {
    if (backHistory === null) return;
    setOutdatedState(true);
    if (backHistory.input !== null) {
      if ("__funix_secret" in backHistory.input) {
        const newFunctionSecret = { ...functionSecret };
        newFunctionSecret[backHistory.functionPath] = backHistory.input
          ? backHistory.input["__funix_secret"]
          : null;
        setFunctionSecret(newFunctionSecret);
      }
    }
    if (backHistory.output !== null) {
      if (typeof backHistory.output === "string") {
        setResponseState(backHistory.output);
      } else {
        setResponseState(JSON.stringify(backHistory.output));
      }
      const newBackConsensus = [...backConsensus];
      newBackConsensus[1] = true;
      setBackConsensus(newBackConsensus);
    }
  }, [backHistory]);

  useEffect(() => {
    if (backConsensus.every((v) => v)) {
      setBackConsensus([false, false, false]);
      setBackHistory(null);
    }
  }, [backConsensus]);

  useEffect(() => {
    if (detail == null) return;
    setShowFunctionTitle(
      detail.theme !== null
        ? "funix_disable_input_title" in detail.theme
          ? !detail.theme.funix_disable_input_title
          : false
        : false,
    );
    setTheme(detail.theme);
  }, [detail]);

  useEffect(() => {
    if (queryLock.current) {
      return;
    }
    queryLock.current = true;
    fetch(new URL(`/param/${preview.id}`, backend).toString(), {
      credentials: "include",
    })
      .then((body) => {
        return body.json();
      })
      .then((data: FunctionDetail) => {
        setDetail(data);
        setWarning(false);
      })
      .then(() => {
        if (preview.keepLast && preview.id in last) {
          setResponseState(JSON.stringify(last[preview.id].output));
        }
      })
      .then(() => {
        if (preview.justRun) {
          // simple run
          let defaultConfig = {};
          if (callableDefault !== null && preview.path in callableDefault) {
            defaultConfig = callableDefault[preview.path];
            const newCallableDefault = { ...callableDefault };
            delete newCallableDefault[preview.path];
            setCallableDefault(newCallableDefault);
          }
          callFunctionRaw(
            new URL(`/call/${preview.id}`, backend),
            defaultConfig,
          ).then((rsp) => {
            setResponseState(rsp.toString());
          });
        }
      });
  }, [preview, backend, last]);

  const needSecret = preview.secret;

  const handleResize = (event: PointerEvent) => {
    const mainWidth = document.getElementById("funix-stack")?.offsetWidth || 1;
    const mainLeftOffset =
      document.getElementById("funix-stack")?.offsetLeft || 1;
    const newLeftWidth = (event.pageX - mainLeftOffset) / mainWidth;

    const newRightWidth = 1 - newLeftWidth;
    setWidth([
      `${(newLeftWidth * 100).toFixed(3)}%`,
      `${(newRightWidth * 100).toFixed(3)}%`,
    ]);
  };

  return detail !== null ? (
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
      {outdated && (
        <Alert severity="info">
          <AlertTitle>Outdated</AlertTitle>
          <InlineBox>You are viewing data from the history.</InlineBox>
        </Alert>
      )}
      {preview.justRun ? (
        <Stack spacing={2}>
          <Grid item>
            <OutputPanel
              detail={detail}
              backend={backend}
              response={response}
            />
          </Grid>
        </Stack>
      ) : (
        <Stack spacing={2}>
          <Grid container direction={detail.direction} wrap="nowrap">
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
                setOutdated={setOutdated}
                preview={preview}
              />
            </Grid>
            {detail.direction === "row" ||
            detail.direction === "row-reverse" ? (
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
                    backgroundColor: (theme) =>
                      `${
                        theme.palette.mode === "dark" &&
                        onResizing &&
                        "grey.900"
                      }`,
                    "&:hover": {
                      backgroundColor: (theme) =>
                        `${
                          theme.palette.mode === "dark"
                            ? "grey.900"
                            : "grey.100"
                        }`,
                      cursor: "ew-resize",
                    },
                  }}
                  onContextMenu={(event) => {
                    event.preventDefault();
                  }}
                  onPointerDown={(event) => {
                    event.preventDefault();
                    setOnResizing(true);
                    document.body.style.cursor = "col-resize";
                    document.body.addEventListener(
                      "pointermove",
                      handleResize,
                      true,
                    );
                    document.body.addEventListener("pointerup", () => {
                      document.body.style.cursor = "default";
                      setOnResizing(false);
                      document.body.removeEventListener(
                        "pointermove",
                        handleResize,
                        true,
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
      )}
    </>
  ) : warning ? (
    <Alert severity="warning">
      <AlertTitle>Waiting for detail</AlertTitle>
      <InlineBox>
        If this message lasts for a long time, please check your network or the
        backend status.
      </InlineBox>
    </Alert>
  ) : (
    <></>
  );
};

export default React.memo(FunixFunction, (prevProps, nextProps) => {
  return (
    _.isEqual(prevProps.backend, nextProps.backend) &&
    _.isEqual(prevProps.preview, nextProps.preview)
  );
});
