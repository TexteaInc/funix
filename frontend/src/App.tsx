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
  Functions,
  GitHub,
  Settings,
  Sick,
  Token,
} from "@mui/icons-material";
import React, { memo, useEffect, useState } from "react";
import { storeAtom } from "./store";
import { useAtom } from "jotai";
import { getList } from "./shared";
import { SiDiscord } from "@icons-pack/react-simple-icons";
import MuiAppBar, { AppBarProps as MuiAppBarProps } from "@mui/material/AppBar";
import MuiPaper, { PaperProps as MuiPaperProps } from "@mui/material/Paper";

// From MUI docs
const drawerWidth = 240;

const Main = styled("main", { shouldForwardProp: (prop) => prop !== "open" })<{
  open?: boolean;
}>(({ theme, open }) => ({
  flexGrow: 1,
  paddingTop: theme.spacing(2),
  transition: theme.transitions.create("margin", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    transition: theme.transitions.create("margin", {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: `${drawerWidth}px`,
  }),
}));

interface AppBarProps extends MuiAppBarProps {
  open?: boolean;
}

interface PaperProps extends MuiPaperProps {
  open?: boolean;
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== "open",
})<AppBarProps>(({ theme, open }) => ({
  transition: theme.transitions.create(["margin", "width"], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: `${drawerWidth}px`,
    transition: theme.transitions.create(["margin", "width"], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const TransitionFooter = styled(MuiPaper, {
  shouldForwardProp: (prop) => prop !== "open",
})<PaperProps>(({ theme, open }) => ({
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  position: "fixed",
  bottom: 0,
  padding: theme.spacing(1),
  zIndex: 100,
  width: "100%",
  ...(open && {
    width: `calc(100% - ${drawerWidth}px)`,
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
    { theme, showFunctionDetail, selectedFunction, functionSecret },
    setStore,
  ] = useAtom(storeAtom);

  const funixBackend: string | undefined = process.env.REACT_APP_FUNIX_BACKEND;
  const selectedFunctionSecret: string | null = selectedFunction?.secret
    ? selectedFunction?.name in functionSecret
      ? functionSecret[selectedFunction?.name]
      : null
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
            autoFocus
            margin="dense"
            label="Backend URL"
            fullWidth
            variant="standard"
            onChange={(e) => setTempBackend(e.target.value)}
            value={tempBackend}
            error={!checkURL(tempBackend)}
          />
          <FormControlLabel
            control={
              <Switch
                value={showFunctionDetail}
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
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setTempBackend(backend);
              setOpen(false);
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              navigate("/");
              setBackend(tempBackend);
              setOpen(false);
            }}
            disabled={!checkURL(tempBackend)}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
      <AppBar position="fixed" open={sideBarOpen}>
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
            {selectedFunction ? selectedFunction.name : "Funix"}
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
            <ListItem disablePadding>
              <ListItemIcon>
                <Sick />
              </ListItemIcon>
              <ListItemText primary="No backend server" />
            </ListItem>
          </List>
        )}
      </Drawer>
      <Main open={sideBarOpen}>
        <Container sx={{ paddingTop: 10, paddingBottom: 8 }} maxWidth={false}>
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
              <Stack direction="row" alignItems="center" gap={1}>
                Please use <code>python -m funix [module]</code> to start
                frontend server or click <Settings /> to set backend server.
              </Stack>
            </Alert>
          )}
        </Container>
        <TransitionFooter open={sideBarOpen}>
          <Container maxWidth={false}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
              spacing={2}
            >
              <Typography variant="body2">
                Powered by <Link href="http://funix.io">Funix.io</Link>
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
    </ThemeProvider>
  );
};

export default memo(App);
