import { ObjectFieldProps } from "@rjsf/core/lib/components/fields/ObjectField";
import {
  Box,
  Button,
  Card,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
  Stack,
  Typography,
} from "@mui/material";
import React, { SyntheticEvent, useEffect, useState } from "react";
import SchemaField from "@rjsf/core/lib/components/fields/SchemaField";
import {
  DataGrid,
  GridCellEditCommitParams,
  GridColDef,
  GridPreProcessEditCellProps,
  GridRowsProp,
  GridSelectionModel,
} from "@mui/x-data-grid";
import { bindHover, bindPopover } from "material-ui-popup-state";
import HoverPopover from "material-ui-popup-state/HoverPopover";
import { usePopupState } from "material-ui-popup-state/hooks";
import { GridColType } from "@mui/x-data-grid/models/colDef/gridColType";

let rowIdCounter = 0;

const stopEventPropagation = (e: SyntheticEvent) => e.stopPropagation();

const ObjectFieldExtendedTemplate = (props: ObjectFieldProps) => {
  const configElements: SchemaField[] = [];
  const arrayElementsInSheet: any[] = [];
  const columns: GridColDef[] = [
    {
      field: "id",
      headerName: "ID",
      type: "number",
    },
  ];
  const arrayValueSelectors: JSX.Element[] = [];
  let lengthLongestWhitelistColumnInSheet = 0;

  props.properties.map((element: any) => {
    const elementContent = element.content;
    const elementProps = elementContent.props;

    const hasArrayExample =
      elementProps.schema.type === "array" &&
      elementProps.schema.hasOwnProperty("example") &&
      Array.isArray(elementProps.schema.example);
    const hasArrayWhitelist =
      elementProps.schema.type === "array" &&
      elementProps.schema.hasOwnProperty("whitelist") &&
      Array.isArray(elementProps.schema.whitelist);
    let arrayValueSelector = <></>;
    if (hasArrayExample || hasArrayWhitelist) {
      let arrayValueSelectorCandidates: Array<any>[];
      if (hasArrayExample)
        arrayValueSelectorCandidates = elementProps.schema.example;
      else {
        arrayValueSelectorCandidates = elementProps.schema.whitelist;
        arrayValueSelectorCandidates.map((candidate) => {
          lengthLongestWhitelistColumnInSheet = Math.max(
            lengthLongestWhitelistColumnInSheet,
            candidate.length
          );
        });
      }
      const [candidateValueSelected, setCandidateValueSelected] = useState<
        Array<any>[] | undefined
      >(undefined);
      const handleCandidateSelection = (e: SelectChangeEvent<any>) => {
        const targetArray: any[] = JSON.parse(e.target.value);
        const possiblySheetColumns = columns.filter(
          (column) => column.field == elementProps.name
        );
        if (possiblySheetColumns.length != 0) {
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
                row[elementProps.name] = getEmptyValue(columnType);
              }
            });
            return newRows;
          });
        } else {
          elementProps.onChange(targetArray);
        }
        setCandidateValueSelected(e.target.value);
      };
      const labelText = `${elementProps.name} Selector (${
        hasArrayWhitelist ? "whitelist" : "example"
      })`;
      arrayValueSelector = (
        <Box>
          <FormControl fullWidth>
            <InputLabel>{labelText}</InputLabel>
            <Select
              label={labelText}
              value={candidateValueSelected}
              onChange={handleCandidateSelection}
            >
              {arrayValueSelectorCandidates.map((candidate) => {
                const candidateJson = JSON.stringify(candidate, null, 1);
                const candidateRows: GridRowsProp = candidate.map(
                  (candidateRowValue, index) => ({
                    id: index,
                    [elementProps.name]: JSON.stringify(candidateRowValue),
                  })
                );
                const popupState = usePopupState({
                  variant: "popover",
                  popupId: `popover-${elementProps.name}`,
                });
                return (
                  <MenuItem value={candidateJson}>
                    <code {...bindHover(popupState)}>{candidateJson}</code>
                    <HoverPopover {...bindPopover(popupState)}>
                      <Card
                        onClick={stopEventPropagation}
                        onMouseDown={stopEventPropagation}
                        sx={{ padding: 1 }}
                      >
                        <Typography
                          variant="subtitle2"
                          sx={{ marginBottom: 1 }}
                        >
                          Column Preview
                        </Typography>
                        <DataGrid
                          columns={[{ field: elementProps.name }]}
                          rows={candidateRows}
                          sx={{ minHeight: 400 }}
                        />
                      </Card>
                    </HoverPopover>
                  </MenuItem>
                );
              })}
            </Select>
          </FormControl>
        </Box>
      );
    }

    const isArrayInSheet =
      elementProps.schema.type === "array" &&
      elementProps.schema.hasOwnProperty("widget") &&
      Array.isArray(elementProps.schema.widget) &&
      elementProps.schema.widget.includes("sheet");
    if (hasArrayExample || hasArrayWhitelist) {
      arrayValueSelectors.push(arrayValueSelector);
    }
    if (!isArrayInSheet) {
      if (hasArrayExample) {
        configElements.push(elementContent);
      }
    } else {
      arrayElementsInSheet.push(elementContent);
      const itemType = elementProps.schema.items.type;
      const gridColType = itemType === "integer" ? "number" : itemType;
      let newColumn: GridColDef = {
        field: elementProps.name,
        type: gridColType,
        editable: !hasArrayWhitelist,
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
      columns.push(newColumn);
    }
  });

  const [rows, setRows] = React.useState<GridRowsProp>([]);
  useEffect(() => {
    updateRJSFObjectField().then(() => null);
    return;
  }, [rows]);
  const [selectionModel, setSelectionModel] =
    React.useState<GridSelectionModel>([]);

  let gridData: Record<string, Array<any>> = {};
  let updateRJSFObjectFieldOpIdCounter = 0;

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

  const getEmptyValue = (type: GridColType | undefined) => {
    switch (type) {
      case "string":
        return "";
      case "number":
        return 0;
      case "boolean":
        return false;
      default:
        throw new Error("Unsupported type");
    }
  };

  const handleAddRow = () => {
    const newRow = (() => {
      let row = { id: rowIdCounter++ };
      columns.map((columnDef) => {
        if (columnDef.field === "id") return;
        const value = getEmptyValue(columnDef.type);
        row = {
          ...row,
          [columnDef.field]: value,
        };
      });
      return row;
    })();
    setRows((prevRows) => [...prevRows, newRow]);
  };

  const handleDeleteRows = () => {
    const newRows = rows.filter(
      (row, index) =>
        !selectionModel.includes(row.id) ||
        index < lengthLongestWhitelistColumnInSheet
    );
    setRows(newRows);
  };

  const handleSelectionModelChange = (
    newSelectionModel: GridSelectionModel
  ) => {
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

  const getNewDataGridElementIfAvailable = () => {
    if (arrayElementsInSheet.length != 0)
      return (
        <Card className="property-wrapper" sx={{ mt: 1 }}>
          <Box sx={{ width: "100%" }} padding={1}>
            <Stack direction="row" spacing={1}>
              <Button size="small" onClick={handleAddRow}>
                Add a row
              </Button>
              <Button size="small" onClick={handleDeleteRows}>
                Delete selected row(s)
              </Button>
            </Stack>
            <Box sx={{ height: 400, mt: 1 }}>
              <DataGrid
                columns={columns}
                rows={rows}
                checkboxSelection={true}
                selectionModel={selectionModel}
                onSelectionModelChange={handleSelectionModelChange}
                onCellEditCommit={handleCellEditCommit}
              />
            </Box>
          </Box>
        </Card>
      );
    else return <></>;
  };

  const renderElement = (element: any) => (
    <div className="property-wrapper">
      <Box sx={{ mt: 1 }}>{element}</Box>
    </div>
  );

  return (
    <div>
      <Typography variant="h5">{props.title}</Typography>
      <Typography variant="body1" sx={{ mt: 1 }}>
        {props.description}
      </Typography>
      <Divider sx={{ mt: 1 }} />
      {arrayValueSelectors.map(renderElement)}
      {configElements.map(renderElement)}
      {getNewDataGridElementIfAvailable()}
    </div>
  );
};

export default ObjectFieldExtendedTemplate;
