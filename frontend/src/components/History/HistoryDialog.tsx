import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  AppBar,
  Button,
  Card,
  CardActions,
  CardContent,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  TextField,
  Toolbar,
  Typography,
} from "@mui/material";
import useFunixHistory, { History } from "../../shared/useFunixHistory";
import {
  ArrowDownward,
  ArrowUpward,
  Close,
  Delete,
  Edit,
  ExpandMore,
  FileDownload,
  Preview,
} from "@mui/icons-material";
import React, { useEffect } from "react";
import {
  Timeline,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineItem,
  TimelineOppositeContent,
  timelineOppositeContentClasses,
  TimelineSeparator,
} from "@mui/lab";
import { exportHistories, exportHistory, PostCallResponse } from "../../shared";
import { useAtom } from "jotai";
import { storeAtom } from "../../store";
import {
  FunixHistoryStepper,
  getHistoryInfo,
  getHistoryStatusColor,
  getHistoryStatusIcon,
  HistoryEnum,
} from "./HistoryUtils";
import ThemeReactJson from "../Common/ThemeReactJson";

// const rewindHistory = async (
//   histories: History[],
//   functions: null | string[],
//   history: History,
//   backend: null | URL
// ) => {
//   if (backend === null) {
//     await Promise.reject("Backend is not set");
//     return;
//   }
//   const index = histories.findIndex((h) => h.timestamp === history.timestamp);
//   // Get [0, index)
//   const newHistories = histories.slice(0, index);
//   const availableHistories = newHistories.filter((h) =>
//     functions?.includes(h.functionName)
//   );
//   return availableHistories.map(async (h) => {
//     if (h.input !== null) {
//       return await callFunctionRaw(
//         new URL(`/call/${h.functionName}`, backend),
//         h.input
//       );
//     }
//     return Promise.resolve();
//   });
// };

const TryJson = (props: {
  src: string | PostCallResponse;
  collapsed: boolean;
}) => {
  if (typeof props.src === "string") {
    try {
      const parsed = JSON.parse(props.src);
      return <ThemeReactJson src={parsed} collapsed={props.collapsed} />;
    } catch {
      return <code>{props.src}</code>;
    }
  }
  return <ThemeReactJson src={props.src} collapsed={props.collapsed} />;
};

type InputAndOutput = "input" | "output";

