import React from "react";
import {
  Autocomplete,
  Checkbox,
  Chip,
  FormControl,
  FormControlLabel,
  FormGroup,
  FormLabel,
  TextField,
} from "@mui/material";
import MarkdownDiv from "../Common/MarkdownDiv";
import { WidgetProps } from "@rjsf/utils";

interface MultipleInput {
  widget: WidgetProps;
  data: any;
  useCheckbox: boolean;
  whitelist: string[];
}

const MultipleInput = (props: MultipleInput) => {
  const [value, setValue] = React.useState<unknown[]>([]);

  React.useEffect(() => {
    if (props.data === value) return;
    if (props.data !== undefined && props.data !== null) {
      setValue(props.data);
    }
  }, [props.data]);

  const _setValue = (newValue: unknown[]) => {
    setValue(newValue);
    props.widget.onChange(newValue);
  };

  if (props.useCheckbox) {
    return (
      <FormControl>
        <FormLabel>
          <MarkdownDiv
            markdown={
              props.widget.label ||
              props.widget.schema.title ||
              props.widget.name
            }
          />
        </FormLabel>
        <FormGroup row>
          {props.whitelist.map((item, index) => (
            <FormControlLabel
              key={index}
              control={
                <Checkbox
                  checked={value.includes(item)}
                  onChange={(event) => {
                    if (event.target.checked) {
                      _setValue([...value, item]);
                    } else {
                      _setValue(value.filter((v) => v !== item));
                    }
                  }}
                />
              }
              label={item}
            />
          ))}
        </FormGroup>
      </FormControl>
    );
  }

  return (
    <Autocomplete
      multiple
      disableClearable
      size="small"
      value={value}
      options={props.whitelist}
      getOptionLabel={(option) => (option as any).toString()}
      disableCloseOnSelect
      onChange={(_event, newValue) => _setValue(newValue)}
      renderInput={(params) => (
        <TextField
          {...params}
          placeholder={props.widget.placeholder}
          label={
            <MarkdownDiv
              markdown={
                props.widget.label ||
                props.widget.schema.title ||
                props.widget.name
              }
            />
          }
          fullWidth
          required={props.widget.required}
          disabled={props.widget.disabled || props.widget.readonly}
        />
      )}
      renderTags={(value, getTagProps) => {
        return value.map((option: any, index) => (
          <Chip
            size="small"
            variant="outlined"
            label={option}
            {...getTagProps({ index })}
          />
        ));
      }}
    />
  );
};

export default MultipleInput;
