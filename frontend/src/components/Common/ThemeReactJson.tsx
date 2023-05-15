import ReactJson from "react-json-view";
import type { ReactJsonViewProps } from "react-json-view";
import { useTheme } from "@mui/material";

const ThemeReactJson = (props: ReactJsonViewProps) => {
  const muiTheme = useTheme();

  const theme =
    "theme" in props
      ? props.theme
      : muiTheme.palette.mode === "dark"
      ? "summerfruit"
      : "rjv-default";

  return <ReactJson {...props} theme={theme} />;
};

export default ThemeReactJson;
