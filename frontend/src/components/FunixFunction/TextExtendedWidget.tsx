// Extended from TextWidget
// Ref: https://github.com/rjsf-team/react-jsonschema-form/blob/4049011ea59737232a86c193d96131ce61be85fa/packages/material-ui/src/TextWidget/TextWidget.tsx

import React from "react";
import { WidgetProps, utils } from "@rjsf/core";
import {
  Autocomplete,
  AutocompleteRenderInputParams,
  FormControl,
  FormControlLabel,
  FormLabel,
  Grid,
  Input,
  Radio,
  RadioGroup,
  Slider,
  TextField,
} from "@mui/material";
import SliderValueLabel from "../Common/SliderValueLabel";
import { sliderWidgetParser } from "../Common/SliderWidgetParser";
import { castValue } from "../Common/ValueOperation";
import MarkdownDiv from "../Common/MarkdownDiv";

const { getDisplayLabel } = utils;

const TextExtendedWidget = ({
  id,
  placeholder,
  required,
  readonly,
  disabled,
  type,
  label,
  value,
  onChange,
  onBlur,
  onFocus,
  autofocus,
  schema,
  uiSchema,
  rawErrors = [],
  registry,
}: WidgetProps) => {
  const rawSchema: any = schema;
  if (
    schema.widget?.indexOf("slider") !== -1 &&
    schema.widget !== undefined &&
    (schema.type === "number" || schema.type === "integer") // slider only for float and integer
  ) {
    const args = sliderWidgetParser(schema.widget);
    const min = args[0] || 0;
    const max = args[1] || 100;
    const defaultStep = schema.type === "integer" ? 1 : 0.1;
    const step = args[2] || defaultStep;

    const [sliderValue, setSliderValue] = React.useState<
      number | string | Array<number | string>
    >(value || min);

    const customSetSliderValue = (
      value: number | string | Array<number | string>
    ) => {
      setSliderValue(value);
      onChange(value);
    };

    const handleSliderChange = (event: Event, newValue: number | number[]) =>
      customSetSliderValue(newValue);

    const handleSliderInputChange = (
      event: React.ChangeEvent<HTMLInputElement>
    ) => {
      customSetSliderValue(
        event.target.value === ""
          ? ""
          : schema.type === "integer"
          ? parseInt(event.target.value)
          : parseFloat(event.target.value)
      );
    };

    const handleSliderInputBlur = () => {
      if (sliderValue < min) {
        customSetSliderValue(min);
      } else if (sliderValue > max) {
        customSetSliderValue(max);
      }
    };

    return (
      <FormControl fullWidth>
        <Grid container spacing={2} alignItems="center">
          {!!label ? (
            <Grid item>
              <MarkdownDiv
                markdown={label || schema.title}
                isRenderInline={true}
              />
            </Grid>
          ) : null}
          <Grid item xs>
            <Slider
              value={typeof sliderValue === "number" ? sliderValue : min}
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
          <Grid item xs={2.5}>
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

  if (schema.widget === "radio" && "whitelist" in rawSchema) {
    const [value, setValue] = React.useState<string>(
      schema.default ? `${schema.default}` : ""
    );

    const _onChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      setValue(event.target.value);
      onChange(event.target.value);
    };

    return (
      <FormControl>
        <FormLabel>
          <MarkdownDiv markdown={label || schema.title} isRenderInline={true} />
        </FormLabel>
        <RadioGroup value={value} onChange={_onChange} row>
          {(rawSchema.whitelist as string[]).map(
            (item: string, index: number) => (
              <FormControlLabel
                key={index}
                value={item}
                label={item}
                control={<Radio />}
              />
            )
          )}
        </RadioGroup>
      </FormControl>
    );
  }

  const [inputValue, setInputValue] = React.useState<
    string | number | boolean | object | null | undefined
  >(value || value === 0 ? value : "");

  const _onValueChange = (rawValue: any) => {
    const castedValue = castValue(rawValue, inputType);
    setInputValue(castValue);
    return onChange(castedValue);
  };
  const _onBlur = ({ target: { value } }: React.FocusEvent<HTMLInputElement>) =>
    onBlur(id, value);
  const _onFocus = ({
    target: { value },
  }: React.FocusEvent<HTMLInputElement>) => onFocus(id, value);

  const { rootSchema } = registry;
  const displayLabel = getDisplayLabel(schema, uiSchema, rootSchema);
  const inputType =
    (type || schema.type) === "string" ? "text" : `${type || schema.type}`;
  const enum ContentPolicy {
    Free,
    Example,
    Whitelist,
  }
  const contentPolicy: ContentPolicy = rawSchema["whitelist"]
    ? ContentPolicy.Whitelist
    : rawSchema["example"]
    ? ContentPolicy.Example
    : ContentPolicy.Free;
  const autocompleteOptions =
    contentPolicy == ContentPolicy.Whitelist
      ? rawSchema["whitelist"]
      : contentPolicy == ContentPolicy.Example
      ? rawSchema["example"]
      : [];
  const freeSolo: boolean = contentPolicy != ContentPolicy.Whitelist;

  return (
    <Autocomplete
      disableClearable={inputType === "number" || inputType === "integer"}
      size="small"
      value={value || value === 0 ? value : ""}
      getOptionLabel={(option) => option.toString()}
      renderInput={(params: AutocompleteRenderInputParams) => (
        <TextField
          multiline={schema.widget === "textarea"}
          maxRows={schema.widget === "textarea" ? 5 : 1}
          {...params}
          id={id}
          placeholder={placeholder}
          label={
            displayLabel ? (
              <MarkdownDiv
                markdown={schema.title || label || "input"}
                isRenderInline={true}
              />
            ) : null
          }
          autoFocus={autofocus}
          required={required}
          disabled={disabled || readonly}
          type={
            inputType === "number" || inputType === "integer"
              ? "number"
              : "text"
          }
          value={inputValue}
          error={rawErrors.length > 0}
          onBlur={_onBlur}
          onFocus={_onFocus}
          onChange={({
            target: { value },
          }: React.ChangeEvent<HTMLInputElement>) => {
            if (freeSolo) return _onValueChange(value);
          }}
          InputLabelProps={{ required: false }}
        />
      )}
      freeSolo={freeSolo}
      options={autocompleteOptions}
      onChange={(_, value) => _onValueChange(value)}
    />
  );
};

export default TextExtendedWidget;
