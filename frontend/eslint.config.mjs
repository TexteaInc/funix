import eslintPluginPrettierRecommended from "eslint-plugin-prettier/recommended";
import eslint from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config({
  rules: {
    "@typescript-eslint/interface-name-prefix": "off",
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-explicit-any": "off",
  },
  extends: [
    eslint.configs.recommended,
    ...tseslint.configs.recommended,
    eslintPluginPrettierRecommended,
  ],
  languageOptions: {
    parserOptions: {
      project: "tsconfig.json",
      tsConfigRootDir: import.meta.dirname,
    },
  },
  ignores: [
    "node_modules/",
    "dist/",
    "build/",
    "package.json",
    "public",
    ".yarn",
  ],
});