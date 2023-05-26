const ProgressBarPlugin = require("progress-bar-webpack-plugin");
const { override, addWebpackPlugin } = require("customize-cra");


class NoPDFWorkerPlugin {
  apply(compiler) {
    compiler.hooks.emit.tapAsync("NoPDFWorkerPlugin", (compilation, callback) => {
      for (const filename in compilation.assets) {
        if (filename.includes("pdf.worker")) {
          delete compilation.assets[filename];
        }
      }
      callback();
    });
  }
}

module.exports = override(
  addWebpackPlugin(
    new ProgressBarPlugin(),
  ),
  addWebpackPlugin(
    new NoPDFWorkerPlugin(),
  )
)
