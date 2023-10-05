import { ObjectFieldProps } from "@rjsf/core/lib/components/fields/ObjectField";
import {
  Box,
  Button,
  Card,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  InputLabel,
  Menu,
  MenuItem,
  MenuList,
  Select,
  SelectChangeEvent,
  Stack,
  Typography,
} from "@mui/material";
import React, { SyntheticEvent, useEffect, useRef, useState } from "react";
import SchemaField from "@rjsf/core/lib/components/fields/SchemaField";
import {
  GridCellEditCommitParams,
  GridCellParams,
  GridColDef,
  GridColumnMenuContainer,
  GridColumnMenuProps,
  GridColumnsMenuItem,
  GridFilterMenuItem,
  GridPreProcessEditCellProps,
  GridRowId,
  GridRowsProp,
  GridSelectionModel,
  GridValidRowModel,
  HideGridColMenuItem,
  MuiEvent,
  SortGridMenuItems,
} from "@mui/x-data-grid";
import {
  bindHover,
  bindMenu,
  bindPopover,
  bindTrigger,
} from "material-ui-popup-state";
import HoverPopover from "material-ui-popup-state/HoverPopover";
import { usePopupState } from "material-ui-popup-state/hooks";
import SheetSlider from "../SheetComponents/SheetSlider";
import SheetCheckBox from "../SheetComponents/SheetCheckBox";
import JSONEditorWidget from "./JSONEditorWidget";
import { castValue, getInitValue } from "../Common/ValueOperation";
import { GridRowModel } from "@mui/x-data-grid/models/gridRows";
import Grid2 from "@mui/material/Unstable_Grid2";
import MarkdownDiv from "../Common/MarkdownDiv";
import { sliderWidgetParser } from "../Common/WidgetSyntaxParser";
import FileUploadWidget from "./FileUploadWidget";
import { useAtom } from "jotai";
import { storeAtom } from "../../store";
import { DataGrid } from "../../Key";

let rowIdCounter = 0;

const stopEventPropagation = (e: SyntheticEvent) => e.stopPropagation();

