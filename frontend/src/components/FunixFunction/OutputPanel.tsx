import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Card,
  CardContent,
  Divider,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
  Stack,
  Typography,
} from "@mui/material";
import { GridRowModel, GridToolbar } from "@mui/x-data-grid";
import React from "react";
import { BaseType, FunctionDetail, ReturnType } from "../../shared";
import OutputError from "./OutputComponents/OutputError";
import { outputRow } from "json-schema";
import MarkdownDiv from "../Common/MarkdownDiv";
import OutputMedias from "./OutputComponents/OutputMedias";
import OutputFiles from "./OutputComponents/OutputFiles";
import OutputCode from "./OutputComponents/OutputCode";
import OutputPlot from "./OutputComponents/OutputPlot";
import Grid2 from "@mui/material/Unstable_Grid2";
import { useAtom } from "jotai";
import { storeAtom } from "../../store";
import { ExpandMore } from "@mui/icons-material";
import ThemeReactJson from "../Common/ThemeReactJson";
import { DataGrid } from "../../Key";
import OutputDataframe from "./OutputComponents/OutputDataframe";
import InnerHTML from "dangerously-set-html-content";

const guessJSON = (response: string | null): object | false => {
  if (response === null) return false;
  try {
    return JSON.parse(response);
  } catch (e) {
    return false;
  }
};

