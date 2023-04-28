import { WidgetProps } from "@rjsf/core";
import {
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  Switch,
} from "@mui/material";
import React, { useEffect } from "react";
import MarkdownDiv from "../Common/MarkdownDiv";

const SwitchWidget = (props: WidgetProps) => {
  const [checked, setChecked] = React.useState<boolean>(
    !!(props.value || props.schema.default)
  );

  useEffect(() => {
    setChecked(!!(props.value || props.schema.default));
  }, [props.value]);

  const onChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setChecked(event.target.checked);
    props.onChange(event.target.checked);
  };

  const control =
    "widget" in props.schema && props.schema.widget === "switch" ? (
      <Switch checked={checked} onChange={onChange} />
    ) : (
      <Checkbox checked={checked} onChange={onChange} />
    );

  return (
    <FormControl fullWidth>
      <FormGroup>
        <FormControlLabel
          control={control}
          label={
            <MarkdownDiv markdown={props.label || ""} isRenderInline={true} />
          }
        />
      </FormGroup>
    </FormControl>
  );
};

export default SwitchWidget;
