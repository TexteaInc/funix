import { WidgetProps } from "@rjsf/core";
import React from "react";
import ReactJson, { InteractionProps } from "react-json-view";
import { Stack, Typography } from "@mui/material";

interface JSONEditorWidgetInterface {
  widget: WidgetProps;
  checkType: string;
}

const JSONEditorWidget = (props: JSONEditorWidgetInterface) => {
  let value = {};
  if (props.widget.schema.type === "array") {
    value = [];
  }
  const [src, setSrc] = React.useState<object>(
    () => props.widget.value || value
  );

  const handleEdit = React.useCallback((value: InteractionProps) => {
    if (value.updated_src instanceof Array) {
      const formatList = value.updated_src.map((item) => {
        if (item === null) return item;
        switch (props.checkType) {
          case "string":
            return item.toString();
          case "number":
            const parsedFloat = parseFloat(item);
            if (!isNaN(parsedFloat) && isFinite(parsedFloat))
              return parsedFloat;
            else return 0.0;
          case "integer":
            const parsedInt = parseInt(item);
            if (!isNaN(parsedInt) && isFinite(parsedInt)) return parsedInt;
            else return 0;
          case "boolean":
            if (typeof item === "boolean") return item;
            else return !!item;
          default:
            return item;
        }
      });
      setSrc(formatList);
      props.widget.onChange(formatList);
    } else {
      setSrc(value.updated_src);
      props.widget.onChange(value.updated_src);
    }
  }, []);

  return (
    <Stack spacing={1}>
      <Typography variant="h5">{props.widget.name}</Typography>
      <ReactJson
        src={src}
        onEdit={handleEdit}
        onDelete={handleEdit}
        onAdd={handleEdit}
      />
    </Stack>
  );
};

export default JSONEditorWidget;
