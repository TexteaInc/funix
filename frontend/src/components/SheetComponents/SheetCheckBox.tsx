import { SheetInterface } from "./SheetInterface";
import React, { useEffect } from "react";
import {
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  Switch,
} from "@mui/material";

export default function SheetCheckBox(
  props: SheetInterface & { isSwitch: boolean },
) {
  const [checked, setChecked] = React.useState<boolean>(props.params.value);

  useEffect(() => {
    setChecked(props.params.value);
  }, [props.params.value]);

  const onChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setChecked(event.target.checked);
    props.customChange(
      props.params.row.id,
      props.params.field,
      event.target.checked,
    );
  };

  const controlElement = props.isSwitch ? (
    <Switch checked={checked} onChange={onChange} sx={{ margin: "0 auto" }} />
  ) : (
    <Checkbox checked={checked} onChange={onChange} sx={{ margin: "0 auto" }} />
  );

  return (
    <FormControl fullWidth>
      <FormGroup>
        <FormControlLabel
          control={controlElement}
          label={""}
          sx={{ width: "100%", margin: "0 auto" }}
        />
      </FormGroup>
    </FormControl>
  );
}
