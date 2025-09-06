import { Checkbox, Rating, Slider, Switch, TextField } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { WidgetProps } from "@rjsf/utils";

export interface FunixCustomProps {
  component: string;
  props: null | Record<string, any>;
  widget: WidgetProps;
}

const FunixCustom: React.FC<FunixCustomProps> = React.memo((props) => {
  const [value, setValue] = useState<any>(
    props.widget.value ?? props.widget.formData ?? undefined,
  );

  useEffect(() => {
    const newValue = props.widget.value ?? props.widget.formData;
    if (newValue !== value) {
      setValue(newValue);
    }
  }, [props.widget.value, props.widget.formData]);

  const handleTextFieldChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = event.target.value;
      setValue(newValue);
      props.widget.onChange(newValue);
    },
    [props.widget],
  );

  const handleBooleanChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = event.target.checked;
      setValue(newValue);
      props.widget.onChange(newValue);
    },
    [props.widget],
  );

  const handleSliderChange = useCallback(
    (_event: Event, newValue: number | number[]) => {
      setValue(newValue);
      props.widget.onChange(newValue);
    },
    [props.widget],
  );

  const handleRatingChange = useCallback(
    (_event: React.SyntheticEvent, newValue: number | null) => {
      setValue(newValue);
      props.widget.onChange(newValue);
    },
    [props.widget],
  );

  switch (props.component) {
    case "@mui/material/TextField":
      return (
        <TextField
          {...props.props}
          value={value ?? ""}
          onChange={handleTextFieldChange}
        />
      );
    case "@mui/material/Switch":
      return (
        <Switch
          {...props.props}
          checked={Boolean(value)}
          onChange={handleBooleanChange}
        />
      );
    case "@mui/material/Checkbox":
      return (
        <Checkbox
          {...props.props}
          checked={Boolean(value)}
          onChange={handleBooleanChange}
        />
      );
    case "@mui/material/Slider":
      return (
        <Slider
          {...props.props}
          value={value ?? 0}
          onChange={handleSliderChange}
        />
      );
    case "@mui/material/Rating":
      return (
        <Rating
          {...props.props}
          value={value ?? null}
          onChange={handleRatingChange}
        />
      );
    default:
      return <div>Unknown component: {props.component}</div>;
  }
});

FunixCustom.displayName = "FunixCustom";

export default FunixCustom;
