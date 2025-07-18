import { Theme } from "@mui/material";
import _ from "lodash";

const defaultLightTheme = {
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: "#ffffff",
          color: "inherit",
          boxShadow:
            "0px 2px 4px -1px rgba(25,118,210,0.2),0px 4px 5px 0px rgba(25,118,210,0.14),0px 1px 10px 0px rgba(25,118,210,0.12)",
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
