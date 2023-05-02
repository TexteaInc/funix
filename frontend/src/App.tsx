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
import { useNavigate } from "react-router-dom";
import {
  ArrowBack,
  ArrowForward,
  EventNote,
  Functions,
  GitHub,
  History,
  Settings,
  Sick,
  Token,
} from "@mui/icons-material";
import React, { useEffect, useState } from "react";
import { storeAtom } from "./store";
import { useAtom } from "jotai";
import { getList } from "./shared";
import { SiDiscord } from "@icons-pack/react-simple-icons";
import MuiAppBar, { AppBarProps as MuiAppBarProps } from "@mui/material/AppBar";
import MuiPaper, { PaperProps as MuiPaperProps } from "@mui/material/Paper";
import HistoryDialog from "./components/History/HistoryDialog";
import HistoryList from "./components/History/HistoryList";
import MarkdownDiv from "./components/Common/MarkdownDiv";
import InlineBox from "./components/Common/InlineBox";

// From MUI docs
const drawerWidth = 240;

const calcDrawerWidth = (
  leftOpen: boolean | undefined,
  rightOpen: boolean | undefined
) => {
  return (Number(!!leftOpen) + Number(!!rightOpen)) * drawerWidth;
};

const Main = styled("main", {
  shouldForwardProp: (prop) => {
    return prop !== "leftOpen" && prop !== "rightOpen";
  },
})<{
  leftOpen?: boolean;
  rightOpen?: boolean;
}>(({ theme, leftOpen, rightOpen }) => ({
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
    marginLeft: `${drawerWidth}px`,
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
}

interface PaperProps extends MuiPaperProps {
  leftOpen?: boolean;
  rightOpen?: boolean;
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => {
    return prop !== "leftOpen" && prop !== "rightOpen";
  },
})<AppBarProps>(({ theme, leftOpen, rightOpen }) => ({
  transition: theme.transitions.create(["margin", "width"], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(leftOpen && {
    width: `calc(100% - ${calcDrawerWidth(leftOpen, rightOpen)}px)`,
    marginLeft: `${drawerWidth}px`,
    transition: theme.transitions.create(["margin", "width"], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
  ...(rightOpen && {
    width: `calc(100% - ${calcDrawerWidth(leftOpen, rightOpen)}px)`,
    marginRight: `${drawerWidth}px`,
    transition: theme.transitions.create(["margin", "width"], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const TransitionFooter = styled(MuiPaper, {
  shouldForwardProp: (prop) => {
    return prop !== "leftOpen" && prop !== "rightOpen";
  },
})<PaperProps>(({ theme, leftOpen, rightOpen }) => ({
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
    width: `calc(100% - ${calcDrawerWidth(leftOpen, rightOpen)}px)`,
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
  const [
    {
      theme,
      showFunctionDetail,
      selectedFunction,
      functionSecret,
      saveHistory,
      appSecret,
    },
    setStore,
  ] = useAtom(storeAtom);

  const funixBackend: string | undefined = process.env.REACT_APP_FUNIX_BACKEND;
  const selectedFunctionSecret: string | null = selectedFunction?.secret
    ? selectedFunction?.name in functionSecret
      ? functionSecret[selectedFunction?.name]
      : appSecret
    : null;
  const [backend, setBackend] = useState(funixBackend);
  const [backendURL, setBackendURL] = useState<URL | undefined>(
    backend ? new URL(backend) : undefined
  );
  const [tempBackend, setTempBackend] = useState(backend);
  const [tempSecret, setTempSecret] = useState(selectedFunctionSecret);
  const [open, setOpen] = useState(false);
  const [tokenOpen, setTokenOpen] = useState(false);
  const [sideBarOpen, setSideBarOpen] = useState(true); // By default
  const [historySideBarOpen, setHistorySideBarOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [tempAppSecret, setTempAppSecret] = useState(appSecret);

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

  useEffect(() => {
    if (typeof backendURL === "undefined") return;
    setStore((store) => {
      return {
        ...store,
        backend: backendURL,
      };
    });
  }, [backendURL]);

  useEffect(() => {
    setStore((store) => ({
      ...store,
      sideBarOpen: sideBarOpen,
    }));
  }, [sideBarOpen]);

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
    <ThemeProvider theme={createTheme(theme || undefined)}>
      <CssBaseline />
      <HistoryDialog open={historyOpen} setOpen={setHistoryOpen} />
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
                setStore((store) => ({
                  ...store,
                  functionSecret: {
                    ...store.functionSecret,
                    [selectedFunction.name]: tempSecret,
                  },
                }));
              }
              setTokenOpen(false);
            }}
          >
            Confirm
          </Button>
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
                    setStore((store) => ({
                      ...store,
                      showFunctionDetail: event.target.checked,
                    }));
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
                    setStore((store) => ({
                      ...store,
                      saveHistory: event.target.checked,
                    }));
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
              setStore((store) => ({
                ...store,
                appSecret: tempAppSecret,
              }));
              setOpen(false);
            }}
            disabled={!checkURL(tempBackend)}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
      <AppBar
        position="fixed"
        leftOpen={sideBarOpen}
        rightOpen={historySideBarOpen}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            size="large"
            onClick={() => setSideBarOpen(true)}
            sx={{ mr: 2, ...(sideBarOpen && { display: "none" }) }}
            edge="start"
          >
            {theme?.direction === "ltr" ? <ArrowBack /> : <ArrowForward />}
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            <MarkdownDiv
              markdown={selectedFunction?.name || "Funix"}
              isRenderInline={true}
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
            onClick={() => setHistorySideBarOpen((prevState) => !prevState)}
          >
            <EventNote />
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
        anchor="left"
        open={sideBarOpen}
      >
        <DrawerHeader>
          <ListItem>
            <ListItemIcon>
              <Functions />
            </ListItemIcon>
            <ListItemText primary="Choose" />
          </ListItem>
          <IconButton onClick={() => setSideBarOpen(false)}>
            {theme?.direction === "ltr" ? <ArrowForward /> : <ArrowBack />}
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
      </Drawer>
      <Main leftOpen={sideBarOpen} rightOpen={historySideBarOpen}>
        <Container sx={{ paddingTop: 10, paddingBottom: 8 }} maxWidth={false}>
          {backendURL ? (
            <Stack
              spacing={2}
              sx={{ width: "100%", margin: "0 auto" }}
              id="funix-stack"
            >
              <FunixFunctionSelected
                backend={backendURL}
                leftSideBarOpen={sideBarOpen}
                rightSideBarOpen={historySideBarOpen}
              />
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
        <TransitionFooter leftOpen={sideBarOpen} rightOpen={historySideBarOpen}>
          <Container maxWidth={false}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
              spacing={2}
            >
              <Typography variant="body2">
                Power by <Link href="http://funix.io">Funix.io</Link>, minimally
                building apps in Python
              </Typography>
              <Box>
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
      >
        <DrawerHeader>
          <ListItem>
            <IconButton onClick={() => setHistorySideBarOpen(false)}>
              {theme?.direction === "ltr" ? <ArrowBack /> : <ArrowForward />}
            </IconButton>
          </ListItem>
        </DrawerHeader>
        <Divider />
        <HistoryList />
      </Drawer>
    </ThemeProvider>
  );
};

export default App;
