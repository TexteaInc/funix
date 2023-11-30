import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { SWRConfig } from "swr";
import { BrowserRouter } from "react-router-dom";
import { closeSnackbar, SnackbarProvider } from "notistack";
import { IconButton } from "@mui/material";
import { Close } from "@mui/icons-material";
import { registerLicense } from "./Key";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

registerLicense();

root.render(
  <React.StrictMode>
    <SWRConfig
      value={{
        fetcher: (resource: URL, init?: RequestInit) =>
          fetch(resource, init).then((res) => res.json()),
        suspense: true,
      }}
    >
      <BrowserRouter>
        <SnackbarProvider
          autoHideDuration={3000}
          maxSnack={3}
          action={(key) => (
            <IconButton onClick={() => closeSnackbar(key)} color="inherit">
              <Close />
            </IconButton>
          )}
        >
          <App />
        </SnackbarProvider>
      </BrowserRouter>
    </SWRConfig>
  </React.StrictMode>
);
