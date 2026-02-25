import {
  JsonViewer,
  applyValue,
  deleteValue,
  getPathValue,
} from "@textea/json-viewer";
import { useTheme } from "@mui/material";
import React from "react";

interface ThemeReactJsonProps {
  src: object;
  collapsed?: boolean | number;
  onEdit?: (params: {
    updated_src: object;
    name: string | null;
    new_value: any;
    existing_value: any;
  }) => void;
  onDelete?: (params: {
    updated_src: object;
    name: string | null;
    existing_value: any;
  }) => void;
  onAdd?: (params: {
    updated_src: object;
    name: string | null;
    new_value: any;
    existing_value: any;
  }) => void;
  theme?: string;
}

const ThemeReactJson = (props: ThemeReactJsonProps) => {
  const muiTheme = useTheme();
  const [value, setValue] = React.useState(props.src);

  React.useEffect(() => {
    setValue(props.src);
  }, [props.src]);

  const defaultInspectDepth =
    props.collapsed === true
      ? 0
      : props.collapsed === false || props.collapsed === undefined
        ? 5
        : typeof props.collapsed === "number"
          ? props.collapsed
          : 5;

  const editable = !!(props.onEdit || props.onAdd || props.onDelete);

  const colorScheme: "light" | "dark" =
    muiTheme.palette.mode === "dark" ? "dark" : "light";

  return (
    <JsonViewer
      value={value}
      defaultInspectDepth={defaultInspectDepth}
      editable={editable}
      enableAdd={!!props.onAdd}
      enableDelete={!!props.onDelete}
      theme={colorScheme}
      onChange={(path, oldValue, newValue) => {
        const updatedSrc = applyValue(value, path as (string | number)[], newValue);
        setValue(updatedSrc);
        if (props.onEdit) {
          props.onEdit({
            updated_src: updatedSrc,
            name: path.length > 0 ? String(path[path.length - 1]) : null,
            new_value: newValue,
            existing_value: oldValue,
          });
        }
      }}
      onAdd={(path) => {
        const typedPath = path as (string | number)[];
        const target = getPathValue(value, typedPath);
        let updatedSrc;
        if (Array.isArray(target)) {
          updatedSrc = applyValue(
            value,
            [...typedPath, (target as unknown[]).length],
            "",
          );
        } else {
          const key = window.prompt("Enter new key name:");
          if (!key) return;
          updatedSrc = applyValue(value, [...typedPath, key], "");
        }
        setValue(updatedSrc);
        if (props.onAdd) {
          props.onAdd({
            updated_src: updatedSrc,
            name: path.length > 0 ? String(path[path.length - 1]) : null,
            new_value: "",
            existing_value: undefined,
          });
        }
      }}
      onDelete={(path, oldValue) => {
        const updatedSrc = deleteValue(value, path as (string | number)[], oldValue);
        setValue(updatedSrc);
        if (props.onDelete) {
          props.onDelete({
            updated_src: updatedSrc,
            name: path.length > 0 ? String(path[path.length - 1]) : null,
            existing_value: oldValue,
          });
        }
      }}
    />
  );
};

export default ThemeReactJson;
