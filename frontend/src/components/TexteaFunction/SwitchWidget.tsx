import { WidgetProps } from "@rjsf/core";
import {
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  Switch,
} from "@mui/material";
import React from "react";
import { JSONSchema7 } from "json-schema";

interface WithWidgetJSONSchema7 extends JSONSchema7 {
  widget?: string; // fix TS2339: Property 'widget' does not exist on type 'JSONSchema7'
}

const SwitchWidget = (props: WidgetProps) => {
  const [checked, setChecked] = React.useState<boolean>(!!props.schema.default);

  const onChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setChecked(event.target.checked);
    props.onChange(event.target.checked);
  };

  let control = <Checkbox checked={checked} onChange={onChange} />;

  if (
    "widget" in props.schema &&
    (props.schema as WithWidgetJSONSchema7).widget === "switch"
  ) {
    control = <Switch checked={checked} onChange={onChange} />;
  }
  return (
    <FormControl fullWidth>
      <FormGroup>
        <FormControlLabel control={control} label={props.label || ""} />
      </FormGroup>
    </FormControl>
  );
};

export default SwitchWidget;
