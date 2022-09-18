import { SheetInterface } from "./SheetInterface";
import React from "react";
import {
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
} from "@mui/material";

export default function SheetCheckBox(props: SheetInterface) {
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
            <Checkbox
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
