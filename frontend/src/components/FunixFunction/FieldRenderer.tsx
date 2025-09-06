import { ReactElement } from "react";
import JSONEditorWidget from "./JSONEditorWidget";
import FileUploadWidget from "./FileUploadWidget";
import DateTimePickerWidget from "./DateTimePickerWidget";
import FunixCustom from "./FunixCustom";
import MultipleInput from "./MultipleInput";
import TextExtendedWidget from "./TextExtendedWidget";
import SwitchWidget from "./SwitchWidget";

export const FILE_TYPES = ["image", "video", "audio", "file"];

export interface FieldRenderOptions {
  fieldSchema: any;
  fieldValue: any;
  fieldProps: any;
  onChange?: (value: any) => void;
  isMultiple?: boolean;
}

export const renderJSONField = (
  fieldProps: any,
  fieldSchema: any,
  fieldValue: any,
  isArray: boolean = false,
): ReactElement => {
  return (
    <JSONEditorWidget
      widget={fieldProps}
      checkType={isArray ? fieldSchema.items?.type || "DO_NOT_CHECK" : ""}
      keys={!isArray ? fieldSchema.keys : undefined}
      data={fieldValue}
    />
  );
};

export const renderFileUploadField = (
  fieldProps: any,
  fieldSchema: any,
  fieldValue: any,
  isMultiple: boolean = false,
): ReactElement => {
  const supportType = isMultiple
    ? fieldSchema.items?.widget
    : fieldSchema.widget;

  return (
    <FileUploadWidget
      widget={fieldProps}
      multiple={isMultiple}
      supportType={supportType}
      data={fieldValue}
    />
  );
};

export const renderDateTimeField = (
  fieldProps: any,
  fieldValue: any,
): ReactElement => {
  return <DateTimePickerWidget widget={fieldProps} data={fieldValue} />;
};

export const renderCustomField = (
  fieldSchema: any,
  fieldProps: any,
): ReactElement => {
  const component = fieldSchema.funixComponent;
  const componentProps = fieldSchema.funixProps || null;

  return (
    <FunixCustom
      component={component}
      props={componentProps}
      widget={fieldProps}
    />
  );
};

export const renderMultipleInputField = (
  fieldProps: any,
  fieldSchema: any,
  fieldValue: any,
  useWhitelist: boolean = false,
): ReactElement => {
  return (
    <MultipleInput
      widget={fieldProps}
      data={fieldValue}
      useCheckbox={fieldSchema.widget === "checkbox"}
      acceptValues={
        useWhitelist ? fieldSchema.whitelist : fieldSchema.example || []
      }
      acceptNewValues={!useWhitelist}
    />
  );
};

export const renderBooleanField = (fieldProps: any): ReactElement => {
  return <SwitchWidget {...fieldProps} />;
};

export const renderTextField = (fieldProps: any): ReactElement => {
  return <TextExtendedWidget {...fieldProps} />;
};

export const renderField = (options: FieldRenderOptions): ReactElement => {
  const { fieldSchema, fieldValue, fieldProps } = options;

  if ("funixComponent" in fieldSchema) {
    return renderCustomField(fieldSchema, fieldProps);
  }

  if (fieldSchema.type === "array") {
    if (fieldSchema.widget === "json") {
      return renderJSONField(fieldProps, fieldSchema, fieldValue, true);
    } else if (FILE_TYPES.indexOf(fieldSchema.items?.widget) !== -1) {
      return renderFileUploadField(fieldProps, fieldSchema, fieldValue, true);
    } else if (fieldSchema.whitelist && Array.isArray(fieldSchema.whitelist)) {
      return renderMultipleInputField(
        fieldProps,
        fieldSchema,
        fieldValue,
        true,
      );
    } else {
      return renderMultipleInputField(
        fieldProps,
        fieldSchema,
        fieldValue,
        false,
      );
    }
  }

  if (fieldSchema.widget === "json") {
    return renderJSONField(fieldProps, fieldSchema, fieldValue, false);
  } else if (FILE_TYPES.indexOf(fieldSchema.widget) !== -1) {
    return renderFileUploadField(fieldProps, fieldSchema, fieldValue, false);
  } else if (fieldSchema.widget === "datetime") {
    return renderDateTimeField(fieldProps, fieldValue);
  } else if (fieldSchema.type === "boolean") {
    return renderBooleanField(fieldProps);
  } else {
    return renderTextField(fieldProps);
  }
};

export const isFileType = (widget: string): boolean => {
  return FILE_TYPES.indexOf(widget) !== -1;
};

export const createFieldProps = (
  baseProps: any,
  fieldSchema: any,
  fieldValue: any,
  onChange: (value: any) => void,
  fieldName: string,
) => {
  const enhancedSchema = {
    ...fieldSchema,
    default:
      fieldValue !== undefined
        ? fieldValue
        : fieldSchema.default !== undefined
          ? fieldSchema.default
          : "",
  };

  return {
    ...baseProps,
    schema: enhancedSchema,
    formData: fieldValue,
    onChange,
    name: fieldName,
    id: fieldName,
    value: fieldValue,
    label: fieldSchema.title || fieldName,
    required: !fieldSchema.optional,
  };
};
