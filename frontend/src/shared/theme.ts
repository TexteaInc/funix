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

const mergeIcon = (theme: Record<string, any>): Theme => {
  const url = theme.funix_icon as string | false;
  if (!url) {
    return theme as unknown as Theme;
  }
  return _.merge(theme, {
    components: {
      MuiAppBar: {
        styleOverrides: {
          root: {
            "& .MuiToolbar-root:before": {
              content: '""',
              "background-image": `url(${url})`,
              display: "block",
              "background-size": "contain",
              "background-repeat": "no-repeat",
              "background-position": "left",
              "margin-right": "10px",
              height: theme.funix_icon_height || "100%",
              width: theme.funix_icon_width || "100%",
            },
          },
        },
      },
    },
  }) as unknown as Theme;
};

const mergeTheme = (theme: Record<string, any> | undefined): Theme => {
  if (!theme) {
    return defaultLightTheme as unknown as Theme;
  }
  const mode = theme?.palette?.type === "dark" ? "dark" : "light";
  let modifiedTheme = theme;
  modifiedTheme = mergeIcon(modifiedTheme);

  return mode === "dark"
    ? (_.merge(defaultDarkTheme, modifiedTheme) as unknown as Theme)
    : (_.merge(defaultLightTheme, modifiedTheme) as unknown as Theme);
};

export default mergeTheme;
