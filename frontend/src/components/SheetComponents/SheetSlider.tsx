import { SheetInterface } from "./SheetInterface";
import React, { useEffect } from "react";
import { FormControl, Grid, Input, Slider } from "@mui/material";
import SliderValueLabel from "../Common/SliderValueLabel";

export default function SheetSlider(
  props: SheetInterface & {
    min: number;
    max: number;
    step: number;
  },
) {
  const [value, setValue] = React.useState<
    number | string | Array<number | string>
  >(props.params.value === undefined ? props.min : props.params.value);

  useEffect(() => {
    setValue(props.params.value === undefined ? props.min : props.params.value);
  }, [props.params.value]);

  const customSetValue = (value: number | string | Array<number | string>) => {
    setValue(value);
    props.customChange(props.params.row.id, props.params.field, value);
  };

  const handleSliderChange = (_event: Event, newValue: number | number[]) =>
    customSetValue(newValue);

  const handleSliderInputChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    customSetValue(
      event.target.value === ""
        ? ""
        : props.type === "integer"
          ? parseInt(event.target.value)
          : parseFloat(event.target.value),
    );
  };

  const handleSliderInputBlur = () => {
    if (Array.isArray(value)) {
      const newValue = (value as Array<number | string>).map((v) => {
        const value =
          typeof v === "number"
            ? v
            : props.type === "integer"
              ? parseInt(v)
              : parseFloat(v);
        if (value < props.min) {
          return props.min;
        } else if (value > props.max) {
          return props.max;
        }
        return value;
      });
      customSetValue(newValue);
    } else {
      const newValue =
        typeof value === "number"
          ? value
          : props.type === "integer"
            ? parseInt(value)
            : parseFloat(value);
      if (newValue < props.min) {
        customSetValue(props.min);
      } else if (newValue > props.max) {
        customSetValue(props.max);
      }
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
            value={
              typeof value === "number"
                ? value
                : typeof value === "string"
                  ? props.type === "integer"
                    ? parseInt(value)
                    : parseFloat(value)
                  : props.min
            }
            min={props.min}
            max={props.max}
            step={props.step}
            onChange={handleSliderChange}
            valueLabelDisplay="on"
            slots={{
              valueLabel: SliderValueLabel,
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
