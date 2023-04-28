import { WidgetProps } from "@rjsf/core";
import React, { useCallback, useEffect } from "react";
import ReactJson, { InteractionProps } from "react-json-view";
import { Stack, Typography } from "@mui/material";
import { castValue, getInitValue } from "../Common/ValueOperation";

interface JSONEditorWidgetInterface {
  widget: WidgetProps;
  checkType: string;
  keys?: { [key: string]: string };
  data?: any;
}

type JSONType = number | string | boolean | object | null | undefined;
type JSONObjectType = { [key: string]: JSONType | any };

const JSONEditorWidget = (props: JSONEditorWidgetInterface) => {
  let value: { [key: string]: JSONType } | JSONType[] = {};
  if (props.widget.schema.type === "array") {
    value = [];
  } else if (props.keys) {
    for (const key in props.keys) {
      value[key] = getInitValue(props.keys[key]);
    }
  }

  const refreshSrc = useCallback(
    () =>
      props.data || props.widget.value || props.widget.schema.default || value,
    [props.data]
  );

  const [src, setSrc] = React.useState<object>(refreshSrc);

  useEffect(() => {
    setSrc(refreshSrc);
  }, [props.data]);

  const handleEdit = React.useCallback((value: InteractionProps) => {
    if (value.updated_src instanceof Array) {
      const formatList = value.updated_src.map((item) => {
        return castValue(item, props.checkType);
      });
      setSrc(formatList);
      props.widget.onChange(formatList);
    } else if (props.keys) {
      const formatDict: { [key: string]: JSONType } = {};
      const JSONTypedUpdatedSource: JSONObjectType = value.updated_src;
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
      setSrc(value.updated_src);
      props.widget.onChange(value.updated_src);
    }
  }, []);

  const reactJSON = props.keys ? (
    <ReactJson src={src} onEdit={handleEdit} />
  ) : (
    <ReactJson
      src={src}
      onEdit={handleEdit}
      onDelete={handleEdit}
      onAdd={handleEdit}
    />
  );

  return (
    <Stack spacing={1}>
      <Typography variant="h5">{props.widget.name}</Typography>
      {reactJSON}
    </Stack>
  );
};

export default JSONEditorWidget;