const HistoryDialog = (props: {
  open: boolean;
  setOpen: (open: boolean) => void;
}) => {
  const { getHistories, clearHistory, removeHistory, setHistoryNameAndPath } =
    useFunixHistory();
  const [{ functions }, setStore] = useAtom(storeAtom);
  const [isAscending, setAscending] = React.useState(true);
  const [clearDialogOpen, setClearDialogOpen] = React.useState(false);
  const [selectedHistory, setSelectedHistory] = React.useState<History | null>(
    null
  );
  const [renameDialogOpen, setRenameDialogOpen] = React.useState(false);
  const [tempRename, setTempRename] = React.useState("");
  const [singleCollapsedMap, setSingleCollapsedMap] = React.useState<
    Record<string, Record<InputAndOutput, boolean>>
  >({});
  // const [backdropOpen, setBackdropOpen] = React.useState(false);
  // const [rewindSnackbarOpen, setRewindSnackbarOpen] = React.useState(false);

  const backHistory = (history: History) => {
    setStore((store) => ({
      ...store,
      backHistory: history,
    }));
    props.setOpen(false);
  };

  const getSingleCollapsed = (uuid: string, type: InputAndOutput) => {
    if (uuid in singleCollapsedMap) {
      return singleCollapsedMap[uuid][type];
    }
    return false;
  };

  // const rewindOver = (history: History) => {
  //   setBackdropOpen(false);
  //   setRewindSnackbarOpen(true);
  //   backHistory(history);
  // };

  const [histories, setHistories] = React.useState<History[]>([]);

  useEffect(() => {
    getHistories().then((h) => setHistories(h));
  }, []);

  window.addEventListener("funix-history-update", () => {
    getHistories().then((h) => setHistories(h));
  });

  return (
    <>
      {/*<Snackbar*/}
      {/*  open={rewindSnackbarOpen}*/}
      {/*  autoHideDuration={3000}*/}
      {/*  onClose={(event, reason) => {*/}
      {/*    if (reason !== "clickaway") {*/}
      {/*      setRewindSnackbarOpen(false);*/}
      {/*    }*/}
      {/*  }}*/}
      {/*  sx={{*/}
      {/*    zIndex: 3050,*/}
      {/*  }}*/}
      {/*  message="Rewind done!"*/}
      {/*/>*/}
      {/*<Backdrop*/}
      {/*  sx={{*/}
      {/*    color: "#ffffff",*/}
      {/*    zIndex: 3100,*/}
      {/*  }}*/}
      {/*  open={backdropOpen}*/}
      {/*>*/}
      {/*  <CircularProgress color="inherit" />*/}
      {/*</Backdrop>*/}
      <Dialog
        open={renameDialogOpen}
        onClose={() => {
          setRenameDialogOpen(false);
          setSelectedHistory(null);
        }}
        sx={{
          zIndex: 3000,
        }}
      >
        <DialogTitle>Rename History</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            label="Name"
            fullWidth
            variant="standard"
            value={tempRename}
            onChange={(e) => {
              if (selectedHistory !== null) {
                setTempRename(e.target.value);
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setRenameDialogOpen(false);
              setSelectedHistory(null);
              setTempRename("");
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              if (selectedHistory !== null) {
                setHistoryNameAndPath(
                  selectedHistory.timestamp,
                  tempRename,
                  selectedHistory.functionPath
                );
              }
              setRenameDialogOpen(false);
              setSelectedHistory(null);
              setTempRename("");
            }}
          >
            Rename
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog
        open={clearDialogOpen}
        onClose={() => setClearDialogOpen(false)}
        sx={{
          zIndex: 3000,
        }}
      >
        <DialogTitle>Clear all history</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This action cannot be undone. All history will be deleted. If you
            want to save your histories before, you can use export function to
            download them as a JSON file.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              getHistories().then((histories) => {
                exportHistories(histories);
              });
            }}
          >
            Export All
          </Button>
          <Button onClick={() => setClearDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={() => {
              clearHistory();
              setClearDialogOpen(false);
            }}
            color="error"
          >
            Clear
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog
        open={props.open}
        onClose={() => props.setOpen(false)}
        fullScreen
        sx={{
          zIndex: 2500,
        }}
      >
        <AppBar sx={{ position: "relative" }}>
          <Toolbar>
            <IconButton
              edge="start"
              color="inherit"
              onClick={() => props.setOpen(false)}
              aria-label="close"
            >
              <Close />
            </IconButton>
            <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
              History
            </Typography>
            {histories.length !== 0 && (
              <>
                <IconButton
                  edge="end"
                  color="inherit"
                  onClick={() => setClearDialogOpen(true)}
                  size="large"
                >
                  <Delete />
                </IconButton>
                <IconButton
                  edge="end"
                  color="inherit"
                  onClick={() => exportHistories(histories)}
                  size="large"
                >
                  <FileDownload />
                </IconButton>
                <IconButton
                  edge="end"
                  color="inherit"
                  onClick={() => setAscending((prevState) => !prevState)}
                  size="large"
                >
                  {isAscending ? <ArrowDownward /> : <ArrowUpward />}
                </IconButton>
              </>
            )}
          </Toolbar>
        </AppBar>
        <Container
          sx={{
            paddingTop: 2,
          }}
          maxWidth="lg"
        >
          {histories.length === 0 ? (
            <Alert severity="info">No history, try to run some functions</Alert>
          ) : (
            <Timeline
              position="right"
              sx={{
                [`& .${timelineOppositeContentClasses.root}`]: {
                  flex: 0.2,
                },
                width: "100%",
              }}
            >
              {histories
                .sort((a, b) => {
                  return isAscending
                    ? a.timestamp - b.timestamp
                    : b.timestamp - a.timestamp;
                })
                .map((history, index) => {
                  const { status, hasSecret } = getHistoryInfo(history);
                  const disabled =
                    functions === null ||
                    !functions?.includes(history.functionName);
                  // setSingleCollapsedMap((prevState) => {
                  //   return {
                  //     ...prevState,
                  //     [history.uuid]: {
                  //       input: false,
                  //       output: false,
                  //     },
                  //   };
                  // });
                  return (
                    <TimelineItem key={index}>
                      <TimelineOppositeContent
                        sx={{ m: "auto 0" }}
                        variant="body2"
                        color="text.secondary"
                      >
                        {new Date(history.timestamp).toLocaleString()}
                      </TimelineOppositeContent>
                      <TimelineSeparator>
                        <TimelineConnector />
                        <TimelineDot color={getHistoryStatusColor(status)}>
                          {getHistoryStatusIcon(status)}
                        </TimelineDot>
                        <TimelineConnector />
                      </TimelineSeparator>
                      <TimelineContent
                        sx={{ py: "12px", px: 2, width: "80%", flex: "auto" }}
                      >
                        <Card>
                          <CardContent>
                            <Typography
                              variant="h5"
                              component="div"
                              gutterBottom
                            >
                              {history.name || "Untitled"}
                            </Typography>
                            <Typography
                              variant="body2"
                              component="div"
                              color="text.secondary"
                              gutterBottom
                            >
                              Function: {history.functionName}
                            </Typography>
                            {hasSecret && (
                              <Typography
                                variant="body2"
                                component="div"
                                color="text.secondary"
                                gutterBottom
                              >
                                This function has secret key, please be careful
                                when sharing this history or input information.
                              </Typography>
                            )}
                            {disabled && (
                              <Typography
                                variant="body2"
                                component="div"
                                color="text.secondary"
                                gutterBottom
                              >
                                This function cannot be found in the current
                                backend server, change the backend server to the
                                one that contains this function to use view.
                              </Typography>
                            )}
                            <FunixHistoryStepper status={status} />
                            <Accordion
                              disabled={history.input === null}
                              expanded={
                                history.input !== null &&
                                getSingleCollapsed(history.uuid, "input")
                              }
                              onChange={(event, expanded) => {
                                setSingleCollapsedMap((prevState) => {
                                  return {
                                    ...prevState,
                                    [history.uuid]: {
                                      ...prevState[history.uuid],
                                      input: expanded,
                                    },
                                  };
                                });
                              }}
                            >
                              <AccordionSummary expandIcon={<ExpandMore />}>
                                <Typography>Input</Typography>
                              </AccordionSummary>
                              <AccordionDetails
                                sx={{
                                  maxWidth: "100%",
                                  overflow: "auto",
                                  maxHeight: "50vh",
                                }}
                              >
                                {history.input !== null ? (
                                  <ThemeReactJson
                                    src={history.input}
                                    collapsed={true}
                                  />
                                ) : (
                                  <Typography>No input</Typography>
                                )}
                              </AccordionDetails>
                            </Accordion>
                            <Accordion
                              disabled={history.output === null}
                              expanded={
                                history.output !== null &&
                                getSingleCollapsed(history.uuid, "output")
                              }
                              onChange={(event, expanded) => {
                                setSingleCollapsedMap((prevState) => {
                                  return {
                                    ...prevState,
                                    [history.uuid]: {
                                      ...prevState[history.uuid],
                                      output: expanded,
                                    },
                                  };
                                });
                              }}
                            >
                              <AccordionSummary expandIcon={<ExpandMore />}>
                                <Typography
                                  sx={{
                                    width: "33%",
                                    flexShrink: 0,
                                  }}
                                >
                                  Output
                                </Typography>
                                {status === HistoryEnum.Error && (
                                  <Typography sx={{ color: "text.secondary" }}>
                                    Backend server reports an error
                                  </Typography>
                                )}
                              </AccordionSummary>
                              <AccordionDetails
                                sx={{
                                  maxWidth: "100%",
                                  overflow: "auto",
                                  maxHeight: "50vh",
                                }}
                              >
                                {history.output !== null ? (
                                  <TryJson
                                    src={history.output}
                                    collapsed={true}
                                  />
                                ) : (
                                  <Typography>No output</Typography>
                                )}
                              </AccordionDetails>
                            </Accordion>
                          </CardContent>
                          <CardActions>
                            <Button
                              size="small"
                              color="primary"
                              startIcon={<Preview />}
                              disabled={disabled}
                              onClick={() => backHistory(history)}
                            >
                              View
                            </Button>
                            <Button
                              size="small"
                              color="primary"
                              startIcon={<Edit />}
                              disabled={disabled}
                              onClick={() => {
                                setTempRename(history.name || "");
                                setSelectedHistory(history);
                                setRenameDialogOpen(true);
                              }}
                            >
                              Rename
                            </Button>
                            {/*<Button*/}
                            {/*  size="small"*/}
                            {/*  color="primary"*/}
                            {/*  startIcon={<FastRewind />}*/}
                            {/*  disabled={disabled}*/}
                            {/*  onClick={async () => {*/}
                            {/*    setBackdropOpen(true);*/}
                            {/*    await rewindHistory(*/}
                            {/*      histories,*/}
                            {/*      functions,*/}
                            {/*      history,*/}
                            {/*      backend*/}
                            {/*    )*/}
                            {/*      .then(() => {*/}
                            {/*        rewindOver(history);*/}
                            {/*      })*/}
                            {/*      .catch((e) => {*/}
                            {/*        console.error(e);*/}
                            {/*        rewindOver(history);*/}
                            {/*      });*/}
                            {/*  }}*/}
                            {/*>*/}
                            {/*  Rewind*/}
                            {/*</Button>*/}
                            <Button
                              size="small"
                              color="primary"
                              startIcon={<FileDownload />}
                              onClick={() => exportHistory(history)}
                            >
                              Export
                            </Button>
                            <Button
                              size="small"
                              color="error"
                              startIcon={<Delete />}
                              onClick={() => removeHistory(history.uuid)}
                            >
                              Delete
                            </Button>
                          </CardActions>
                        </Card>
                      </TimelineContent>
                    </TimelineItem>
                  );
                })}
            </Timeline>
          )}
        </Container>
      </Dialog>
    </>
  );
};

export default React.memo(HistoryDialog, (prevProps, nextProps) => {
  return (
    prevProps.open === nextProps.open && prevProps.setOpen === nextProps.setOpen
  );
});
