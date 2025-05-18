const ProgressBarPlugin = require("progress-bar-webpack-plugin");
const SaveRemoteFilePlugin = require("save-remote-file-webpack-plugin");
const webpack = require("webpack");

const scripts = process.env.REACT_APP_IN_FUNIX
  ? `
  <script src="static/js/jquery-3.7.1.min.js"></script>
  <script src="static/js/mpl.js"></script>
  <link rel="stylesheet" href="static/css/fbm.css" />
  <link rel="stylesheet" href="static/css/mpl.css" />
  `
  : `
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/matplotlib/matplotlib@v3.10.x/lib/matplotlib/backends/web_backend/js/mpl.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/matplotlib/matplotlib@v3.10.x/lib/matplotlib/backends/web_backend/css/fbm.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/matplotlib/matplotlib@v3.10.x/lib/matplotlib/backends/web_backend/css/mpl.css" />
  `;

module.exports = function override(config) {
  if (process.env.MUI_PRO_LICENSE_KEY) {
    config.plugins.push(
      new webpack.DefinePlugin({
        "process.env.REACT_APP_MUI_PRO_LICENSE_KEY": JSON.stringify(
          process.env.MUI_PRO_LICENSE_KEY,
        ),
      }),
    );
  }

  config.module.rules.push({
    test: /\.html$/i,
    type: "asset/source",
  });
  config.module.rules.push({
    test: /index\.html$/,
    loader: "string-replace-loader",
    options: {
      search: "<!--%SCRIPTS%-->",
      replace: scripts,
    },
  });

  if (process.env.REACT_APP_IN_FUNIX) {
    config.plugins.push(
      new SaveRemoteFilePlugin([
        {
          url: "https://code.jquery.com/jquery-3.7.1.min.js",
          filepath: "static/js/jquery-3.7.1.min.js",
          hash: false,
        },
        {
          url: "https://cdn.jsdelivr.net/gh/matplotlib/matplotlib@v3.10.x/lib/matplotlib/backends/web_backend/js/mpl.js",
          filepath: "static/js/mpl.js",
          hash: false,
        },
        {
          url: "https://cdn.jsdelivr.net/gh/matplotlib/matplotlib@v3.10.x/lib/matplotlib/backends/web_backend/css/fbm.css",
          filepath: "static/css/fbm.css",
          hash: false,
        },
        {
          url: "https://cdn.jsdelivr.net/gh/matplotlib/matplotlib@v3.10.x/lib/matplotlib/backends/web_backend/css/mpl.css",
          filepath: "static/css/mpl.css",
          hash: false,
        },
      ]),
    );
  }

  config.plugins.push(new ProgressBarPlugin());
  return config;
};
