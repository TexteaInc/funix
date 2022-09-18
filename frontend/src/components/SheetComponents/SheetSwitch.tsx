import { SheetInterface } from "./SheetInterface";
import React from "react";
import {
  FormControl,
  FormControlLabel,
  FormGroup,
  Switch,
} from "@mui/material";

export default function SheetSwitch(props: SheetInterface) {
  const [checked, setChecked] = React.useState<boolean>(props.params.value);

  const onChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setChecked(event.target.checked);
    props.customChange(
      props.params.row.id,
      props.params.field,
      event.target.checked
    );
  };

  return (
    <FormControl fullWidth>
      <FormGroup>
        <FormControlLabel
          control={
            <Switch
              checked={checked}
              onChange={onChange}
              sx={{ margin: "0 auto" }}
            />
          }
          label={""}
          sx={{ width: "100%", margin: "0 auto" }}
        />
      </FormGroup>
    </FormControl>
  );
}
