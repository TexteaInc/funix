import { WidgetProps } from "@rjsf/core";
import React from "react";
import { Stack, Typography } from "@mui/material";
import { applyValue, JsonViewer } from "@textea/json-viewer";

interface JSONEditorWidgetInterface {
  widget: WidgetProps;
  checkType: string;
  keys?: { [key: string]: string };
}

type JSONType = number | string | boolean | object | null | undefined;
type JSONObjectType = { [key: string]: JSONType | any };

const JSONEditorWidget = (props: JSONEditorWidgetInterface) => {
  const getInitValue = (type: string): JSONType => {
    switch (type) {
      case "string":
        return "";
      case "number":
        return 0.0;
      case "boolean":
        return false;
      case "integer":
        return 0;
      default:
        return null;
    }
  };

  const castValue = (value: any, type: string): JSONType => {
    if (value === null || value == undefined) return value;
    switch (type) {
      case "string":
        return value.toString();
      case "number":
        const parsedFloat = parseFloat(value);
        if (!isNaN(parsedFloat) && isFinite(parsedFloat)) return parsedFloat;
        else return 0.0;
      case "integer":
        const parsedInt = parseInt(value);
        if (!isNaN(parsedInt) && isFinite(parsedInt)) return parsedInt;
        else return 0;
      case "boolean":
        if (typeof value === "boolean") return value;
        else return !!value;
      default:
        return value;
    }
  };

  let value: { [key: string]: JSONType } | JSONType[] = {};
  if (props.widget.schema.type === "array") {
    value = [];
  } else if (props.keys) {
    for (const key in props.keys) {
      value[key] = getInitValue(props.keys[key]);
    }
  }
  const [src, setSrc] = React.useState<object>(
    () => props.widget.value || value
  );

  const handleChange = React.useCallback(
    (path: (string | number)[], oldValue: any, newValue: any) => {
      if (props.widget.schema.type === "array") {
        const newTypedValue = castValue(newValue, props.checkType);
        const newSrc: (JSONType | any)[] = applyValue(src, path, newTypedValue);
        setSrc(newSrc);
      } else if (props.keys) {
        const formatDict: { [key: string]: JSONType } = {};
        const JSONTypedUpdatedSource: JSONObjectType = applyValue(
          src,
          path,
          newValue
        );
        for (const key in JSONTypedUpdatedSource) {
          if (key in props.keys) {
            formatDict[key] = castValue(
              JSONTypedUpdatedSource[key],
              props.keys[key]
            );
          }
        }
        setSrc(formatDict);
        props.widget.onChange(formatDict);
      } else {
        const newSrc: object = applyValue(src, path, newValue);
        setSrc(newSrc);
        props.widget.onChange(newSrc);
      }
    },
    []
  );

  return (
    <Stack spacing={1}>
      <Typography variant="h5">{props.widget.name}</Typography>
      <JsonViewer value={src} onChange={handleChange} />
    </Stack>
  );
};

export default JSONEditorWidget;
