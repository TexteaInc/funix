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
          {process.env.REACT_APP_IN_FUNIX === undefined ? (
            <>
              <script src="https://d3js.org/d3.v5.js"></script>
              <script src="https://mpld3.github.io/js/mpld3.v0.5.8.js"></script>
            </>
          ) : (
            <>
              <script src="/static/js/d3.v5.js"></script>
              <script src="/static/js/mpld3.v0.5.8.js"></script>
            </>
          )}
          <App />
        </SnackbarProvider>
      </BrowserRouter>
    </SWRConfig>
  </React.StrictMode>
);
