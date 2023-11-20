const ProgressBarPlugin = require("progress-bar-webpack-plugin");
const SaveRemoteFilePlugin = require("save-remote-file-webpack-plugin");
const webpack = require("webpack");

module.exports = function override(config) {
  if (process.env.MUI_PRO_LICENSE_KEY) {
    config.plugins.push(
      new webpack.DefinePlugin({
        "process.env.REACT_APP_MUI_PRO_LICENSE_KEY": JSON.stringify(process.env.MUI_PRO_LICENSE_KEY)
      })
    )
  }
  if (process.env.REACT_APP_IN_FUNIX) {
    config.plugins.push(
      new SaveRemoteFilePlugin([{
        url: "https://d3js.org/d3.v5.js",
        filepath: "static/js/d3.v5.js",
        hash: false
      }, {
        url: "https://mpld3.github.io/js/mpld3.v0.5.8.js",
        filepath: "static/js/mpld3.v0.5.8.js",
        hash: false
      }]),
    )
  }
  config.plugins.push(
    new ProgressBarPlugin(),
    new webpack.IgnorePlugin({
      checkResource(resource) {
        return resource === "pdfjs-dist/build/pdf.worker.js";
      }
    }),
  )
  return config;
}
