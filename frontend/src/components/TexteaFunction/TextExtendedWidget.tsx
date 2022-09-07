// Extended from TextWidget
// Ref: https://github.com/rjsf-team/react-jsonschema-form/blob/4049011ea59737232a86c193d96131ce61be85fa/packages/material-ui/src/TextWidget/TextWidget.tsx

import React from "react";
import { WidgetProps, utils } from "@rjsf/core";
import {
  Autocomplete,
  AutocompleteRenderInputParams,
  TextField,
} from "@mui/material";

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
  options,
  schema,
  uiSchema,
  rawErrors = [],
  registry,
}: WidgetProps) => {
  const _onValueChange = (rawValue: any) => {
    let value;
    switch (inputType) {
      case "text":
        value = rawValue;
        break;
      case "number":
        const parsedFloat = parseFloat(rawValue);
        if (!isNaN(parsedFloat) && isFinite(parsedFloat)) value = parsedFloat;
        else value = 0;
        break;
      case "integer":
        const parsedInt = parseInt(rawValue);
        if (!isNaN(parsedInt) && isFinite(parsedInt)) value = parsedInt;
        else value = 0;
        break;
      case "boolean":
        if (rawValue in ["True", "true"]) value = true;
        else if (rawValue in ["False", "false"]) value = false;
        value = rawValue;
        break;
      default:
        console.log("Unknown input type, treat as text");
        value = rawValue;
        break;
    }
    return onChange(value === "" ? options.emptyValue : value);
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
  const rawSchema: any = schema;
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
      size="small"
      value={value || value === 0 ? value : ""}
      getOptionLabel={(option) => option.toString()}
      renderInput={(params: AutocompleteRenderInputParams) => (
        <TextField
          {...params}
          id={id}
          placeholder={placeholder}
          label={displayLabel ? label || schema.title : false}
          autoFocus={autofocus}
          required={required}
          disabled={disabled || readonly}
          type={inputType as string}
          value={value || value === 0 ? value : ""}
          error={rawErrors.length > 0}
          onBlur={_onBlur}
          onFocus={_onFocus}
          onChange={({
            target: { value },
          }: React.ChangeEvent<HTMLInputElement>) => {
            if (freeSolo) return _onValueChange(value);
          }}
        />
      )}
      freeSolo={freeSolo}
      options={autocompleteOptions}
      onChange={(_, value) => _onValueChange(value)}
    />
  );
};

export default TextExtendedWidget;
