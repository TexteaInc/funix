import { SheetInterface } from "./SheetInterface";
import React from "react";
import { FormControl, Grid, Input, Slider } from "@mui/material";
import SliderValueLabel from "../Common/SliderValueLabel";

export default function SheetSlider(
  props: SheetInterface & {
    min: number;
    max: number;
    step: number;
  }
) {
  const [value, setValue] = React.useState<
    number | string | Array<number | string>
  >(props.params.value | props.min);

  const customSetValue = (value: number | string | Array<number | string>) => {
    setValue(value);
    props.customChange(props.params.row.id, props.params.field, value);
  };

  const handleSliderChange = (event: Event, newValue: number | number[]) =>
    customSetValue(newValue);

  const handleSliderInputChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    customSetValue(
      event.target.value === ""
        ? ""
        : props.type === "integer"
        ? parseInt(event.target.value)
        : parseFloat(event.target.value)
    );
  };

  const handleSliderInputBlur = () => {
    if (value < props.min) {
      customSetValue(props.min);
    } else if (value > props.max) {
      customSetValue(props.max);
    }
  };

  return (
    <FormControl fullWidth>
      <Grid
        container
        spacing={2}
        alignItems="center"
        sx={{ paddingX: 2, marginTop: "-5%" }}
      >
        <Grid item xs>
          <Slider
            value={typeof value === "number" ? value : props.min}
            min={props.min}
            max={props.max}
            step={props.step}
            onChange={handleSliderChange}
            valueLabelDisplay="on"
            components={{
              ValueLabel: SliderValueLabel,
            }}
          />
        </Grid>
        <Grid item sx={{ maxWidth: "40%" }}>
          <Input
            value={value}
            size="small"
            inputProps={{
              type: "number",
              min: props.min,
              max: props.max,
              step: props.step,
            }}
            onChange={handleSliderInputChange}
            onBlur={handleSliderInputBlur}
          />
        </Grid>
      </Grid>
    </FormControl>
  );
}
