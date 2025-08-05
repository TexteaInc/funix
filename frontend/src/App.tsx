import {
  Alert,
  AlertTitle,
  Box,
  Button,
  Container,
  createTheme,
  CssBaseline,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Drawer,
  FormControlLabel,
  FormGroup,
  IconButton,
  InputAdornment,
  Link,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stack,
  styled,
  Switch,
  TextField,
  ThemeProvider,
  Toolbar,
  Typography,
} from "@mui/material";
import FunixFunctionList from "./components/FunixFunctionList";
import FunixFunctionSelected from "./components/FunixFunctionSelected";
import FunixTabBar from "./components/FunixTabBar";
import { useNavigate } from "react-router-dom";
import {
  ArrowBack,
  ArrowForward,
  Code,
  ContentCopy,
  EventNote,
  Functions,
  GitHub,
  History,
  Settings,
  Share,
  Sick,
  Token,
} from "@mui/icons-material";
import React, { useCallback, useEffect, useState } from "react";
import { useAtom } from "jotai";
import { getList } from "./shared";
import { SiDiscord } from "@icons-pack/react-simple-icons";
import MuiAppBar, { AppBarProps as MuiAppBarProps } from "@mui/material/AppBar";
import MuiPaper, { PaperProps as MuiPaperProps } from "@mui/material/Paper";
import HistoryDialog from "./components/History/HistoryDialog";
import HistoryList from "./components/History/HistoryList";
import InlineBox from "./components/Common/InlineBox";
import { useSnackbar } from "notistack";
import {
  stringTemplate,
  TemplateString,
} from "./components/Common/TemplateString";
import PrivacyDialog from "./components/PrivacyDialog";
import {
  appSecretAtom,
  backendAtom,
  functionsAtom,
  functionSecretAtom,
  saveHistoryAtom,
  selectedFunctionAtom,
  showFunctionDetailAtom,
  themeAtom,
} from "./store";
import HistoryLoader from "./components/History/HistoryLoader";
import mergeTheme from "./shared/theme";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";

const drawerWidth = 240;

const calcDrawerWidth = (
  leftOpen: boolean | undefined,
  rightOpen: boolean | undefined,
  functionListWidth: number,
) => {
  return (
    Number(!!leftOpen) * functionListWidth + Number(!!rightOpen) * drawerWidth
  );
};

