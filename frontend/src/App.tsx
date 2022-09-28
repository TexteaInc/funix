import React, { useState } from "react";
import {
  Alert,
  Button,
  Container,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import TexteaFunctionList from "./components/TexteaFunctionList";
import TexteaFunctionSelected from "./components/TexteaFunctionSelected";
import { Navigate, useLocation } from "react-router-dom";
import { Path } from "history";

const App = () => {
  const { search } = useLocation();
  const query = new URLSearchParams(search);
  const backendStr = query.get("backend");
  if (backendStr == null) {
    const [backendStrInput, setBackendStrInput] = useState<string>(
      "http://localhost:8080"
    );
    const [toRedirect, setToRedirect] = useState<boolean>(false);
    if (!toRedirect) {
      return (
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
      );
    } else {
      const newParams = new URLSearchParams({
        backend: backendStrInput,
      });
      const toPath: Partial<Path> = {
        search: newParams.toString(),
      };
      return <Navigate to={toPath} replace={false} />;
    }
  } else {
    let backend: URL | undefined = undefined;
    try {
      backend = new URL(backendStr);
    } catch (e: any) {
      return (
        <Container sx={{ paddingY: 2 }}>
          <Alert severity="error">Unable to encode URL</Alert>
        </Container>
      );
    }

    return (
      <Container sx={{ paddingY: 2 }}>
        <Stack spacing={2}>
          <TexteaFunctionList backend={backend} />
          <TexteaFunctionSelected backend={backend} />
        </Stack>
      </Container>
    );
  }
};

export default App;
