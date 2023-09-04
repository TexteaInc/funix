const ProgressBarPlugin = require("progress-bar-webpack-plugin");
const webpack = require("webpack");

module.exports = function override(config) {
  if (process.env.MUI_PRO_LICENSE_KEY) {
    config.plugins.push(
      new webpack.DefinePlugin({
        "process.env.REACT_APP_MUI_PRO_LICENSE_KEY": JSON.stringify(process.env.MUI_PRO_LICENSE_KEY)
      })
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
