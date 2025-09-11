import React from "react";
import { Editor } from "ketcher-react";
import { Box, SxProps, Theme } from "@mui/material";
import "miew/dist/miew.min.css";
import "ketcher-react/dist/index.css";
import {
  useKetcherEditor,
  UseKetcherEditorOptions,
} from "../hooks/useKetcherEditor";

declare global {
  interface Window {
    ketcher: any;
  }
}

export interface KetcherEditorProps extends UseKetcherEditorOptions {
  width?: string | number;
  height?: string | number;
  sx?: SxProps<Theme>;
  staticResourcesUrl?: string;
  errorHandler?: (error: any) => void;
}

const KetcherEditor: React.FC<KetcherEditorProps> = React.memo((props) => {
  const {
    width = "100%",
    height = "700px",
    sx,
    staticResourcesUrl = "",
    errorHandler = () => {},
    ...hookOptions
  } = props;

  const { structServiceProvider, handleInit } = useKetcherEditor(hookOptions);

  return (
    <Box
      sx={{
        width,
        height,
        resize: "vertical",
        ...sx,
      }}
    >
      <Editor
        staticResourcesUrl={staticResourcesUrl}
        structServiceProvider={structServiceProvider}
        errorHandler={errorHandler}
        onInit={handleInit}
      />
    </Box>
  );
});

KetcherEditor.displayName = "KetcherEditor";

export default KetcherEditor;
