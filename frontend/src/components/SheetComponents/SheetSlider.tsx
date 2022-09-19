import { SheetInterface } from "./SheetInterface";
import React from "react";
import { FormControl, Grid, Input, Slider } from "@mui/material";
import SliderValueLabel from "../Common/SliderValueLabel";
import { sliderWidgetParser } from "../Common/SliderWidgetParser";

export default function SheetSlider(props: SheetInterface) {
  const args = sliderWidgetParser(props.widget);

  const min = args[0] || 0;
  const max = args[1] || 100;
  const defaultStep = props.type === "integer" ? 1 : 0.1;
  const step = args[2] || defaultStep;

  const [value, setValue] = React.useState<
    number | string | Array<number | string>
  >(props.params.value | min);

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
    if (value < min) {
      customSetValue(min);
    } else if (value > max) {
      customSetValue(max);
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
            value={typeof value === "number" ? value : min}
            min={min}
            max={max}
            step={step}
            onChange={handleSliderChange}
            valueLabelDisplay="on"
            components={{
              ValueLabel: SliderValueLabel,
            }}
          />
        </Grid>
        <Grid item sx={{ maxWidth: "35%" }}>
          <Input
            value={value}
            size="small"
            inputProps={{
              type: "number",
              min: min,
              max: max,
              step: step,
            }}
            onChange={handleSliderInputChange}
            onBlur={handleSliderInputBlur}
          />
        </Grid>
      </Grid>
    </FormControl>
  );
}
