import React, { useState } from "react";
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import Form from "@rjsf/material-ui/v5";
import { callFunctionRaw, FunctionDetail, FunctionPreview } from "../../shared";
import useSWR from "swr";
import {
  Alert,
  Button,
  Card,
  CardContent,
  FormControl,
  FormControlLabel,
  FormLabel,
  Grid,
  Radio,
  RadioGroup,
  Stack,
  Typography,
} from "@mui/material";
import ReactJson from "react-json-view";
import TextExtendedWidget from "./TextExtendedWidget";
import ObjectFieldExtendedTemplate from "./ObjectFieldExtendedTemplate";
import { DataGrid } from "@mui/x-data-grid";
import { GridRowModel } from "@mui/x-data-grid/models/gridRows";
import SwitchWidget from "./SwitchWidget";

export type FunctionDetailProps = {
  preview: FunctionPreview;
  backend: URL;
  setTheme: (theme: Record<string, any>) => void;
};

const TexteaFunction: React.FC<FunctionDetailProps> = ({
  preview,
  backend,
  setTheme,
}) => {
  const { data: detail } = useSWR<FunctionDetail>(
    new URL(`/param/${preview.path}`, backend).toString()
  );
  const [form, setForm] = useState<Record<string, any>>({});
  const [response, setResponse] = useState<string | null>(null);

  if (detail == null) {
    console.log("Failed to display function detail");
    return <div />;
  }

  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const functionDetail = detail!;

  const handleChange = ({ formData }: Record<string, any>) => {
    // console.log("Data changed: ", formData);
    setForm(formData);
  };

  const handleSubmit = async () => {
    console.log("Data submitted: ", form);
    const response = await callFunctionRaw(
      new URL(`/call/${functionDetail.id}`, backend),
      form
    );
    setResponse(response.toString());
  };

  const widgets = {
    TextWidget: TextExtendedWidget,
    CheckboxWidget: SwitchWidget,
  };

  const uiSchema = {
    "ui:ObjectFieldTemplate": ObjectFieldExtendedTemplate,
    "ui:submitButtonOptions": {
      norender: true,
    },
  };

  type ResponseViewProps = {
    response: string | null;
  };

  const ResponseView: React.FC<ResponseViewProps> = ({ response }) => {
    if (response == null) {
      return (
        <Alert severity="info">
          Execute the function first to see response here
        </Alert>
      );
    } else {
      try {
        const parsedResponse: object = JSON.parse(response);
        const is1dArray = (target: any) => {
          if (!Array.isArray(target)) return false;
          else {
            for (const row of target)
              if (
                Array.isArray(row) ||
                typeof row === "object" ||
                typeof row === "function"
              )
                return false;
            return true;
          }
        };
        if (typeof parsedResponse !== "object" && !is1dArray(parsedResponse)) {
          return <code>{response ?? ""}</code>;
        }
        const [selectedResponseViewType, setSelectedResponseViewType] =
          useState<string>("json");
        const handleResponseViewChange = (
          e: React.ChangeEvent<HTMLInputElement>
        ) => {
          setSelectedResponseViewType(e.target.value);
        };
        const responseViewRadioGroup = (
          <FormControl>
            <FormLabel id="response-view-radio-group">View in</FormLabel>
            <RadioGroup
              row
              aria-labelledby="response-view-radio-group"
              name="response-view-radio-group"
              value={selectedResponseViewType}
              onChange={handleResponseViewChange}
            >
              <FormControlLabel value="json" control={<Radio />} label="JSON" />
              <FormControlLabel
                value="sheet"
                control={<Radio />}
                label="Sheet"
              />
            </RadioGroup>
          </FormControl>
        );
        if (Array.isArray(parsedResponse) && is1dArray(parsedResponse)) {
          const SelectedResponseView = (props: any) => {
            if (props.selectedResponseViewType === "json")
              return <ReactJson src={parsedResponse ?? {}} />;
            else if (props.selectedResponseViewType === "sheet")
              return (
                <DataGrid
                  columns={[{ field: "root" }]}
                  rows={parsedResponse.map((rowValue, index) => ({
                    id: index,
                    root: rowValue,
                  }))}
                />
              );
            else throw new Error("Unsupported selectedResponseViewType");
          };
          return (
            <div>
              {responseViewRadioGroup}
              <SelectedResponseView
                selectedResponseViewType={selectedResponseViewType}
              />
            </div>
          );
        } else if (
          typeof parsedResponse === "object" &&
          parsedResponse !== null
        ) {
          const keysOfArraysInSheet: string[] = [];
          for (const [k, v] of Object.entries(parsedResponse)) {
            if (Array.isArray(v) && is1dArray(v)) {
              keysOfArraysInSheet.push(k);
            }
          }
          if (keysOfArraysInSheet.length === 0)
            return <ReactJson src={parsedResponse ?? {}} />;
          else {
            const SelectedResponseView = (props: any) => {
              if (props.selectedResponseViewType === "json")
                return <ReactJson src={parsedResponse ?? {}} />;
              else if (props.selectedResponseViewType === "sheet") {
                const rows: GridRowModel[] = [];
                let newObject: object = {};
                for (const [k, v] of Object.entries(parsedResponse)) {
                  if (keysOfArraysInSheet.includes(k)) {
                    v.map((rowValue: any, index: number) => {
                      if (index < rows.length) {
                        rows[index] = {
                          ...rows[index],
                          [k]: rowValue,
                        };
                      } else {
                        rows.push({
                          id: index,
                          [k]: rowValue,
                        });
                      }
                    });
                  } else {
                    newObject = { ...newObject, [k]: v };
                  }
                }
                const grid = (
                  <DataGrid
                    columns={keysOfArraysInSheet.map((key) => ({
                      field: key,
                    }))}
                    rows={rows}
                    sx={{ minHeight: 400 }}
                  />
                );
                if (Object.keys(newObject).length != 0) {
                  return (
                    <div>
                      {grid}
                      <ReactJson src={newObject} />
                    </div>
                  );
                } else return grid;
              } else throw new Error("Unsupported selectedResponseViewType");
            };
            return (
              <div>
                {responseViewRadioGroup}
                <SelectedResponseView
                  selectedResponseViewType={selectedResponseViewType}
                />
              </div>
            );
          }
        } else {
          return <ReactJson src={parsedResponse ?? {}} />;
        }
      } catch (e) {
        return <code>{response ?? ""}</code>;
      }
    }
  };

  const formElement = (
    <Form
      schema={functionDetail.schema}
      formData={form}
      onChange={handleChange}
      widgets={widgets}
      uiSchema={uiSchema}
    />
  );

  setTheme(functionDetail.theme);

  return (
    <Stack spacing={2}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              {formElement}
              <Button variant="contained" onClick={handleSubmit} sx={{ mt: 1 }}>
                Submit
              </Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Stack spacing={2}>
            <Card>
              <CardContent>
                <Stack spacing={1}>
                  <Typography variant="h5">Response</Typography>
                  <ResponseView response={response} />
                </Stack>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <Typography variant="h5">Function Detail</Typography>
                <ReactJson src={functionDetail} collapsed />
              </CardContent>
            </Card>
          </Stack>
        </Grid>
      </Grid>
    </Stack>
  );
};

export default TexteaFunction;