const Main = styled("main", {
  shouldForwardProp: (prop) => {
    return (
      prop !== "leftOpen" &&
      prop !== "rightOpen" &&
      prop !== "functionListWidth"
    );
  },
})<{
  leftOpen?: boolean;
  rightOpen?: boolean;
  functionListWidth: number;
}>(({ theme, leftOpen, rightOpen, functionListWidth }) => ({
  flexGrow: 1,
  paddingTop: theme.spacing(2),
  transition: theme.transitions.create("margin", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(leftOpen && {
    transition: theme.transitions.create("margin", {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: `${functionListWidth}px`,
  }),
  ...(rightOpen && {
    transition: theme.transitions.create("margin", {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginRight: `${drawerWidth}px`,
  }),
}));

interface AppBarProps extends MuiAppBarProps {
  leftOpen?: boolean;
  rightOpen?: boolean;
  functionListWidth: number;
}

interface PaperProps extends MuiPaperProps {
  leftOpen?: boolean;
  rightOpen?: boolean;
  functionListWidth: number;
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => {
    return (
      prop !== "leftOpen" &&
      prop !== "rightOpen" &&
      prop !== "functionListWidth"
    );
  },
})<AppBarProps>(({ theme, leftOpen, rightOpen, functionListWidth }) => ({
  transition: theme.transitions.create(["margin", "width"], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(leftOpen && {
    width: `calc(100% - ${calcDrawerWidth(
      leftOpen,
      rightOpen,
      functionListWidth,
    )}px)`,
    marginLeft: `${functionListWidth}px`,
    transition: theme.transitions.create(["margin", "width"], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
  ...(rightOpen && {
    width: `calc(100% - ${calcDrawerWidth(
      leftOpen,
      rightOpen,
      functionListWidth,
    )}px)`,
    marginRight: `${drawerWidth}px`,
    transition: theme.transitions.create(["margin", "width"], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const TransitionFooter = styled(MuiPaper, {
  shouldForwardProp: (prop) => {
    return (
      prop !== "leftOpen" &&
      prop !== "rightOpen" &&
      prop !== "functionListWidth"
    );
  },
})<PaperProps>(({ theme, leftOpen, rightOpen, functionListWidth }) => ({
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  position: "fixed",
  bottom: 0,
  padding: theme.spacing(1),
  zIndex: 100,
  width: "100%",
  ...((leftOpen || rightOpen) && {
    width: `calc(100% - ${calcDrawerWidth(
      leftOpen,
      rightOpen,
      functionListWidth,
    )}px)`,
    transition: theme.transitions.create("width", {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const DrawerHeader = styled("div")(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
  justifyContent: "space-between",
}));

const App = () => {
  const navigate = useNavigate();
  const [selectedFunction] = useAtom(selectedFunctionAtom);
  const [theme] = useAtom(themeAtom);
  const [functions] = useAtom(functionsAtom);
  const [functionSecret] = useAtom(functionSecretAtom);
  const [appSecret, setAppSecret] = useAtom(appSecretAtom);
  const [, setBackendStore] = useAtom(backendAtom);
  const [, setFunctionSecretStore] = useAtom(functionSecretAtom);
  const [showFunctionDetail, setShowFunctionDetail] = useAtom(
    showFunctionDetailAtom,
  );
  const [saveHistory, setSaveHistory] = useAtom(saveHistoryAtom);

  const funixBackend: string | undefined = process.env.REACT_APP_FUNIX_BACKEND;
  const selectedFunctionSecret: string | null = selectedFunction?.secret
    ? selectedFunction?.path in functionSecret
      ? functionSecret[selectedFunction?.path]
      : appSecret
    : null;
  const [backend, setBackend] = useState(funixBackend);
  const [backendURL, setBackendURL] = useState<URL | undefined>(
    backend ? new URL(backend) : undefined,
  );
  const [tempBackend, setTempBackend] = useState(backend);
  const [tempSecret, setTempSecret] = useState(selectedFunctionSecret);
  const [open, setOpen] = useState(false);
  const [tokenOpen, setTokenOpen] = useState(false);
  const [sideBarOpen, setSideBarOpen] = useState(() => {
    return functions !== null && functions.length > 1;
  }); // By default
  const [historySideBarOpen, setHistorySideBarOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [tempAppSecret, setTempAppSecret] = useState(appSecret);
  const [functionListWidth, setFunctionListWidth] = useState(drawerWidth);
  const [onResizing, setOnResizing] = useState(false);
  const [shareOpen, setShareOpen] = useState(false);
  const [shareUrl, setShareUrl] = useState(window.location.href);

  const { enqueueSnackbar } = useSnackbar();

  const handlePointerMoveLeftSidebar = useCallback((e: PointerEvent | any) => {
    setFunctionListWidth(e.clientX - document.body.offsetLeft);
  }, []);

  const handlePointerUpLeftSidebar = () => {
    setOnResizing(false);
    document.removeEventListener(
      "pointermove",
      handlePointerMoveLeftSidebar,
      true,
    );
    document.removeEventListener("pointerup", handlePointerUpLeftSidebar, true);
  };

  const handlePointerDownLeftSidebar = () => {
    setOnResizing(true);
    document.addEventListener(
      "pointermove",
      handlePointerMoveLeftSidebar,
      true,
    );
    document.addEventListener("pointerup", handlePointerUpLeftSidebar, true);
  };

  useEffect(() => {
    getList(new URL("/list", window.location.origin))
      .then(() => {
        setBackend(window.location.origin);
        setTempBackend(window.location.origin);
        setBackendURL(new URL(window.location.origin));
      })
      .catch(() => {
        console.warn("No backend server on the same port!");
      });
  }, [window.location.origin]);

  const isTabBarMode = theme?.funix_nest === true;

  useEffect(() => {
    if (functions !== null) {
      setSideBarOpen(!isTabBarMode && functions.length > 1);
    }
  }, [functions, isTabBarMode]);

  useEffect(() => {
    if (theme !== undefined && theme !== null) {
      document.title = stringTemplate(theme.funix_title || "{{org}}", {
        org: selectedFunction?.name || "Funix",
        functionName: selectedFunction?.name || "No name",
        functionPath: selectedFunction?.path || "No path",
        functionId: selectedFunction?.id || "No id",
        functionHasSecret: selectedFunction?.secret ? "Yes" : "No",
      });
    }
  }, [theme, selectedFunction]);

  useEffect(() => {
    if (typeof backendURL === "undefined") return;
    setBackendStore(backendURL);
  }, [backendURL]);

  useEffect(() => {
    const handleClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (target !== null && target.tagName === "A") {
        const href = target.getAttribute("href");
        if (href && href.startsWith("/")) {
          event.preventDefault();
          navigate(href);
        }
      }
    };
    document.body.addEventListener("click", handleClick);
    return () => {
      document.body.removeEventListener("click", handleClick);
    };
  }, []);

  const checkURL = (url: string | undefined): boolean => {
    if (!url) return false;
    try {
      new URL(url);
      return true;
    } catch (e) {
      return false;
    }
  };

  return (
    <ThemeProvider theme={createTheme(mergeTheme(theme || undefined))}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <HistoryLoader>
          <CssBaseline />
          <HistoryDialog open={historyOpen} setOpen={setHistoryOpen} />
          <PrivacyDialog backend={backendURL} />
          <Dialog
            open={tokenOpen}
            onClose={() => setTokenOpen(false)}
            maxWidth="sm"
            fullWidth
          >
            <DialogTitle>Secret Token</DialogTitle>
            <DialogContent>
              <TextField
                autoFocus
                margin="dense"
                label="Secret Token"
                onChange={(e) => setTempSecret(e.target.value)}
                value={tempSecret}
                fullWidth
                variant="standard"
              />
            </DialogContent>
            <DialogActions>
              <Button
                onClick={() => {
                  setTempSecret(selectedFunctionSecret);
                  setTokenOpen(false);
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={() => {
                  if (selectedFunction) {
                    setFunctionSecretStore((store) => ({
                      ...store,
                      [selectedFunction.path]: tempSecret,
                    }));
                  }
                  setTokenOpen(false);
                }}
              >
                Confirm
              </Button>
            </DialogActions>
          </Dialog>
          <Dialog
            open={shareOpen}
            onClose={() => setShareOpen(false)}
            fullWidth
            maxWidth="md"
          >
            <DialogTitle>Share</DialogTitle>
            <DialogContent>
              <TextField
                margin="dense"
                label="URL"
                fullWidth
                variant="outlined"
                value={shareUrl}
                onChange={(e) => setShareUrl(e.target.value)}
                error={!checkURL(shareUrl)}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        edge="end"
                        onClick={() => {
                          navigator.clipboard.writeText(shareUrl).then(() => {
                            enqueueSnackbar("Copied URL", {
                              variant: "success",
                            });
                          });
                        }}
                      >
                        <ContentCopy />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              <Button
                color="primary"
                startIcon={<Code />}
                onClick={() => {
                  navigator.clipboard
                    .writeText(
                      `<iframe src="${shareUrl}" width="100%" height="100%" style="border: none"></iframe>`,
                    )
                    .then(() => {
                      enqueueSnackbar("Copied iframe", { variant: "success" });
                    });
                }}
              >
                Copy Iframe
              </Button>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setShareOpen(false)}>Close</Button>
            </DialogActions>
          </Dialog>
          <Dialog open={open} onClose={() => setOpen(false)}>
            <DialogTitle>Settings</DialogTitle>
            <DialogContent>
              <TextField
                margin="dense"
                label="Backend URL"
                fullWidth
                variant="standard"
                onChange={(e) => setTempBackend(e.target.value)}
                value={tempBackend}
                error={!checkURL(tempBackend)}
              />
              <TextField
                margin="dense"
                label="All pages secret (for this app)"
                fullWidth
                variant="standard"
                onChange={(e) => setTempAppSecret(e.target.value)}
                value={tempAppSecret}
              />
              <FormGroup>
                <FormControlLabel
                  control={
                    <Switch
                      checked={showFunctionDetail}
                      onChange={(event) => {
                        const value = event.target.checked;
                        localStorage.setItem(
                          "showFunctionDetail",
                          value.toString(),
                        );
                        setShowFunctionDetail(value);
                      }}
                    />
                  }
                  label="Show function detail"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={saveHistory}
                      onChange={(event) => {
                        const value = event.target.checked;
                        localStorage.setItem("saveHistory", value.toString());
                        setSaveHistory(value);
                      }}
                    />
                  }
                  label="Save history"
                />
              </FormGroup>
            </DialogContent>
            <DialogActions>
              <Button
                onClick={() => {
                  setTempBackend(backend);
                  setTempAppSecret(appSecret);
                  setOpen(false);
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={() => {
                  navigate("/");
                  setBackend(tempBackend);
                  setAppSecret(tempAppSecret);
                  setOpen(false);
                }}
                disabled={!checkURL(tempBackend)}
              >
                Confirm
              </Button>
            </DialogActions>
          </Dialog>
          {!isTabBarMode ? (
            <AppBar
              position="fixed"
              leftOpen={sideBarOpen}
              rightOpen={historySideBarOpen}
              functionListWidth={functionListWidth}
            >
              <Toolbar>
                {functions !== null &&
                  functions?.length > 1 &&
                  !isTabBarMode && (
                    <IconButton
                      color="inherit"
                      size="large"
                      onClick={() => setSideBarOpen(true)}
                      sx={{ mr: 2, ...(sideBarOpen && { display: "none" }) }}
                      edge="start"
                    >
                      {theme?.direction === "ltr" ? (
                        <ArrowBack />
                      ) : (
                        <ArrowForward />
                      )}
                    </IconButton>
                  )}
                <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                  <TemplateString
                    template={theme?.funix_header || "{{org}}"}
                    records={{
                      org: selectedFunction?.name || "Funix",
                      functionName: selectedFunction?.name || "No name",
                      functionPath: selectedFunction?.path || "No path",
                      functionId: selectedFunction?.id || "No id",
                      functionHasSecret: selectedFunction?.secret
                        ? "Yes"
                        : "No",
                      functionHasWebsocket: selectedFunction?.websocket
                        ? "Yes"
                        : "No",
                      functionModule: selectedFunction?.module || "No module",
                    }}
                  />
                </Typography>
                {selectedFunction && selectedFunction.secret && (
                  <IconButton
                    size="large"
                    color="inherit"
                    edge="end"
                    onClick={() => {
                      setTempSecret(selectedFunctionSecret);
                      setTokenOpen(true);
                    }}
                  >
                    <Token />
                  </IconButton>
                )}
                <IconButton
                  size="large"
                  color="inherit"
                  edge="end"
                  onClick={() => setHistoryOpen(true)}
                >
                  <History />
                </IconButton>
                <IconButton
                  size="large"
                  color="inherit"
                  edge="end"
                  onClick={() =>
                    setHistorySideBarOpen((prevState) => !prevState)
                  }
                >
                  <EventNote />
                </IconButton>
                <IconButton
                  size="large"
                  color="inherit"
                  edge="end"
                  onClick={() => {
                    setShareOpen(true);
                    setShareUrl(window.location.href);
                  }}
                >
                  <Share />
                </IconButton>
                <IconButton
                  size="large"
                  onClick={() => setOpen(true)}
                  color="inherit"
                  edge="end"
                >
                  <Settings />
                </IconButton>
              </Toolbar>
            </AppBar>
          ) : (
            <Box
              sx={{
                position: "fixed",
                top: 0,
                left: 0,
                right: 0,
                zIndex: (theme) => theme.zIndex.appBar,
              }}
            >
              {backendURL && (
                <FunixTabBar
                  backend={backendURL}
                  onHistoryOpen={() => setHistoryOpen(true)}
                  onHistorySideBarToggle={() =>
                    setHistorySideBarOpen((prevState) => !prevState)
                  }
                  sideBarOpen={sideBarOpen}
                  onSideBarToggle={() => setSideBarOpen(true)}
                  functions={functions}
                />
              )}
            </Box>
          )}
          {!isTabBarMode && (
            <Drawer
              sx={{
                width: functionListWidth,
                flexShrink: 0,
                "& .MuiDrawer-paper": {
                  width: functionListWidth,
                  boxSizing: "border-box",
                },
              }}
              variant="persistent"
              anchor="left"
              open={sideBarOpen}
              ModalProps={{
                keepMounted: true,
              }}
            >
              <DrawerHeader>
                <ListItem>
                  <ListItemIcon>
                    <Functions />
                  </ListItemIcon>
                  <ListItemText primary="Choose" />
                </ListItem>
                <IconButton onClick={() => setSideBarOpen(false)}>
                  {theme?.direction === "ltr" ? (
                    <ArrowForward />
                  ) : (
                    <ArrowBack />
                  )}
                </IconButton>
              </DrawerHeader>
              <Divider />
              {backendURL ? (
                <FunixFunctionList backend={backendURL} />
              ) : (
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Sick />
                    </ListItemIcon>
                    <ListItemText primary="No backend server" />
                  </ListItem>
                </List>
              )}
              <Box
                component="div"
                sx={{
                  width: ".75rem",
                  height: "100%",
                  margin: "0 auto",
                  backgroundColor: (theme) =>
                    `${theme.palette.mode === "dark" && onResizing && "grey.900"}`,
                  "&:hover": {
                    backgroundColor: (theme) =>
                      `${theme.palette.mode === "dark" ? "grey.900" : "grey.100"}`,
                    cursor: "ew-resize",
                  },
                  position: "absolute",
                  top: 0,
                  right: 0,
                  bottom: 0,
                  zIndex: 100,
                }}
                onMouseDown={handlePointerDownLeftSidebar}
                onContextMenu={(event) => {
                  event.preventDefault();
                  setFunctionListWidth(drawerWidth);
                }}
              />
            </Drawer>
          )}
          <Main
            leftOpen={!isTabBarMode && sideBarOpen}
            rightOpen={historySideBarOpen}
            functionListWidth={functionListWidth}
          >
            <Container
              sx={{
                paddingTop: 10,
                paddingBottom: 8,
              }}
              maxWidth={false}
            >
              {backendURL ? (
                <Stack
                  spacing={2}
                  sx={{ width: "100%", margin: "0 auto" }}
                  id="funix-stack"
                >
                  <FunixFunctionSelected backend={backendURL} />
                </Stack>
              ) : (
                <Alert severity="error">
                  <AlertTitle>No backend server</AlertTitle>
                  <InlineBox>
                    Please use
                    <code>python -m funix [module]</code>
                    to start frontend server or click
                    <Settings />
                    to set backend server.
                  </InlineBox>
                </Alert>
              )}
            </Container>
            <TransitionFooter
              leftOpen={!isTabBarMode && sideBarOpen}
              rightOpen={historySideBarOpen}
              functionListWidth={functionListWidth}
            >
              <Container maxWidth={false}>
                <Stack
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center"
                  spacing={2}
                >
                  <Typography variant="body2">
                    <TemplateString
                      template={theme?.funix_footer || "{{org}}"}
                      records={{
                        org: [
                          "This app is automatically generated by ",
                          <Link href="https://funix.io">Funix.io</Link>,
                          ", the laziest way to build apps in Python - lazier than Streamlit or Gradio.",
                        ],
                        year: new Date().getFullYear().toString(),
                        funixLink: (
                          <Link href="https://funix.io">Funix.io</Link>
                        ),
                      }}
                    />
                  </Typography>
                  <Box>
                    {theme?.funix_disable_footer_icons !== true ? (
                      <>
                        <Link href="https://github.com/TexteaInc/funix">
                          <IconButton>
                            <GitHub />
                          </IconButton>
                        </Link>
                        <Link href="https://discord.gg/sxHQE3mvuZ">
                          <IconButton>
                            <SiDiscord />
                          </IconButton>
                        </Link>
                      </>
                    ) : null}
                    {/* <Link href="https://twitter.com/texteaInc">
                <IconButton>
                  <Twitter />
                </IconButton>
              </Link> */}
                  </Box>
                </Stack>
              </Container>
            </TransitionFooter>
          </Main>
          <Drawer
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              "& .MuiDrawer-paper": {
                width: drawerWidth,
                boxSizing: "border-box",
              },
            }}
            variant="persistent"
            anchor="right"
            open={historySideBarOpen}
            ModalProps={{
              keepMounted: true,
            }}
          >
            <DrawerHeader>
              <ListItem>
                <IconButton onClick={() => setHistorySideBarOpen(false)}>
                  {theme?.direction === "ltr" ? (
                    <ArrowBack />
                  ) : (
                    <ArrowForward />
                  )}
                </IconButton>
              </ListItem>
            </DrawerHeader>
            <Divider />
            <HistoryList isOpen={historySideBarOpen} />
          </Drawer>
        </HistoryLoader>
      </LocalizationProvider>
    </ThemeProvider>
  );
};

export default App;
