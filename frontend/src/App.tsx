import React, { useState } from "react";
import {
  Alert,
  Button,
  Container,
  createTheme,
  Stack,
  TextField,
  ThemeProvider,
  Typography,
} from "@mui/material";
import TexteaFunctionList from "./components/TexteaFunctionList";
import TexteaFunctionSelected from "./components/TexteaFunctionSelected";
import { Navigate, useLocation } from "react-router-dom";
import { Path } from "history";

const App = () => {
  const [theme, setTheme] = React.useState<Record<string, any>>({});
  const { search } = useLocation();
  const query = new URLSearchParams(search);
  const backendStr = query.get("backend");
  if (backendStr == null) {
    const [backendStrInput, setBackendStrInput] = useState<string>(
      "http://localhost:4010"
    );
    const [toRedirect, setToRedirect] = useState<boolean>(false);
    if (!toRedirect) {
      return (
        <ThemeProvider theme={createTheme(theme)}>
          <Container sx={{ paddingY: 2 }}>
            <Typography variant="h4">PyDataFront</Typography>
            <TextField
              label="Backend URL"
              value={backendStrInput}
              onChange={(e) => setBackendStrInput(e.currentTarget.value)}
              fullWidth
              sx={{ mt: 2 }}
            />
            <Button
              variant="contained"
              onClick={() => setToRedirect(true)}
              sx={{ mt: 1 }}
            >
              Submit
            </Button>
          </Container>
        </ThemeProvider>
      );
    } else {
      const newParams = new URLSearchParams({
        backend: backendStrInput,
      });
      const toPath: Partial<Path> = {
        search: newParams.toString(),
      };
      return (
        <ThemeProvider theme={createTheme(theme)}>
          <Navigate to={toPath} />
        </ThemeProvider>
      );
    }
  } else {
    let backend: URL | undefined = undefined;
    try {
      backend = new URL(backendStr);
    } catch (e: any) {
      return (
        <ThemeProvider theme={createTheme(theme)}>
          <Container sx={{ paddingY: 2 }}>
            <Alert severity="error">Unable to encode URL</Alert>
          </Container>
        </ThemeProvider>
      );
    }

    return (
      <ThemeProvider theme={createTheme(theme)}>
        <Container sx={{ paddingY: 2 }}>
          <Stack spacing={2}>
            <TexteaFunctionList backend={backend} />
            <TexteaFunctionSelected backend={backend} setTheme={setTheme} />
          </Stack>
        </Container>
      </ThemeProvider>
    );
  }
};

export default App;