const ObjectFieldExtendedTemplate = (props: ObjectFieldProps) => {
  const deepClonedFormData = JSON.parse(JSON.stringify(props.formData));
  const configElements: (SchemaField | JSX.Element)[] = [];
  const rowElements: JSX.Element[] = [];
  const arrayElementsInSheet: any[] = [];
  const columns: GridColDef[] = [
    {
      field: "id",
      headerName: "ID",
      type: "number",
    },
  ];
  const arraySimpleSelectors: JSX.Element[] = [];
  let arraySheetSelectors: Record<string, any> = {};
  let lengthLongestWhitelistColumnInSheet = 0;
  type propElementToJSXElementReturn = {
    type: "config" | "sheet";
    element: JSX.Element;
  };

  const propElementToJSXElement = (
    element: any
  ): propElementToJSXElementReturn => {
    const elementContent = element.content;
    const elementProps = elementContent.props;
    const elementData = elementProps.formData;
    const isArray = elementProps.schema.type === "array";
    const isArrayInSheet =
      elementProps.schema.type === "array" &&
      "widget" in elementProps.schema &&
      elementProps.schema.widget === "sheet";
    const hasArrayExample =
      isArray &&
      "example" in elementProps.schema &&
      Array.isArray(elementProps.schema.example) &&
      elementProps.schema.example.length != 0 &&
      Array.isArray(elementProps.schema.example[0]);
    const hasArrayWhitelist =
      isArray &&
      "whitelist" in elementProps.schema &&
      Array.isArray(elementProps.schema.whitelist) &&
      elementProps.schema.whitelist.length != 0 &&
      Array.isArray(elementProps.schema.whitelist[0]);
    const enum MenuItemGetterType {
      SimpleSelectorExample,
      SimpleSelectorWhitelist,
      SheetSelector,
    }
    const filesType = ["image", "video", "audio", "file"];
    if (!isArray) {
      if (elementContent.props.schema.widget === "json") {
        if (elementContent.props.schema.keys) {
          return {
            type: "config",
            element: (
              <JSONEditorWidget
                widget={elementContent.props}
                checkType={""}
                keys={elementContent.props.schema.keys}
                data={elementData}
              />
            ),
          };
        } else {
          return {
            type: "config",
            element: (
              <JSONEditorWidget
                widget={elementContent.props}
                checkType={""}
                data={elementData}
              />
            ),
          };
        }
      } else if (filesType.indexOf(elementContent.props.schema.widget) !== -1) {
        return {
          type: "config",
          element: (
            <FileUploadWidget
              widget={elementContent.props}
              multiple={false}
              supportType={elementContent.props.schema.widget}
              data={elementData}
            />
          ),
        };
      } else {
        return {
          type: "config",
          element: elementContent,
        };
      }
    } else {
      if (hasArrayExample || hasArrayWhitelist) {
        // Array Selector, Shared Part
        let arraySelectorCandidates: Array<any>[];

        if (hasArrayExample)
          arraySelectorCandidates = elementProps.schema.example;
        else {
          arraySelectorCandidates = elementProps.schema.whitelist;
          arraySelectorCandidates.map((candidate) => {
            lengthLongestWhitelistColumnInSheet = Math.max(
              lengthLongestWhitelistColumnInSheet,
              candidate.length
            );
          });
        }

        const [candidateValueSelected, setCandidateValueSelected] = useState<
          string | []
        >([]);

        const handleCandidateSelectionEvent = (e: SelectChangeEvent<any>) =>
          handleCandidateSelection(e.target.value);

        const handleCandidateSelection = (newSelection: string) => {
          const targetArray: any[] = JSON.parse(newSelection);
          const possiblySheetColumns = columns.filter(
            (column) => column.field == elementProps.name
          );
          if (possiblySheetColumns.length !== 0) {
            if (rows.length < targetArray.length) {
              const currentRowsLength = rows.length;
              for (let i = 0; i < targetArray.length - currentRowsLength; i++) {
                handleAddRow();
              }
            }
            setRows((prevRows) => {
              const newRows = [...prevRows];
              newRows.map((row, index) => {
                if (index < targetArray.length) {
                  row[elementProps.name] = targetArray[index];
                } else {
                  const columnType = possiblySheetColumns[0].type;
                  row[elementProps.name] = getInitValue(columnType);
                }
              });
              return newRows;
            });
          } else {
            elementProps.onChange(targetArray);
          }
          if (hasArrayWhitelist) {
            setCandidateValueSelected(newSelection);
          }
        };

        const getMenuItems = (
          candidates: Array<any>[],
          type: MenuItemGetterType,
          props: any
        ) =>
          candidates.map((candidate) => {
            const candidateJson = JSON.stringify(candidate, null, 1);
            const candidateRows: GridRowsProp = candidate.map(
              (candidateRowValue, index) => {
                const rowValueJsonStr = JSON.stringify(candidateRowValue);
                const toUseJson =
                  rowValueJsonStr.length > 0 &&
                  (rowValueJsonStr[0] == "[" || rowValueJsonStr[0] == "{");
                return {
                  id: index,
                  [elementProps.name]: toUseJson
                    ? rowValueJsonStr
                    : candidateRowValue,
                };
              }
            );
            const popupState = usePopupState({
              variant: "popover",
              popupId: `popover-${elementProps.name}`,
            });
            let handleMenuItemClick = () => {
              return;
            };
            if (type === MenuItemGetterType.SimpleSelectorExample) {
              handleMenuItemClick = () => {
                handleCandidateSelection(candidateJson);
                props.parentPopupState.close();
              };
            }
            if (type === MenuItemGetterType.SheetSelector) {
              handleMenuItemClick = () => {
                handleCandidateSelection(candidateJson);
                props.setDialogOpen(false);
              };
            }
            const stopEventPropagationIfNotSheet = (e: SyntheticEvent) => {
              if (type !== MenuItemGetterType.SheetSelector)
                stopEventPropagation(e);
            };
            // HoverPopover not working on Sheet Fill Selector
            return (
              <MenuItem value={candidateJson} onClick={handleMenuItemClick}>
                <code {...bindHover(popupState)}>{candidateJson}</code>
                <HoverPopover
                  {...bindPopover(popupState)}
                  anchorOrigin={{
                    vertical: "bottom",
                    horizontal: "center",
                  }}
                  transformOrigin={{
                    vertical: "top",
                    horizontal: "center",
                  }}
                >
                  <Card
                    onClick={stopEventPropagationIfNotSheet}
                    onMouseDown={stopEventPropagationIfNotSheet}
                    sx={{ padding: 1 }}
                  >
                    <Typography variant="subtitle2" sx={{ marginBottom: 1 }}>
                      Column Preview
                    </Typography>
                    <DataGrid
                      columns={[{ field: elementProps.name, minWidth: 350 }]}
                      rows={candidateRows}
                      sx={{ minHeight: 400 }}
                    />
                  </Card>
                </HoverPopover>
              </MenuItem>
            );
          });

        if (!isArrayInSheet) {
          // Array Selector, Simple Widget
          let arraySimpleSelector;
          const labelText = `${elementProps.name} Selector (${
            hasArrayWhitelist ? "whitelist" : "example"
          })`;

          if (hasArrayWhitelist) {
            arraySimpleSelector = (
              <Box>
                <FormControl fullWidth>
                  <InputLabel>{labelText}</InputLabel>
                  <Select
                    label={labelText}
                    value={candidateValueSelected}
                    onChange={handleCandidateSelectionEvent}
                    MenuProps={{
                      disableScrollLock: true,
                    }}
                  >
                    {getMenuItems(
                      arraySelectorCandidates,
                      MenuItemGetterType.SimpleSelectorWhitelist,
                      {}
                    )}
                  </Select>
                </FormControl>
              </Box>
            );
          } else {
            arraySimpleSelector = (() => {
              const popupState = usePopupState({
                variant: "popover",
                popupId: "demoMenu",
              });
              return (
                <div>
                  <Button {...bindTrigger(popupState)}>{labelText}</Button>
                  <Menu {...bindMenu(popupState)} disableScrollLock={true}>
                    {getMenuItems(
                      arraySelectorCandidates,
                      MenuItemGetterType.SimpleSelectorExample,
                      {
                        parentPopupState: popupState,
                      }
                    )}
                  </Menu>
                </div>
              );
            })();
          }
          arraySimpleSelectors.push(arraySimpleSelector);
        } else {
          // Array Selector, Sheet Widget (GridColumn)
          const labelText = `Fill (${
            hasArrayWhitelist ? "whitelist" : "example"
          })`;
          arraySheetSelectors = {
            ...arraySheetSelectors,
            [elementProps.name]: (props: any) => ({
              label: labelText,
              menuItems: getMenuItems(
                arraySelectorCandidates,
                MenuItemGetterType.SheetSelector,
                props
              ),
            }),
          };
        }
      }

      if (!isArrayInSheet && !hasArrayWhitelist) {
        if (elementContent.props.schema.widget === "json") {
          return {
            type: "config",
            element: (
              <JSONEditorWidget
                widget={elementContent.props}
                checkType={
                  elementContent.props.schema.items?.type || "DO_NOT_CHECK"
                }
                data={elementData}
              />
            ),
          };
        } else if (filesType.indexOf(elementProps.schema.items.widget) !== -1) {
          return {
            type: "config",
            element: (
              <FileUploadWidget
                widget={elementContent.props}
                multiple={true}
                supportType={elementProps.schema.items.widget}
                data={elementData}
              />
            ),
          };
        } else {
          return {
            type: "config",
            element: elementContent,
          };
        }
      }
      if (isArrayInSheet) {
        const itemType = elementProps.schema.items.type;
        const itemWidget = elementProps.schema.items.widget;
        const gridColType = itemType === "integer" ? "number" : itemType;
        let newColumn: GridColDef = {
          field: elementProps.name,
          type: gridColType,
          editable: !hasArrayWhitelist,
        };
        const handleCustomComponentChange = (
          rowId: GridRowId,
          field: string,
          value: any
        ) => {
          setRows((prevRows) => {
            const newRows = [...prevRows];
            newRows.map((row) => {
              if (row.id === rowId) {
                row[field] = value;
              }
            });
            return newRows;
          });
        };
        if (itemType === "integer") {
          newColumn = {
            ...newColumn,
            preProcessEditCellProps: (params: GridPreProcessEditCellProps) => ({
              ...params.props,
              error: !Number.isInteger(Number(params.props.value)),
            }),
          };
        }

        switch (itemType) {
          case "number":
          case "integer":
            if (itemWidget.indexOf("slider") !== -1) {
              const parsedArguments = sliderWidgetParser(itemWidget);

              const min = parsedArguments[0] || 0;
              const max = parsedArguments[1] || 100;
              const defaultStep = itemType === "integer" ? 1 : 0.1;
              const step = parsedArguments[2] || defaultStep;

              const width = 220 + max.toString().length * 16;

              newColumn = {
                ...newColumn,
                width,
                editable: false,
                renderCell: (params) => {
                  return (
                    <SheetSlider
                      widget={itemWidget}
                      type={itemType}
                      params={params}
                      customChange={handleCustomComponentChange}
                      min={min}
                      max={max}
                      step={step}
                    />
                  );
                },
              };
            }
            break;
          case "boolean":
            if (itemWidget === "checkbox" || itemWidget === "switch") {
              newColumn = {
                ...newColumn,
                editable: false,
                renderCell: (params) => {
                  return (
                    <SheetCheckBox
                      widget={itemWidget}
                      type={itemType}
                      params={params}
                      customChange={handleCustomComponentChange}
                      isSwitch={itemWidget === "switch"}
                    />
                  );
                },
              };
            }
            break;
        }

        columns.push(newColumn);
        return {
          type: "sheet",
          element: elementContent,
        };
      }
    }

    return {
      type: "config",
      element: <></>,
    };
  };

  props.schema.input_layout.forEach((row) => {
    const rowGrid: JSX.Element[] = [];
    row.forEach((rowItem) => {
      let rowElement: JSX.Element = <></>;
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
            <div
              dangerouslySetInnerHTML={{
                __html: rowItem.content !== undefined ? rowItem.content : "",
              }}
            />
          );
          break;
        case "argument":
          rowElement = (
            <>
              {
                propElementToJSXElement(
                  props.properties.filter(
                    (prop: any) => prop.name === rowItem.argument
                  )[0]
                ).element
              }
            </>
          );
          break;
        case "divider":
          rowElement =
            rowItem.content !== undefined ? (
              <Divider
                textAlign={
                  rowItem.position !== undefined ? "left" : rowItem.position
                }
              >
                {rowItem.content}
              </Divider>
            ) : (
              <Divider />
            );
          break;
      }
      rowElement = (
        <Grid2
          xs={rowItem.width !== undefined ? rowItem.width : true}
          mdOffset={rowItem.offset}
        >
          {rowElement}
        </Grid2>
      );
      rowGrid.push(rowElement);
    });
    rowElements.push(
      <Grid2 container spacing={2} alignItems="center">
        {rowGrid.map((item) => item)}
      </Grid2>
    );
  });

  props.properties
    .filter((element: any) => !element.content.props.schema.customLayout)
    .map((element: any) => {
      const result = propElementToJSXElement(element);
      switch (result.type) {
        case "config":
          configElements.push(result.element);
          break;
        case "sheet":
          arrayElementsInSheet.push(result.element);
          break;
      }
    });

  // Sheet Fields and Utils
  const types: (string | undefined)[] = [];
  const fields: string[] = [];
  columns.forEach((column: GridColDef) => {
    types.push(column.type);
    fields.push(column.field);
  });

  type defaultSheetValues = {
    key: string;
    default: any[];
    type: string;
  };

  const getDefaultValues = () => {
    let maxLength = 0;
    const defaultValues: defaultSheetValues[] = arrayElementsInSheet.map(
      (element) => {
        if ("default" in element.props.schema) {
          if (element.props.schema.default.length > maxLength) {
            maxLength = element.props.schema.default.length;
          }
          return {
            key: element.key,
            default: element.props.schema.default,
            type: element.props.schema.items.type,
          };
        } else {
          return {
            key: element.key,
            default: [],
            type: element.props.schema.items.type,
          };
        }
      }
    );
    const newRows = [];
    for (let i = 0; i < maxLength; i++) {
      const newRow: { [key: string]: any } = { id: rowIdCounter++ };
      defaultValues.forEach((value) => {
        if (value.default.length > i) {
          newRow[value.key] = value.default[i];
        } else {
          newRow[value.key] = getInitValue(value.type);
        }
      });
      newRows.push(newRow);
    }
    return newRows;
  };

  const [rows, setRows] = React.useState<GridRowsProp>(getDefaultValues());

  useEffect(() => {
    updateRJSFObjectField().then(() => null);
  }, [rows]);

  // useEffect(() => {
  //   rowIdCounter = 0;
  //   setRows([]);
  //   backSheet();
  // }, [props.formData]);

  // window.addEventListener("funix-rollback-now", () => {
  //   rowIdCounter = 0;
  //   setRows([]);
  //   backSheet();
  // });

  const [selectionModel, setSelectionModel] =
    React.useState<GridSelectionModel>([]);

  let gridData: Record<string, Array<any>> = {};
  let updateRJSFObjectFieldOpIdCounter = 0;

  const backSheet = () => {
    const newSheet: Record<string, any[]> = {};
    const newSheetModel: GridValidRowModel[] = [];
    for (const column of columns) {
      if (column.field === "id") continue;
      const arrayElementsWithKey = arrayElementsInSheet.filter(
        (element) => element.key === column.field
      );
      for (const element of arrayElementsWithKey) {
        const key = element.key;
        if (key in deepClonedFormData) {
          newSheet[key] = deepClonedFormData[key];
        }
      }
    }
    const longestArrayLength = Math.max(
      ...Object.values(newSheet).map((array) => array.length)
    );
    const keysInNewSheet = Object.keys(newSheet);
    for (let i = 0; i < longestArrayLength; i++) {
      const sheetRow: Record<string, any> = {};
      for (const key of keysInNewSheet) {
        sheetRow[key] = newSheet[key][i];
      }
      newSheetModel.push({
        id: i,
        ...sheetRow,
      });
    }
    setRows(newSheetModel);
  };

  const updateRJSFObjectField = async () => {
    updateRJSFObjectFieldOpIdCounter++;
    const currentOpId = updateRJSFObjectFieldOpIdCounter;
    columns.map((column) => {
      gridData = {
        ...gridData,
        [column.field]: [],
      };
    });
    rows.map((row) => {
      Object.entries(row).map(([key, value]) => {
        gridData[key].push(value);
      });
    });
    for (const column of columns) {
      if (column.field == "id") continue;
      const arrayElementsWithKey = arrayElementsInSheet.filter(
        (arrayElement) => arrayElement.key === column.field
      );
      for (const arrayElementWithKey of arrayElementsWithKey) {
        arrayElementWithKey.props.onChange(gridData[arrayElementWithKey.key]);
        const promiseCheckSyncFunction = (
          resolve: (value: void | PromiseLike<void>) => void
        ) => {
          const checkIfFormDataSynced = () =>
            props.formData[arrayElementWithKey.key] !==
            gridData[arrayElementWithKey.key];
          setTimeout(async () => {
            // What is that?
            if (
              currentOpId === updateRJSFObjectFieldOpIdCounter &&
              !checkIfFormDataSynced()
            )
              await new Promise<void>(promiseCheckSyncFunction);
            resolve();
          }, 10);
        };
        await new Promise<void>(promiseCheckSyncFunction);
      }
    }
  };

  const handleAddRow = () => {
    const newRow = (() => {
      let row = { id: rowIdCounter++ };
      columns.map((columnDef) => {
        if (columnDef.field === "id") return;
        const value = getInitValue(columnDef.type);
        row = {
          ...row,
          [columnDef.field]: value,
        };
      });
      return row;
    })();
    setRows((prevRows) => [...prevRows, newRow]);
  };

  const clipSheetTextToArray = (clipText: string): (string[] | undefined)[] => {
    const allLines: string[] = clipText.trim().split(/\r?\n/);
    return allLines.map((line: string) =>
      line
        .trim()
        .split(/\t+/)
        .map((element: string) => element.trim())
    );
  };

  const clipSheetArrayInsertToSheet = (
    rowId: GridRowId,
    clipSheetTextArray: (string[] | undefined)[]
  ) => {
    const newRows: { [key: string]: any }[] = [];
    clipSheetTextArray.forEach((lineArray: string[] | undefined) => {
      if (lineArray === undefined) return;
      const row: { [key: string]: any } = { id: rowIdCounter++ };
      lineArray.forEach((value: string, index: number) => {
        row[fields[index + 1]] = castValue(value, types[index + 1]);
      });
      newRows.push(row);
    });

    if (rows.length === 0) {
      setRows(newRows);
      return;
    }

    if (rows.length > 0 && rowId !== 0) {
      const beforeRowIdRows = rows.filter((row) => row.id < rowId);
      const afterRowIdRows = rows.filter((row) => row.id > rowId);

      const changedNewRows = newRows.map((row, index) => {
        return { ...row, id: index + (rowId as number) };
      });

      const changedAfterRowIdRows = afterRowIdRows.map((row, index) => {
        return {
          ...row,
          id: (rowId as number) + clipSheetTextArray.length + index,
        };
      });

      setRows([
        ...beforeRowIdRows,
        ...changedNewRows,
        ...changedAfterRowIdRows,
      ]);

      return;
    }

    setRows((prevRows) => {
      return [...prevRows, ...newRows];
    });
  };

  const handlePasteRows = () => {
    navigator.clipboard.readText().then((clipText: string) => {
      clipSheetArrayInsertToSheet(0, clipSheetTextToArray(clipText));
    });
  };

  const copyRows = (rows: GridRowModel[]) => {
    let copyString = "";
    rows.forEach((row: GridRowModel) => {
      fields.forEach((field: string, index: number) => {
        if (index === 0) return;
        copyString += `${row[field]}\t`;
      });
      copyString = copyString.substring(0, copyString.length - 1) + "\n";
    });
    navigator.clipboard.writeText(copyString).then(() => {
      copyString = "";
    });
  };

  const handleCopyRows = () => {
    const filteredRows = rows.filter((row: GridRowModel) =>
      selectionModel.includes(row.id)
    );
    copyRows(filteredRows);
  };

  const handleCopyRow = (rowId: GridRowId) => {
    const row = rows.filter((row: GridRowModel) => row.id === rowId);
    copyRows(row);
  };

  const handleDeleteRows = () => {
    const newRows = rows.filter(
      (row, index) =>
        !selectionModel.includes(row.id) ||
        index < lengthLongestWhitelistColumnInSheet
    );
    setRows(newRows);
  };

  const handleDeleteRow = (rowId: GridRowId) => {
    const newRows = rows.filter((row: GridRowModel) => row.id !== rowId);
    setRows(newRows);
  };

  const handleSelectionModelChange = (
    newSelectionModel: GridSelectionModel
  ): void => {
    setSelectionModel(newSelectionModel);
  };

  const handleCellEditCommit = (params: GridCellEditCommitParams) => {
    setRows((prevRows) => {
      const newRows = [...prevRows];
      newRows.map((row) => {
        if (row.id === params.id) {
          row[params.field] = params.value;
        }
      });
      return newRows;
    });
  };

  const insertRows = (rowId: GridRowId) => {
    navigator.clipboard.readText().then((clipText: string) => {
      clipSheetArrayInsertToSheet(rowId, clipSheetTextToArray(clipText));
    });
  };

  const handleCellKeyDown = (
    params: GridCellParams,
    event: MuiEvent<React.KeyboardEvent>
  ): void => {
    if (event.key === "Delete") {
      if (selectionModel.length === 0) handleDeleteRow(params.id);
      else handleDeleteRows();
    }
    if (event.ctrlKey) {
      if (event.key === "c") {
        if (selectionModel.length === 0) handleCopyRow(params.id);
        else handleCopyRows();
      }
      if (event.key === "v") insertRows(params.id);
    }
  };

  const getNewDataGridElementIfAvailable = () => {
    const [{ backHistory }] = useAtom(storeAtom);

    useEffect(() => {
      if (backHistory !== null && backHistory["input"] !== null) {
        rowIdCounter = 0;
        setRows([]);
        backSheet();
      }
    }, [backHistory, props.formData]);

    if (arrayElementsInSheet.length != 0) {
      return (
        <Card className="property-wrapper" sx={{ mt: 1 }}>
          <Box sx={{ width: "100%" }} padding={1}>
            <Stack direction="row" spacing={1}>
              <Button size="small" onClick={handleAddRow} variant="text">
                Add a row
              </Button>
              <Button size="small" onClick={handleDeleteRows} variant="text">
                Delete selected row(s)
              </Button>
              <Button size="small" onClick={handleCopyRows} variant="text">
                Copy
              </Button>
              <Button size="small" onClick={handlePasteRows} variant="text">
                Paste
              </Button>
            </Stack>
            <Box sx={{ height: 400, mt: 1, paddingRight: 1 }}>
              <DataGrid
                columns={columns}
                columnVisibilityModel={{
                  id: false,
                }}
                rows={rows}
                checkboxSelection={true}
                selectionModel={selectionModel}
                onSelectionModelChange={handleSelectionModelChange}
                onCellEditCommit={handleCellEditCommit}
                disableSelectionOnClick={true}
                components={{
                  ColumnMenu: GridColumnMenu,
                }}
                sx={{ marginRight: 1 }}
                onCellKeyDown={handleCellKeyDown}
              />
            </Box>
          </Box>
        </Card>
      );
    } else return <></>;
  };

  const [dialogOpen, setDialogOpen] = useState<boolean>(false);
  const [dialogTitle, setDialogTitle] = useState<string>("");
  const [dialogMenuListContent, setDialogMenuListContent] = useState<any>(
    <></>
  );
  const GridColumnMenu = React.forwardRef<
    HTMLUListElement,
    GridColumnMenuProps
  >(function GridColumnMenu(props: GridColumnMenuProps, ref) {
    const { hideMenu, currentColumn } = props;
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const forcedCurrentColumn = currentColumn!;
    const fieldName = forcedCurrentColumn.field;
    let extraMenuItem = <></>;
    if (arraySheetSelectors.hasOwnProperty(fieldName)) {
      const arraySheetSelector = arraySheetSelectors[fieldName]({
        setDialogOpen: setDialogOpen,
      });
      const handleMenuItemClick = (e: React.MouseEvent<any>) => {
        hideMenu(e);
        setDialogTitle(`${arraySheetSelector.label} of ${fieldName}`);
        setDialogMenuListContent(arraySheetSelector.menuItems);
        setDialogOpen(true);
      };
      extraMenuItem = (
        <div>
          <MenuItem onClick={handleMenuItemClick}>
            {arraySheetSelector.label}
          </MenuItem>
        </div>
      );
    }
    return (
      <GridColumnMenuContainer ref={ref} {...props}>
        <SortGridMenuItems onClick={hideMenu} column={forcedCurrentColumn} />
        <GridFilterMenuItem onClick={hideMenu} column={forcedCurrentColumn} />
        <HideGridColMenuItem onClick={hideMenu} column={forcedCurrentColumn} />
        <GridColumnsMenuItem onClick={hideMenu} column={forcedCurrentColumn} />
        {extraMenuItem}
      </GridColumnMenuContainer>
    );
  });

  // Object Rendering

  const renderElement = (element: any, key: number) => (
    <div className="property-wrapper" key={key}>
      <Box sx={{ mt: 1 }}>{element}</Box>
    </div>
  );

  const pushDone = useRef(false);

  useEffect(() => {
    if (pushDone.current) return;
    if (arrayElementsInSheet.length !== 0) {
      pushDone.current = true;
      rowIdCounter = 0;
    }
  }, []);

  return (
    <Stack spacing={1}>
      {props.description !== "" && (
        <MarkdownDiv markdown={props.description} isRenderInline={false} />
      )}
      {rowElements.map(renderElement)}
      {arraySimpleSelectors.map(renderElement)}
      {configElements.map(renderElement)}
      {getNewDataGridElementIfAvailable()}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>{dialogTitle}</DialogTitle>
        <DialogContent>
          <MenuList>{dialogMenuListContent}</MenuList>
        </DialogContent>
      </Dialog>
    </Stack>
  );
};

export default ObjectFieldExtendedTemplate;
