import { WidgetProps } from "@rjsf/core";
import {
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  Switch,
} from "@mui/material";
import React from "react";

const SwitchWidget = (prop: WidgetProps | any) => {
  const [checked, setChecked] = React.useState<boolean>(!!prop.schema.default);

  const _onValueChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setChecked(event.target.checked);
    prop.onChange(event.target.checked);
  };

  let control = <Checkbox checked={checked} onChange={_onValueChange} />;

  if (prop.schema.hasOwnProperty("widget") && prop.schema.widget === "switch") {
    control = <Switch checked={checked} onChange={_onValueChange} />;
  }
  return (
    <FormControl fullWidth>
      <FormGroup>
        <FormControlLabel control={control} label={prop.label || ""} />
      </FormGroup>
    </FormControl>
  );
};

export default SwitchWidget;
