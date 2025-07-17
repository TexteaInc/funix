import { Theme } from "@mui/material";
import _ from "lodash";

const defaultLightTheme = {
  palette: {
    type: "light",
    primary: {
      main: "#fefefe",
      light: "#ffffff",
      dark: "#dfdfdf",
    },
    secondary: {
      main: "#e040fb",
    },
    background: {
      paper: "#fefefe",
    },
  },
  components: {
    MuiSvgIcon: {
      styleOverrides: {
        root: {
          color: "inherit !important",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        textPrimary: {
          color: "#1976d2",
        },
      },
    },
    MuiCheckbox: {
      styleOverrides: {
        root: {
          color: "rgba(0, 0, 0, 0.6)",
          "&.Mui-checked": {
            color: "rgb(0, 0, 0)",
          },
        },
      },
    },
    MuiSlider: {
      styleOverrides: {
        root: {
          color: "rgb(0, 0, 0) !important",
        },
      },
    },
    MuiInput: {
      styleOverrides: {
        root: {
          "&::after": {
            borderBottomColor: "rgb(0, 0, 0, 0.87) !important",
          },
        },
        underline: {
          "&:before": {
            borderColor: "rgba(0, 0, 0, 0.42) !important",
          },
          "&:hover::before": {
            borderColor: "rgba(0, 0, 0, 0.87) !important",
          },
        },
      },
    },
    MuiFormLabel: {
      styleOverrides: {
        root: {
          "&.Mui-focused": {
            color: "rgb(0, 0, 0, 0.87) !important",
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& fieldset": {
            borderColor: "rgba(0, 0, 0, 0.42) !important",
          },
          "&&:hover fieldset": {
            borderColor: "rgba(0, 0, 0, 0.87) !important",
            borderWidth: "2px !important",
          },
        },
      },
    },
    MuiRadio: {
      styleOverrides: {
        root: {
          "&.Mui-checked": {
            color: "rgb(0, 0, 0) !important",
          },
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        track: {
          backgroundColor: "rgb(0, 0, 0) !important",
          "&.Mui-checked": {
            backgroundColor: "rgb(0, 0, 0) !important",
          },
        },
        textPrimary: {
          color: "rgb(0, 0, 0) !important",
        },
      },
    },
    MuiLink: {
      styleOverrides: {
        root: {
          color: "#1976d2",
        },
      },
    },
  },
};

const defaultDarkTheme = {
  palette: {
    type: "dark",
  },
};

const mergeTheme = (theme: Record<string, any> | undefined): Theme => {
  if (!theme) {
    return defaultLightTheme as unknown as Theme;
  }

  if (theme?.palette?.type === "dark") {
    return _.merge(defaultDarkTheme, theme) as unknown as Theme;
  }

  return _.merge(defaultLightTheme, theme) as unknown as Theme;
};

export default mergeTheme;