const OutputPanel = (props: {
  detail: FunctionDetail;
  backend: URL;
  response: string | null;
}) => {
  const [{ showFunctionDetail, viewType }, setStore] = useAtom(storeAtom);

  type ResponseViewProps = {
    response: string | null;
    returnType?: { [key: string]: BaseType } | ReturnType[] | ReturnType;
  };

  const GuessingDataView: React.FC<ResponseViewProps> = ({ response }) => {
    if (response === null) {
      return <></>;
    } else {
      try {
        const parsedResponse: object = JSON.parse(response);
        if (!Array.isArray(parsedResponse)) {
          if (parsedResponse.hasOwnProperty("error_body")) {
            return <OutputError error={parsedResponse as any} />;
          }
        }
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
        const responseViewRadioGroup = (
          <FormControl>
            <FormLabel id="response-view-radio-group">View in: </FormLabel>
            <RadioGroup
              row
              aria-labelledby="response-view-radio-group"
              name="response-view-radio-group"
              value={viewType}
              onChange={(event) => {
                setStore((store) => ({
                  ...store,
                  viewType: event.target.value as "json" | "sheet",
                }));
              }}
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
              return <ThemeReactJson src={parsedResponse ?? {}} />;
            else if (props.selectedResponseViewType === "sheet")
              return (
                <DataGrid
                  pagination
                  autoPageSize
                  columns={[
                    { field: "id", headerName: "ID" },
                    { field: "value", headerName: "Root" },
                  ]}
                  rows={parsedResponse.map((rowValue, index) => ({
                    id: index,
                    value: rowValue,
                  }))}
                  components={{
                    Toolbar: GridToolbar,
                  }}
                  sx={{ minHeight: 400 }}
                />
              );
            else throw new Error("Unsupported selectedResponseViewType");
          };
          return (
            <div>
              {responseViewRadioGroup}
              <SelectedResponseView selectedResponseViewType={viewType} />
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
            return <ThemeReactJson src={parsedResponse ?? {}} />;
          else {
            const SelectedResponseView = (props: any) => {
              if (props.selectedResponseViewType === "json")
                return <ThemeReactJson src={parsedResponse ?? {}} />;
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
                    pagination
                    autoPageSize
                    columns={keysOfArraysInSheet.map((key) => ({
                      field: key,
                    }))}
                    rows={rows}
                    sx={{ minHeight: 400 }}
                    components={{
                      Toolbar: GridToolbar,
                    }}
                  />
                );
                if (Object.keys(newObject).length != 0) {
                  return (
                    <div>
                      {grid}
                      <ThemeReactJson src={newObject} />
                    </div>
                  );
                } else return grid;
              } else throw new Error("Unsupported selectedResponseViewType");
            };
            return (
              <div>
                {responseViewRadioGroup}
                <SelectedResponseView selectedResponseViewType={viewType} />
              </div>
            );
          }
        } else {
          return <ThemeReactJson src={parsedResponse ?? {}} />;
        }
      } catch (e) {
        return <code>{response ?? ""}</code>;
      }
    }
  };

  const getTypedElement = (
    elementType: ReturnType,
    response: any,
    index: number
  ): JSX.Element => {
    switch (elementType) {
      case "Figure":
        return (
          <OutputPlot
            plotCode={JSON.stringify(response)}
            indexId={index.toString()}
          />
        );
      case "Dataframe":
        return <OutputDataframe dataframe={response} />;
      case "string":
      case "text":
        return <span>{response}</span>;
      case "number":
      case "integer":
      case "boolean":
        return <code>{response}</code>;
      case "array":
      case "list":
      case "object":
      case "dict":
      case "Dict":
      case "List":
        return <GuessingDataView response={JSON.stringify(response)} />;
      case "Markdown":
        return <MarkdownDiv markdown={response} isRenderInline={false} />;
      case "HTML":
        return <InnerHTML html={response} />;
      case "Images":
      case "Videos":
      case "Audios":
      case "FigureImage":
        return (
          <OutputMedias
            medias={response}
            type={elementType}
            backend={props.backend.toString()}
          />
        );
      case "Code":
        if (typeof response === "string") {
          return <OutputCode code={response} />;
        } else {
          const outputCodeProp = response as {
            code: string;
            lang?: string;
          };
          return (
            <OutputCode
              code={outputCodeProp.code}
              language={outputCodeProp.lang}
            />
          );
        }
      case "Files":
        return (
          <OutputFiles files={response} backend={props.backend.toString()} />
        );
      default:
        return <GuessingDataView response={JSON.stringify(response)} />;
    }
  };

  const ResponseView: React.FC<ResponseViewProps> = ({
    response,
    returnType,
  }) => {
    if (response == null) {
      return (
        <Alert severity="info">
          Run the function to see the output/return here. To run, click the Run
          button at the bottom of the left, input panel.
        </Alert>
      );
    } else {
      if (
        typeof returnType !== undefined &&
        (Array.isArray(returnType) || typeof returnType === "string")
      ) {
        const listReturnType =
          typeof returnType === "string" ? [returnType] : returnType;
        const parsedResponse = guessJSON(response);
        if (parsedResponse === false) {
          return <code>{response}</code>;
        }
        if (!Array.isArray(parsedResponse))
          return <GuessingDataView response={response} />;
        const output: outputRow[] = props.detail.schema.output_layout;
        const layout: JSX.Element[] = [];
        output.forEach((row) => {
          const rowElements: JSX.Element[] = [];
          row.forEach((item) => {
            let itemElement: JSX.Element;
            switch (item.type) {
              case "markdown":
                itemElement = (
                  <MarkdownDiv
                    markdown={
                      (Array.isArray(item.content)
                        ? item.content[0]
                        : item.content) || ""
                    }
                    isRenderInline={false}
                  />
                );
                break;
              case "html":
                itemElement = (
                  <InnerHTML
                    html={
                      Array.isArray(item.content)
                        ? item.content[0]
                        : item.content || ""
                    }
                  />
                );
                break;
              case "divider":
                itemElement =
                  item.content !== undefined ? (
                    <Divider textAlign={item.position || "left"}>
                      {item.content}
                    </Divider>
                  ) : (
                    <Divider />
                  );
                break;
              case "images":
              case "videos":
              case "audios":
                itemElement = (
                  <OutputMedias
                    medias={item.content || ""}
                    type={item.type}
                    backend={props.backend.toString()}
                  />
                );
                break;
              case "files":
                itemElement = (
                  <OutputFiles
                    files={item.content || ""}
                    backend={props.backend.toString()}
                  />
                );
                break;
              case "code":
                itemElement = (
                  <OutputCode
                    code={
                      (Array.isArray(item.content)
                        ? item.content[0]
                        : item.content) || ""
                    }
                    language={item.lang}
                  />
                );
                break;
              case "return_index":
                if (Array.isArray(item.index)) {
                  itemElement = <></>;
                  item.index.forEach((index) => {
                    itemElement = (
                      <>
                        {itemElement}
                        {getTypedElement(
                          listReturnType[index],
                          parsedResponse[index],
                          index
                        )}
                      </>
                    );
                  });
                } else {
                  itemElement = getTypedElement(
                    listReturnType[item.index || 0],
                    parsedResponse[item.index || 0],
                    item.index || 0
                  );
                }
                break;
              default:
                itemElement = <code>{item.content ?? ""}</code>;
            }
            rowElements.push(
              <Grid2 xs={item.width || true} mdOffset={item.offset}>
                {itemElement}
              </Grid2>
            );
          });
          layout.push(
            <Grid2 container spacing={2} alignItems="center">
              {rowElements}
            </Grid2>
          );
        });
        const columns = parsedResponse
          .filter((_, index) => {
            if (Array.isArray(props.detail.schema.output_indexes)) {
              return props.detail.schema.output_indexes.indexOf(index) === -1;
            } else {
              return true;
            }
          })
          .map((row, index) => {
            const singleReturnType: ReturnType = listReturnType[index];

            return getTypedElement(singleReturnType, row, index);
          });
        return (
          <>
            {layout}
            {columns}
          </>
        );
      } else if (returnType === null) {
        return (
          <Alert severity="success">
            The function has been successfully executed.
          </Alert>
        );
      } else {
        return <GuessingDataView response={response} />;
      }
    }
  };

  return (
    <Stack spacing={2} id="output-panel">
      <Card>
        <CardContent>
          <Stack spacing={1}>
            <ResponseView
              response={props.response}
              returnType={props.detail.return_type}
            />
          </Stack>
        </CardContent>
      </Card>
      {showFunctionDetail && (
        <Card>
          <CardContent>
            <Typography variant="h5">Function Detail</Typography>
            <ThemeReactJson src={props.detail} collapsed />
          </CardContent>
        </Card>
      )}
      {props.detail.source !== "" && (
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h5">Source Code</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <OutputCode code={props.detail.source} language="python" />
          </AccordionDetails>
        </Accordion>
      )}
    </Stack>
  );
};

export default React.memo(OutputPanel, (prevProps, nextProps) => {
  return (
    prevProps.response === nextProps.response &&
    prevProps.detail === nextProps.detail &&
    prevProps.backend === nextProps.backend
  );
});
