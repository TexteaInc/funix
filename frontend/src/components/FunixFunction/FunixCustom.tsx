import { Checkbox, Rating, Slider, Switch, TextField } from "@mui/material";
import React from "react";
import { WidgetProps } from "@rjsf/utils";

export interface FunixCustomProps {
  component: string;
  props: null | Record<string, any>;
  widget: WidgetProps;
}

const FunixCustom: React.FC<FunixCustomProps> = (props) => {
  const [value, setValue] = React.useState<any>();
  switch (props.component) {
    case "@mui/material/TextField":
      return (
        <TextField
          {...props.props}
          value={value}
          onChange={(event) => {
            setValue(event.target.value);
            props.widget.onChange(event.target.value);
          }}
        />
      );
    case "@mui/material/Switch":
      return (
        <Switch
          {...props.props}
          checked={value}
          onChange={(event) => {
            setValue(event.target.checked);
            props.widget.onChange(event.target.checked);
          }}
        />
      );
    case "@mui/material/Checkbox":
      return (
        <Checkbox
          {...props.props}
          checked={value}
          onChange={(event) => {
            setValue(event.target.checked);
            props.widget.onChange(event.target.checked);
          }}
        />
      );
    case "@mui/material/Slider":
      return (
        <Slider
          {...props.props}
          value={value}
          onChange={(_event, value) => {
            setValue(value);
            props.widget.onChange(value);
          }}
        />
      );
    case "@mui/material/Rating":
      return (
        <Rating
          {...props.props}
          value={value}
          onChange={(_event, value) => {
            setValue(value);
            props.widget.onChange(value);
          }}
        />
      );
    default:
      return <div>Unknown component: {props.component}</div>;
  }
};

export default FunixCustom;
