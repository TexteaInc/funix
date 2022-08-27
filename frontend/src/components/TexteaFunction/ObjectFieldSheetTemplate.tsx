import { ObjectFieldProps } from "@rjsf/core/lib/components/fields/ObjectField";
import { Box, Button, Card, Divider, Stack, Typography } from "@mui/material";
import React, { useEffect } from "react";
import SchemaField from "@rjsf/core/lib/components/fields/SchemaField";
import {
  DataGrid,
  GridCellEditCommitParams,
  GridColDef,
  GridPreProcessEditCellProps,
  GridRowsProp,
  GridSelectionModel,
} from "@mui/x-data-grid";

let rowIdCounter = 0;

const ObjectFieldSheetTemplate = (props: ObjectFieldProps) => {
  const configElements: SchemaField[] = [];
  const arrayElementsInSheet: any[] = [];
  const columns: GridColDef[] = [
    {
      field: "id",
      headerName: "ID",
      type: "number",
    },
  ];

  props.properties.map((element: any) => {
    const elementContent = element.content;
    const elementProps = elementContent.props;
    const isArrayInSheet =
      elementProps.schema.type === "array" &&
      elementProps.schema.hasOwnProperty("widget") &&
      Array.isArray(elementProps.schema.widget) &&
      elementProps.schema.widget.includes("sheet");
    if (!isArrayInSheet) {
      configElements.push(elementContent);
    } else {
      arrayElementsInSheet.push(elementContent);
      const itemType = elementProps.schema.items.type;
      const gridColType = itemType === "integer" ? "number" : itemType;
      let newColumn: GridColDef = {
        field: elementProps.name,
        type: gridColType,
        editable: true,
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
    updateRJSFObjectFieldOpIdCounter += 1;
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

  const handleAddRow = () => {
    const newRow = (() => {
      let row = { id: rowIdCounter++ };
      columns.map((columnDef) => {
        if (columnDef.field === "id") return;
        const value = (() => {
          switch (columnDef.type) {
            case "string":
              return "";
            case "number":
              return 0;
            case "boolean":
              return false;
            default:
              throw new Error("Unsupported type");
          }
        })();
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
    const newRows = rows.filter((row) => !selectionModel.includes(row.id));
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

  return (
    <div>
      <Typography variant="h5">{props.title}</Typography>
      <Typography variant="body1" sx={{ mt: 1 }}>
        {props.description}
      </Typography>
      <Divider sx={{ mt: 1 }} />
      {configElements.map((element: any) => (
        <div className="property-wrapper">
          <Box sx={{ mt: 1 }}>{element}</Box>
        </div>
      ))}
      {getNewDataGridElementIfAvailable()}
    </div>
  );
};

export default ObjectFieldSheetTemplate;
