import { ReactElement, useState, useEffect } from "react";
import {
  Box,
  Divider,
  Stack,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Button,
  Typography,
} from "@mui/material";
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  KeyboardArrowUp as ArrowUpIcon,
  KeyboardArrowDown as ArrowDownIcon,
} from "@mui/icons-material";
import Grid2 from "@mui/material/Unstable_Grid2";
import MarkdownDiv from "../Common/MarkdownDiv";
import InnerHTML from "dangerously-set-html-content";
import FunixCustom from "./FunixCustom";
import JSONEditorWidget from "./JSONEditorWidget";
import FileUploadWidget from "./FileUploadWidget";
import MultipleInput from "./MultipleInput";
import DateTimePickerWidget from "./DateTimePickerWidget";
import SwitchWidget from "./SwitchWidget";
import TextExtendedWidget from "./TextExtendedWidget";

interface PyDanticPanelProps {
  rootContent: ReactElement;
  elementName?: string;
  arrayIndex?: number;
  onArrayMove?: (index: number, direction: "up" | "down") => void;
  onArrayDelete?: (index: number) => void;
  onArrayAdd?: () => void;
  showArrayControls?: boolean;
}

const PyDanticPanel = (props: PyDanticPanelProps) => {
  const rootContent = props.rootContent;
  const rootContentProps = rootContent.props;
  const rootContentSchema = rootContentProps.schema;
  const elementName = props.elementName || rootContentProps.name || "Object";

  const createDefaultValue = (schema: any): any => {
    if (schema.type === "array") {
      return schema.default || [];
    } else if (schema.type === "object") {
      const defaultObj: Record<string, any> = {};
      const properties = schema.items?.properties || schema.properties || {};

      Object.keys(properties).forEach((key) => {
        const prop = properties[key];
        if (prop.default !== undefined) {
          defaultObj[key] = prop.default;
        } else if (prop.type === "array") {
          defaultObj[key] = [];
        } else if (prop.type === "object") {
          defaultObj[key] = createDefaultValue(prop);
        } else if (prop.type === "boolean") {
          defaultObj[key] = false;
        } else if (prop.type === "number" || prop.type === "integer") {
          defaultObj[key] = 0;
        } else {
          defaultObj[key] = "";
        }
      });

      return schema.default || defaultObj;
    } else {
      return schema.default || "";
    }
  };

  const [pydanticForm, setPydanticForm] = useState<object | any[]>(() => {
    if (
      rootContentProps.formData !== undefined &&
      rootContentProps.formData !== null
    ) {
      return rootContentProps.formData;
    }
    if (rootContentSchema.default !== undefined) {
      return rootContentSchema.default;
    }
    return createDefaultValue(rootContentSchema);
  });

  useEffect(() => {
    const shouldInitialize =
      rootContentProps.formData === undefined ||
      rootContentProps.formData === null ||
      (Array.isArray(rootContentProps.formData) &&
        rootContentProps.formData.length === 0) ||
      (typeof rootContentProps.formData === "object" &&
        Object.keys(rootContentProps.formData).length === 0);

    if (shouldInitialize) {
      const defaultValue =
        rootContentSchema.default !== undefined
          ? rootContentSchema.default
          : createDefaultValue(rootContentSchema);

      setPydanticForm(defaultValue);

      if (rootContentProps.onChange) {
        rootContentProps.onChange(defaultValue);
      }
    }
  }, []);

  useEffect(() => {
    if (
      rootContentProps.formData !== undefined &&
      rootContentProps.formData !== null &&
      JSON.stringify(rootContentProps.formData) !== JSON.stringify(pydanticForm)
    ) {
      setPydanticForm(rootContentProps.formData);
    }
  }, [rootContentProps.formData]);

  const handleFieldChange = (fieldName: string, value: any) => {
    const newForm =
      rootContentSchema.type === "array"
        ? [...(pydanticForm as any[])]
        : { ...(pydanticForm as object) };
    (newForm as any)[fieldName] = value;
    setPydanticForm(newForm);
    if (rootContentProps.onChange) {
      rootContentProps.onChange(newForm);
    }
  };

  const handleArrayItemChange = (index: number, value: any) => {
    const newArray = [...(pydanticForm as any[])];
    newArray[index] = value;
    setPydanticForm(newArray);
    if (rootContentProps.onChange) {
      rootContentProps.onChange(newArray);
    }
  };

  const handleArrayAdd = () => {
    const newArray = [...(pydanticForm as any[])];
    const itemSchema = rootContentSchema.items;
    const defaultValue: Record<string, any> = {};

    if (itemSchema.properties) {
      Object.keys(itemSchema.properties).forEach((key) => {
        const prop = itemSchema.properties[key];
        if (prop.default !== undefined) {
          defaultValue[key] = prop.default;
        } else if (prop.type === "array") {
          defaultValue[key] = [];
        } else if (prop.type === "object") {
          defaultValue[key] = {};
        } else if (prop.type === "boolean") {
          defaultValue[key] = false;
        } else if (prop.type === "number" || prop.type === "integer") {
          defaultValue[key] = 0;
        } else {
          defaultValue[key] = "";
        }
      });
    }

    newArray.push(defaultValue);
    setPydanticForm(newArray);
    if (rootContentProps.onChange) {
      rootContentProps.onChange(newArray);
    }
  };

  const handleArrayDelete = (index: number) => {
    const newArray = [...(pydanticForm as any[])];
    newArray.splice(index, 1);
    setPydanticForm(newArray);
    if (rootContentProps.onChange) {
      rootContentProps.onChange(newArray);
    }
  };

  const handleArrayMove = (index: number, direction: "up" | "down") => {
    const newArray = [...(pydanticForm as any[])];
    const targetIndex = direction === "up" ? index - 1 : index + 1;

    if (targetIndex >= 0 && targetIndex < newArray.length) {
      [newArray[index], newArray[targetIndex]] = [
        newArray[targetIndex],
        newArray[index],
      ];
      setPydanticForm(newArray);
      if (rootContentProps.onChange) {
        rootContentProps.onChange(newArray);
      }
    }
  };

  const renderField = (fieldName: string, fieldSchema: any): ReactElement => {
    let fieldValue = (pydanticForm as any)?.[fieldName];

    if (fieldValue === undefined || fieldValue === null) {
      fieldValue = fieldSchema.default;
    }

    const filesType = ["image", "video", "audio", "file"];

    if (
      fieldSchema.widget === "__object_complex_pydantic" ||
      fieldSchema.widget === "__array_complex_pydantic"
    ) {
      const nestedProps = {
        ...rootContentProps,
        schema: fieldSchema,
        formData: fieldValue,
        onChange: (newValue: any) => handleFieldChange(fieldName, newValue),
        name: fieldName,
      };

      return (
        <PyDanticPanel
          rootContent={{
            ...rootContent,
            props: nestedProps,
          }}
          elementName={fieldSchema.title || fieldName}
        />
      );
    }

    if ("funixComponent" in fieldSchema) {
      const component = fieldSchema.funixComponent;
      const componentProps =
        "funixProps" in fieldSchema ? fieldSchema.funixProps : null;
      return (
        <FunixCustom
          component={component}
          props={componentProps}
          widget={{
            ...rootContentProps,
            schema: fieldSchema,
            formData: fieldValue,
            onChange: (newValue: any) => handleFieldChange(fieldName, newValue),
            name: fieldName,
          }}
        />
      );
    }

    const enhancedSchema = {
      ...fieldSchema,
      default:
        fieldValue !== undefined
          ? fieldValue
          : fieldSchema.default !== undefined
            ? fieldSchema.default
            : "",
    };

    const fieldProps = {
      ...rootContentProps,
      schema: enhancedSchema,
      formData: fieldValue,
      onChange: (newValue: any) => handleFieldChange(fieldName, newValue),
      name: fieldName,
      id: fieldName,
      value: fieldValue,
      label: fieldSchema.title || fieldName,
      required: !fieldSchema.optional,
    };

    if (fieldSchema.type === "array") {
      if (fieldSchema.widget === "json") {
        return (
          <JSONEditorWidget
            widget={fieldProps}
            checkType={fieldSchema.items?.type || "DO_NOT_CHECK"}
            data={fieldValue !== undefined ? fieldValue : fieldSchema.default}
          />
        );
      } else if (filesType.indexOf(fieldSchema.items?.widget) !== -1) {
        return (
          <FileUploadWidget
            widget={fieldProps}
            multiple={true}
            supportType={fieldSchema.items.widget}
            data={fieldValue !== undefined ? fieldValue : fieldSchema.default}
          />
        );
      } else if (
        fieldSchema.whitelist &&
        Array.isArray(fieldSchema.whitelist)
      ) {
        return (
          <MultipleInput
            widget={fieldProps}
            data={fieldValue !== undefined ? fieldValue : fieldSchema.default}
            useCheckbox={fieldSchema.widget === "checkbox"}
            acceptValues={fieldSchema.whitelist}
            acceptNewValues={false}
          />
        );
      } else {
        return (
          <MultipleInput
            widget={fieldProps}
            data={fieldValue !== undefined ? fieldValue : fieldSchema.default}
            useCheckbox={fieldSchema.widget === "checkbox"}
            acceptValues={fieldSchema.example || []}
            acceptNewValues={true}
          />
        );
      }
    } else {
      if (fieldSchema.widget === "json") {
        return (
          <JSONEditorWidget
            widget={fieldProps}
            checkType=""
            keys={fieldSchema.keys}
            data={fieldValue !== undefined ? fieldValue : fieldSchema.default}
          />
        );
      } else if (filesType.indexOf(fieldSchema.widget) !== -1) {
        return (
          <FileUploadWidget
            widget={fieldProps}
            multiple={false}
            supportType={fieldSchema.widget}
            data={fieldValue !== undefined ? fieldValue : fieldSchema.default}
          />
        );
      } else if (fieldSchema.widget === "datetime") {
        return (
          <DateTimePickerWidget
            widget={fieldProps}
            data={fieldValue !== undefined ? fieldValue : fieldSchema.default}
          />
        );
      } else if (fieldSchema.type === "boolean") {
        return <SwitchWidget {...fieldProps} />;
      } else {
        return <TextExtendedWidget {...fieldProps} />;
      }
    }
  };

  const renderArrayItem = (item: any, index: number): ReactElement => {
    const itemSchema = rootContentSchema.items;
    const itemProps = {
      ...rootContentProps,
      schema: itemSchema,
      formData: item,
      onChange: (newValue: any) => handleArrayItemChange(index, newValue),
      name: `${rootContentProps.name}[${index}]`,
    };

    const arrayLength = (pydanticForm as any[]).length;

    return (
      <Card key={index} variant="outlined" sx={{ mb: 2 }}>
        <CardHeader
          title={
            <Typography variant="subtitle2">
              {itemSchema.title || `Item ${index + 1}`}
            </Typography>
          }
          action={
            <Box>
              <IconButton
                size="small"
                onClick={() => handleArrayMove(index, "up")}
                disabled={index === 0}
              >
                <ArrowUpIcon />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => handleArrayMove(index, "down")}
                disabled={index === arrayLength - 1}
              >
                <ArrowDownIcon />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => handleArrayDelete(index)}
                color="error"
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          }
          sx={{ pb: 1 }}
        />
        <CardContent sx={{ pt: 0 }}>
          <PyDanticPanel
            rootContent={{
              ...rootContent,
              props: itemProps,
            }}
            elementName={`${elementName}[${index}]`}
            showArrayControls={true}
          />
        </CardContent>
      </Card>
    );
  };

  const renderLayoutRow = (row: any[]): ReactElement => {
    const rowGrid: ReactElement[] = [];

    row.forEach((rowItem, index) => {
      let rowElement: ReactElement | null = null;

      switch (rowItem.type) {
        case "markdown":
          rowElement = (
            <MarkdownDiv
              markdown={rowItem.content !== undefined ? rowItem.content : ""}
              isRenderInline={false}
            />
          );
          break;
        case "html":
          rowElement = (
            <InnerHTML
              html={rowItem.content !== undefined ? rowItem.content : ""}
            />
          );
          break;
        case "argument":
          if (
            rootContentSchema.items?.properties?.[rowItem.argument] ||
            rootContentSchema.properties?.[rowItem.argument]
          ) {
            const fieldSchema =
              rootContentSchema.items?.properties?.[rowItem.argument] ||
              rootContentSchema.properties?.[rowItem.argument];
            rowElement = renderField(rowItem.argument, fieldSchema);
          }
          break;
        case "divider":
          rowElement =
            rowItem.content !== undefined ? (
              <Divider
                textAlign={
                  rowItem.position !== undefined ? rowItem.position : "left"
                }
              >
                {rowItem.content}
              </Divider>
            ) : (
              <Divider />
            );
          break;
      }

      if (rowElement) {
        rowElement = (
          <Grid2
            key={index}
            xs={rowItem.width !== undefined ? rowItem.width * 12 : true}
            mdOffset={rowItem.offset}
          >
            {rowElement}
          </Grid2>
        );
        rowGrid.push(rowElement);
      }
    });

    return (
      <Grid2 container spacing={2} alignItems="center">
        {rowGrid}
      </Grid2>
    );
  };

  const renderAllFields = (): ReactElement[] => {
    const properties =
      rootContentSchema.items?.properties || rootContentSchema.properties || {};
    return Object.keys(properties).map((fieldName, index) => (
      <Box key={index} className="property-wrapper" sx={{ mt: 1 }}>
        {renderField(fieldName, properties[fieldName])}
      </Box>
    ));
  };

  const renderContent = (): ReactElement[] => {
    const elements: ReactElement[] = [];

    const layoutSchema = rootContentSchema.items || rootContentSchema;
    const hasPydanticLayout =
      (rootContentSchema.pydantic_layout &&
        Array.isArray(rootContentSchema.pydantic_layout)) ||
      (layoutSchema.pydantic_layout &&
        Array.isArray(layoutSchema.pydantic_layout));

    if (hasPydanticLayout) {
      const layout =
        rootContentSchema.pydantic_layout || layoutSchema.pydantic_layout;
      layout.forEach((row: any[], index: number) => {
        elements.push(
          <Box
            key={`layout-${index}`}
            className="property-wrapper"
            sx={{ mt: 1 }}
          >
            {renderLayoutRow(row)}
          </Box>,
        );
      });
    } else {
      elements.push(...renderAllFields());
    }

    return elements;
  };

  if (rootContentSchema.widget === "__array_complex_pydantic") {
    return (
      <Card variant="outlined">
        <CardHeader
          title={<Typography variant="h6">{elementName}</Typography>}
          action={
            <Button
              startIcon={<AddIcon />}
              onClick={handleArrayAdd}
              size="small"
              variant="outlined"
            >
              Add Item
            </Button>
          }
        />
        <CardContent>
          {rootContentSchema.title && (
            <MarkdownDiv
              markdown={rootContentSchema.title}
              isRenderInline={false}
            />
          )}
          <Stack spacing={2}>
            {Array.isArray(pydanticForm) &&
              (pydanticForm as any[]).map((item, index) =>
                renderArrayItem(item, index),
              )}
            {(!Array.isArray(pydanticForm) ||
              (pydanticForm as any[]).length === 0) && (
              <Typography
                variant="body2"
                color="text.secondary"
                textAlign="center"
              >
                No data, click the "Add Item" button to add a new item
              </Typography>
            )}
          </Stack>
        </CardContent>
      </Card>
    );
  }

  const cardContent = (
    <Stack spacing={1}>
      {rootContentSchema.title && (
        <MarkdownDiv
          markdown={rootContentSchema.title}
          isRenderInline={false}
        />
      )}
      {renderContent()}
    </Stack>
  );

  if (props.showArrayControls) {
    return cardContent;
  }

  return (
    <Card variant="outlined">
      <CardHeader
        title={<Typography variant="h6">{elementName}</Typography>}
        action={
          props.onArrayDelete &&
          props.arrayIndex !== undefined && (
            <Box>
              {props.onArrayMove && (
                <>
                  <IconButton
                    size="small"
                    onClick={() => props.onArrayMove!(props.arrayIndex!, "up")}
                  >
                    <ArrowUpIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() =>
                      props.onArrayMove!(props.arrayIndex!, "down")
                    }
                  >
                    <ArrowDownIcon />
                  </IconButton>
                </>
              )}
              <IconButton
                size="small"
                onClick={() => props.onArrayDelete!(props.arrayIndex!)}
                color="error"
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          )
        }
      />
      <CardContent>{cardContent}</CardContent>
    </Card>
  );
};

export default PyDanticPanel;
