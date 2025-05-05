// Extended from TextWidget
// Ref: https://github.com/rjsf-team/react-jsonschema-form/blob/4049011ea59737232a86c193d96131ce61be85fa/packages/material-ui/src/TextWidget/TextWidget.tsx

import React, { useEffect } from "react";
import {
  Autocomplete,
  AutocompleteRenderInputParams,
  FormControl,
  FormControlLabel,
  FormLabel,
  Grid,
  IconButton,
  Input,
  InputAdornment,
  Radio,
  RadioGroup,
  Slider,
  TextField,
  useTheme,
} from "@mui/material";
import SliderValueLabel from "../Common/SliderValueLabel";
import {
  sliderWidgetParser,
  textareaWidgetParser,
} from "../Common/WidgetSyntaxParser";
import { castValue } from "../Common/ValueOperation";
import MarkdownDiv from "../Common/MarkdownDiv";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import Editor from "@monaco-editor/react";
import { getDisplayLabel, WidgetProps } from "@rjsf/utils";
import validator from "@rjsf/validator-ajv8";

type MultilineProps = {
  multiline?: boolean;
  rows?: number;
  maxRows?: number;
  minRows?: number;
};

const unique = (arr: any[]) => [...new Set(arr)];

const TextExtendedWidget = ({
  id,
  name,
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
  formContext,
}: WidgetProps) => {
  const rawSchema: any = schema;
  const advancedExamples: Record<string, any>[] | null =
    formContext.advancedExamples;

  const [availableExamples, setAvailableExamples] = React.useState<string[]>(
    advancedExamples === null
      ? []
      : unique(
          advancedExamples
            .filter((example) => {
              return name in example;
            })
            .map((example) => example[name]),
        ),
  );

  useEffect(() => {
    if (advancedExamples !== null) {
      const fromKeys = Object.keys(formContext.form);
      setAvailableExamples(
        unique(
          advancedExamples
            .filter((example) => {
              for (const key of fromKeys) {
                if (!(key in example)) {
                  return false;
                }
                if (
                  example[key] !== formContext.form[key] &&
                  key !== name &&
                  formContext.form[key] !== ""
                ) {
                  return false;
                }
              }
              return true;
            })
            .filter((example) => {
              return name in example;
            })
            .map((example) => example[name]),
        ),
      );
    }
  }, [formContext]);

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
    >(value === undefined ? min : value);

    useEffect(() => {
      if (value === sliderValue) return;
      setSliderValue(value === undefined ? min : value);
    }, [value]);

    const customSetSliderValue = (
      value: number | string | Array<number | string>,
    ) => {
      setSliderValue(value);
      onChange(value);
    };

    const handleSliderChange = (_event: Event, newValue: number | number[]) =>
      customSetSliderValue(newValue);

    const handleSliderInputChange = (
      event: React.ChangeEvent<HTMLInputElement>,
    ) => {
      customSetSliderValue(
        event.target.value === ""
          ? ""
          : schema.type === "integer"
            ? parseInt(event.target.value)
            : parseFloat(event.target.value),
      );
    };

    const handleSliderInputBlur = () => {
      if (Array.isArray(sliderValue)) {
        const newValue = (sliderValue as Array<number | string>).map((v) => {
          const value =
            typeof v === "number"
              ? v
              : schema.type === "integer"
                ? parseInt(v)
                : parseFloat(v);
          if (value < min) {
            return min;
          } else if (value > max) {
            return max;
          }
          return value;
        });
        customSetSliderValue(newValue);
      } else {
        const newValue =
          typeof sliderValue === "number"
            ? sliderValue
            : schema.type === "integer"
              ? parseInt(sliderValue)
              : parseFloat(sliderValue);
        if (newValue < min) {
          customSetSliderValue(min);
        } else if (newValue > max) {
          customSetSliderValue(max);
        }
      }
    };

    return (
      <FormControl fullWidth>
        <Grid container spacing={2} alignItems="center">
          {label ? (
            <Grid item>
              <MarkdownDiv
                markdown={label || schema.title || ""}
                isRenderInline={true}
              />
            </Grid>
          ) : null}
          <Grid item xs>
            <Slider
              value={
                typeof sliderValue === "number"
                  ? sliderValue
                  : typeof sliderValue === "string"
                    ? schema.type === "integer"
                      ? parseInt(sliderValue)
                      : parseFloat(sliderValue)
                    : min
              }
              min={min}
              max={max}
              step={step}
              onChange={handleSliderChange}
              valueLabelDisplay="on"
              slots={{
                valueLabel: SliderValueLabel,
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

  if (
    schema.widget?.indexOf("code") !== -1 &&
    schema.widget !== undefined &&
    schema.type === "string"
  ) {
    const [src, setSrc] = React.useState<string>(schema.default || value);
    const [height, setHeight] = React.useState(450);
    const theme = useTheme();

    useEffect(() => {
      if (value === src) return;
      setSrc(schema.default || value);
    }, [value]);

    let language = "plaintext";

    if (
      schema.widget.indexOf("[") !== -1 &&
      schema.widget.indexOf("]") !== -1
    ) {
      language = schema.widget
        .split("[")[1]
        .split("]")[0]
        .trim()
        .replaceAll('"', "");
    }

    return (
      <Editor
        width="100%"
        height={height}
        value={src}
        language={language}
        options={{
          minimap: {
            enabled: false,
          },
        }}
        theme={theme.palette.mode === "dark" ? "vs-dark" : "light"}
        onMount={(editor) => {
          editor.onDidChangeModelContent(() => {
            setHeight(
              Math.max(450, editor.getModel().getLineCount() * 20 + 20),
            );
          });
        }}
        onChange={(value) => {
          if (value) {
            setSrc(value);
            onChange(value);
          } else {
            setSrc("");
            onChange("");
          }
        }}
      />
    );
  }

  if (schema.widget === "radio" && "whitelist" in rawSchema) {
    const [radioValue, setRadioValue] = React.useState<string>(
      value === undefined
        ? schema.default
          ? `${schema.default}`
          : ""
        : `${value}`,
    );

    useEffect(() => {
      if (value === radioValue) return;
      setRadioValue(
        value === undefined
          ? schema.default
            ? `${schema.default}`
            : ""
          : `${value}`,
      );
    }, [value]);

    const _onChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      setRadioValue(event.target.value);
      onChange(event.target.value);
    };

    return (
      <FormControl>
        <FormLabel>
          <MarkdownDiv markdown={label || schema.title} isRenderInline={true} />
        </FormLabel>
        <RadioGroup value={radioValue} onChange={_onChange} row>
          {(rawSchema.whitelist as string[]).map(
            (item: string, index: number) => (
              <FormControlLabel
                key={index}
                value={item}
                label={item}
                control={<Radio />}
              />
            ),
          )}
        </RadioGroup>
      </FormControl>
    );
  }

  const [inputValue, setInputValue] = React.useState<
    string | number | boolean | object | null | undefined
  >(value || value === 0 ? value : "");
  const [showPassword, setShowPassword] = React.useState(false);

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
  const displayLabel = getDisplayLabel(validator, schema, uiSchema, rootSchema);
  const inputType =
    (type || schema.type) === "string" ? "text" : `${type || schema.type}`;
  const enum ContentPolicy {
    Free,
    Example,
    Whitelist,
    AdvancedExamples = 3,
  }
  const contentPolicy: ContentPolicy = formContext.advancedExamples
    ? ContentPolicy.AdvancedExamples
    : rawSchema["whitelist"]
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

  const multilineConfig: MultilineProps = {};
  multilineConfig.multiline = true;

  if (schema.widget) {
    const widget = schema.widget;

    if (schema.widget.indexOf("textarea") !== -1) {
      const parseResult = textareaWidgetParser(widget);

      if (parseResult === "default") {
        multilineConfig.rows = 5;
      } else if (parseResult.length === 1) {
        multilineConfig.rows = parseResult[0];
      } else if (parseResult.length === 2) {
        multilineConfig.minRows = parseResult[0];
        multilineConfig.maxRows = parseResult[1];
      } else {
        console.warn("Invalid widget syntax for textarea");
        multilineConfig.rows = parseResult[0];
      }
    } else {
      multilineConfig.multiline = false;
    }
  }

  if (inputType === "number" || inputType === "integer") {
    multilineConfig.multiline = false;
  }

  if (
    autocompleteOptions.length === 0 &&
    contentPolicy != ContentPolicy.AdvancedExamples
  ) {
    return (
      <TextField
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
        fullWidth
        autoFocus={autofocus}
        required={required}
        disabled={disabled || readonly}
        type={
          inputType === "number" || inputType === "integer"
            ? "Number"
            : schema.widget === "password"
              ? showPassword
                ? "text"
                : "password"
              : "text"
        }
        value={value || value === 0 ? value : ""}
        error={rawErrors.length > 0}
        onBlur={_onBlur}
        onFocus={_onFocus}
        onChange={({
          target: { value },
        }: React.ChangeEvent<HTMLInputElement>) => {
          _onValueChange(value);
        }}
        InputLabelProps={{
          required: false,
        }}
        {...multilineConfig}
        size="small"
        inputProps={{
          style: {
            resize:
              schema.widget !== "password" &&
              inputType !== "number" &&
              inputType !== "integer"
                ? "vertical"
                : "none",
          },
        }}
        InputProps={{
          endAdornment:
            schema.widget === "password" ? (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setShowPassword((show) => !show)}
                  onMouseDown={(e) => e.preventDefault()}
                  edge="end"
                  sx={{
                    m: 0,
                  }}
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ) : (
              <></>
            ),
        }}
      />
    );
  }

  return (
    <Autocomplete
      disableClearable
      size="small"
      value={value || value === 0 ? value : ""}
      getOptionLabel={(option) => option.toString()}
      renderInput={(params: AutocompleteRenderInputParams) => {
        const newParams = params;
        if (schema.widget === "password") {
          newParams.InputProps.endAdornment = (
            <>
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setShowPassword((show) => !show)}
                  onMouseDown={(e) => e.preventDefault()}
                  edge="end"
                  sx={{
                    m: 0,
                  }}
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            </>
          );
        }
        return (
          <TextField
            {...multilineConfig}
            {...newParams}
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
            fullWidth
            autoFocus={autofocus}
            required={required}
            disabled={disabled || readonly}
            type={
              inputType === "number" || inputType === "integer"
                ? "Number"
                : schema.widget === "password"
                  ? showPassword
                    ? "text"
                    : "password"
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
            InputLabelProps={{
              required: false,
            }}
          />
        );
      }}
      freeSolo={freeSolo}
      options={
        contentPolicy == ContentPolicy.AdvancedExamples
          ? availableExamples
          : autocompleteOptions
      }
      onChange={(_, value) => _onValueChange(value)}
    />
  );
};

export default TextExtendedWidget;
