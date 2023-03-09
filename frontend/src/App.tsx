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
  Fab,
  FormControlLabel,
  IconButton,
  Link,
  Paper,
  Stack,
  Switch,
  TextField,
  ThemeProvider,
  Typography,
} from "@mui/material";
import FunixFunctionList from "./components/FunixFunctionList";
import FunixFunctionSelected from "./components/FunixFunctionSelected";
import { useNavigate } from "react-router-dom";
import { GitHub, Settings } from "@mui/icons-material";
import { memo, useEffect, useState } from "react";
import { storeAtom } from "./store";
import { useAtom } from "jotai";
import { getList } from "./shared";
import { SiDiscord } from "@icons-pack/react-simple-icons";

const App = () => {
  const navigate = useNavigate();
  const funixBackend: string | undefined = process.env.REACT_APP_FUNIX_BACKEND;
  const [backend, setBackend] = useState(funixBackend);
  const [backendURL, setBackendURL] = useState<URL | undefined>(
    backend ? new URL(backend) : undefined
  );
  const [tempBackend, setTempBackend] = useState(backend);
  const [open, setOpen] = useState(false);
  const [{ theme, showFunctionDetail }, setStore] = useAtom(storeAtom);

  const checkURL = (url: string | undefined): boolean => {
    if (!url) return false;
    try {
      new URL(url);
      return true;
    } catch (e) {
      return false;
    }
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

  return (
    <ThemeProvider theme={createTheme(theme || undefined)}>
      <CssBaseline />
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
      <Container sx={{ paddingTop: 2, paddingBottom: 8 }} maxWidth={false}>
        {backendURL ? (
          <Stack
            spacing={2}
            sx={{ width: "100%", margin: "0 auto" }}
            id="funix-stack"
          >
            <FunixFunctionList backend={backendURL} />
            <FunixFunctionSelected backend={backendURL} />
          </Stack>
        ) : (
          <Alert severity="error">
            <AlertTitle>No backend server</AlertTitle>
            <Stack direction="row" alignItems="center" gap={1}>
              Please use <code>python -m funix [module]</code> to start frontend
              server or click <Settings /> to set backend server.
            </Stack>
          </Alert>
        )}
      </Container>
      <Paper
        sx={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          padding: ".5rem",
          zIndex: 100,
        }}
        component="footer"
      >
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
      </Paper>
      <Fab
        color="primary"
        onClick={() => setOpen(true)}
        sx={{
          position: "fixed",
          bottom: "4.5rem",
          right: "1.5rem",
          zIndex: 100,
        }}
      >
        <Settings />
      </Fab>
    </ThemeProvider>
  );
};

export default memo(App);
