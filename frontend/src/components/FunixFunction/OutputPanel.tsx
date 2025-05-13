import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Button,
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
import React, { ReactElement, useMemo, useCallback } from "react";
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
import { useNavigate } from "react-router-dom";

const guessJSON = (response: string | null): object | false => {
  if (response === null) return false;
  try {
    return JSON.parse(response);
  } catch (e) {
    return false;
  }
};

const ResponseViewRadioGroup = React.memo(
  ({
    viewType,
    onChange,
  }: {
    viewType: string;
    onChange: (value: "json" | "sheet") => void;
  }) => (
    <FormControl>
      <FormLabel id="response-view-radio-group">View in: </FormLabel>
      <RadioGroup
        row
        aria-labelledby="response-view-radio-group"
        name="response-view-radio-group"
        value={viewType}
        onChange={(event) => onChange(event.target.value as "json" | "sheet")}
      >
        <FormControlLabel value="json" control={<Radio />} label="JSON" />
        <FormControlLabel value="sheet" control={<Radio />} label="Sheet" />
      </RadioGroup>
    </FormControl>
  ),
);

const GuessingDataView = React.memo(
  ({ response }: { response: string | null }) => {
    const [{ viewType }, setStore] = useAtom(storeAtom);

    const handleViewTypeChange = useCallback(
      (newViewType: "json" | "sheet") => {
        setStore((store) => ({
          ...store,
          viewType: newViewType,
        }));
      },
      [setStore],
    );

    if (response === null) {
      return <></>;
    } else {
      try {
        const parsedResponse: object = JSON.parse(response);
        if (!Array.isArray(parsedResponse)) {
          if ("error_body" in parsedResponse) {
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

        if (Array.isArray(parsedResponse) && is1dArray(parsedResponse)) {
          const SelectedResponseView = useMemo(() => {
            if (viewType === "json")
              return <ThemeReactJson src={parsedResponse ?? {}} />;
            else if (viewType === "sheet")
              return (
                <DataGrid
                  pagination
                  autoPageSize
                  columns={[
                    { field: "id", headerName: "ID" },
                    {
                      field: "value",
                      headerName: "Root",
                    },
                  ]}
                  rows={parsedResponse.map((rowValue, index) => ({
                    id: index,
                    value: rowValue,
                  }))}
                  slots={{
                    toolbar: GridToolbar,
                  }}
                  sx={{ minHeight: 400 }}
                />
              );
            else return <div>Unsupported view type</div>;
          }, [parsedResponse, viewType]);

          return (
            <div>
              <ResponseViewRadioGroup
                viewType={viewType}
                onChange={handleViewTypeChange}
              />
              {SelectedResponseView}
            </div>
          );
        } else if (
          typeof parsedResponse === "object" &&
          parsedResponse !== null
        ) {
          const keysOfArraysInSheet = useMemo(() => {
            const keys: string[] = [];
            for (const [k, v] of Object.entries(parsedResponse)) {
              if (Array.isArray(v) && is1dArray(v)) {
                keys.push(k);
              }
            }
            return keys;
          }, [parsedResponse]);

          if (keysOfArraysInSheet.length === 0)
            return <ThemeReactJson src={parsedResponse ?? {}} />;
          else {
            const SelectedResponseView = useMemo(() => {
              if (viewType === "json")
                return <ThemeReactJson src={parsedResponse ?? {}} />;
              else if (viewType === "sheet") {
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
                    slots={{
                      toolbar: GridToolbar,
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
              } else return <div>Unsupported view type</div>;
            }, [parsedResponse, viewType, keysOfArraysInSheet]);

            return (
              <div>
                <ResponseViewRadioGroup
                  viewType={viewType}
                  onChange={handleViewTypeChange}
                />
                {SelectedResponseView}
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
  },
);

const TypedElement = React.memo(
  ({
    elementType,
    response,
    index,
  }: {
    elementType: ReturnType;
    response: any;
    index: number;
  }) => {
    const navigate = useNavigate();
    const [store, setStore] = useAtom(storeAtom);

    switch (elementType) {
      case "Callable": {
        const jumpHref = response.jump;
        if (jumpHref === undefined || jumpHref === null || jumpHref === "") {
          return <Button variant="contained">Callable</Button>;
        }
        return (
          <Button
            variant="contained"
            onClick={() => {
              if (
                jumpHref !== undefined &&
                jumpHref !== null &&
                jumpHref !== ""
              ) {
                if ("args" in response) {
                  setStore((store) => {
                    const newCallableDefault = { ...store.callableDefault };
                    newCallableDefault[jumpHref] = response.args;
                    return {
                      ...store,
                      callableDefault: newCallableDefault,
                    };
                  });
                }
                navigate(jumpHref);
              }
            }}
          >
            {response.title}
          </Button>
        );
      }
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
            backend={store.backend?.toString() || ""}
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
          <OutputFiles
            files={response}
            backend={store.backend?.toString() || ""}
          />
        );
      default:
        return <GuessingDataView response={JSON.stringify(response)} />;
    }
  },
);

// 提取一个空响应组件
const EmptyResponseAlert = React.memo(() => (
  <Alert severity="info">
    Run the function to see the output/return here. To run, click the Run button
    at the bottom of the left, input panel.
  </Alert>
));

// 提取成功执行的响应组件
const SuccessResponseAlert = React.memo(() => (
  <Alert severity="success">The function has been successfully executed.</Alert>
));

// 提取输出布局项组件
const OutputLayoutItem = React.memo(
  ({
    item,
    parsedResponse,
    listReturnType,
    backend,
    rowElementIndex,
  }: {
    item: any;
    parsedResponse: any;
    listReturnType: ReturnType[];
    backend: string;
    rowElementIndex: number;
  }) => {
    let itemElement: ReactElement;

    switch (item.type) {
      case "markdown":
        itemElement = (
          <MarkdownDiv
            markdown={
              (Array.isArray(item.content) ? item.content[0] : item.content) ||
              ""
            }
            isRenderInline={false}
          />
        );
        break;
      case "html":
        itemElement = (
          <InnerHTML
            html={
              Array.isArray(item.content) ? item.content[0] : item.content || ""
            }
          />
        );
        break;
      case "divider":
        itemElement =
          item.content !== undefined ? (
            <Divider textAlign={item.position || "left"}>
              {Array.isArray(item.content) ? item.content[0] : item.content}
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
            backend={backend}
          />
        );
        break;
      case "files":
        itemElement = (
          <OutputFiles files={item.content || ""} backend={backend} />
        );
        break;
      case "code":
        itemElement = (
          <OutputCode
            code={
              (Array.isArray(item.content) ? item.content[0] : item.content) ||
              ""
            }
            language={item.lang}
          />
        );
        break;
      case "return_index":
        if (Array.isArray(item.index)) {
          const elements: ReactElement[] = [];
          item.index.forEach((index: number) => {
            elements.push(
              <TypedElement
                key={`typed-element-${index}`}
                elementType={listReturnType[index]}
                response={parsedResponse[index]}
                index={index}
              />,
            );
          });
          itemElement = <>{elements}</>;
        } else {
          itemElement = (
            <TypedElement
              elementType={listReturnType[item.index || 0]}
              response={parsedResponse[item.index || 0]}
              index={item.index || 0}
            />
          );
        }
        break;
      default:
        itemElement = <code>{item.content ?? ""}</code>;
    }

    return (
      <Grid2
        key={`grid-item-${item.type}-${rowElementIndex}`}
        xs={item.width || true}
        mdOffset={item.offset}
      >
        {itemElement}
      </Grid2>
    );
  },
  (prevProps, nextProps) => {
    // 自定义比较方法，减少不必要的重渲染
    return (
      prevProps.rowElementIndex === nextProps.rowElementIndex &&
      prevProps.backend === nextProps.backend &&
      JSON.stringify(prevProps.item) === JSON.stringify(nextProps.item) &&
      // 只比较相关的响应部分
      (prevProps.item.type !== "return_index" ||
        (Array.isArray(prevProps.item.index)
          ? prevProps.item.index.every(
              (idx: number) =>
                JSON.stringify(prevProps.parsedResponse[idx]) ===
                JSON.stringify(nextProps.parsedResponse[idx]),
            )
          : JSON.stringify(
              prevProps.parsedResponse[prevProps.item.index || 0],
            ) ===
            JSON.stringify(
              nextProps.parsedResponse[nextProps.item.index || 0],
            )))
    );
  },
);

// 提取输出行组件
const OutputRow = React.memo(
  ({
    row,
    rowIndex,
    parsedResponse,
    listReturnType,
    backend,
  }: {
    row: any[];
    rowIndex: number;
    parsedResponse: any;
    listReturnType: ReturnType[];
    backend: string;
  }) => {
    const rowElements = useMemo(() => {
      return row.map((item, itemIndex) => (
        <OutputLayoutItem
          key={`item-${rowIndex}-${itemIndex}`}
          item={item}
          parsedResponse={parsedResponse}
          listReturnType={listReturnType}
          backend={backend}
          rowElementIndex={itemIndex}
        />
      ));
    }, [row, rowIndex, parsedResponse, listReturnType, backend]);

    return (
      <Grid2
        key={`grid-row-${rowIndex}`}
        container
        spacing={2}
        alignItems="center"
      >
        {rowElements}
      </Grid2>
    );
  },
);

// 提取输出列组件
const OutputColumns = React.memo(
  ({
    parsedResponse,
    listReturnType,
    outputIndexes,
  }: {
    parsedResponse: any[];
    listReturnType: ReturnType[];
    outputIndexes: number[] | undefined;
  }) => {
    return (
      <>
        {parsedResponse
          .filter((_, index) => {
            if (Array.isArray(outputIndexes)) {
              return outputIndexes.indexOf(index) === -1;
            } else {
              return true;
            }
          })
          .map((row, index) => {
            const singleReturnType: ReturnType = listReturnType[index];
            return (
              <TypedElement
                key={`column-element-${index}`}
                elementType={singleReturnType}
                response={row}
                index={index}
              />
            );
          })}
      </>
    );
  },
);

// 提取有类型布局的响应视图组件
const TypedLayoutResponseView = React.memo(
  ({
    response,
    returnType,
    detail,
    backend,
  }: {
    response: string;
    returnType: ReturnType[] | ReturnType;
    detail: FunctionDetail;
    backend: URL;
  }) => {
    const listReturnType = useMemo(
      () => (typeof returnType === "string" ? [returnType] : returnType),
      [returnType],
    );

    const parsedResponse = useMemo(() => {
      const result = guessJSON(response);
      return result === false ? null : result;
    }, [response]);

    // 如果解析失败，直接显示原始响应
    if (parsedResponse === null) {
      return <code>{response}</code>;
    }

    // 如果不是数组，使用GuessingDataView
    if (!Array.isArray(parsedResponse)) {
      return <GuessingDataView response={response} />;
    }

    // 输出布局
    const output: outputRow[] = detail.schema.output_layout;

    // 确保listReturnType是数组类型
    const safeListReturnType: ReturnType[] = Array.isArray(listReturnType)
      ? listReturnType
      : [listReturnType];

    return (
      <>
        {output.map((row, rowIndex) => (
          <OutputRow
            key={`row-${rowIndex}`}
            row={row}
            rowIndex={rowIndex}
            parsedResponse={parsedResponse}
            listReturnType={safeListReturnType}
            backend={backend.toString()}
          />
        ))}

        <OutputColumns
          parsedResponse={parsedResponse}
          listReturnType={safeListReturnType}
          outputIndexes={detail.schema.output_indexes}
        />
      </>
    );
  },
);

const ResponseView = React.memo(
  ({
    response,
    returnType,
    detail,
    backend,
  }: {
    response: string | null;
    returnType?: { [key: string]: BaseType } | ReturnType[] | ReturnType;
    detail: FunctionDetail;
    backend: URL;
  }) => {
    // 处理空响应
    if (response == null) {
      return <EmptyResponseAlert />;
    }

    // 处理有类型的响应
    if (
      returnType !== undefined &&
      (Array.isArray(returnType) || typeof returnType === "string")
    ) {
      return (
        <TypedLayoutResponseView
          response={response}
          returnType={returnType}
          detail={detail}
          backend={backend}
        />
      );
    }

    // 处理返回null的响应
    else if (returnType === null) {
      return <SuccessResponseAlert />;
    }

    // 处理其他类型的响应
    else {
      return <GuessingDataView response={response} />;
    }
  },
);

const OutputPanel = (props: {
  detail: FunctionDetail;
  backend: URL;
  response: string | null;
}) => {
  const [{ showFunctionDetail }] = useAtom(storeAtom);

  const functionDetailCard = useMemo(() => {
    if (!showFunctionDetail) return null;
    return (
      <Card>
        <CardContent>
          <Typography variant="h5">Function Detail</Typography>
          <ThemeReactJson src={props.detail} collapsed />
        </CardContent>
      </Card>
    );
  }, [showFunctionDetail, props.detail]);

  const sourceCodeAccordion = useMemo(() => {
    if (props.detail.source === "") return null;
    return (
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h5">Source Code</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <OutputCode code={props.detail.source} language="python" />
        </AccordionDetails>
      </Accordion>
    );
  }, [props.detail.source]);

  return (
    <Stack spacing={2} id="output-panel">
      <Card>
        <CardContent>
          <Stack spacing={1}>
            <ResponseView
              response={props.response}
              returnType={props.detail.return_type}
              detail={props.detail}
              backend={props.backend}
            />
          </Stack>
        </CardContent>
      </Card>
      {functionDetailCard}
      {sourceCodeAccordion}
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
