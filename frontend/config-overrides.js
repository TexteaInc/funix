const ProgressBarPlugin = require("progress-bar-webpack-plugin");
const { override, addWebpackPlugin } = require("customize-cra");
const webpack = require("webpack");


module.exports = override(
  addWebpackPlugin(
    new ProgressBarPlugin(),
  ),
  addWebpackPlugin(
    new webpack.IgnorePlugin({
      checkResource(resource) {
        return resource === "pdfjs-dist/build/pdf.worker.js";
      }
    }),
  ),
)
