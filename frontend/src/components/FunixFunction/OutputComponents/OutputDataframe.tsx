import { GridColDef, GridToolbar } from "@mui/x-data-grid";
import { DataGrid } from "../../../Key";
import { Box, Stack, Typography } from "@mui/material";
import { useMemo } from "react";
import React from "react";

const getStringDisplayLength = (display: string) => {
  const element = document.createElement("div");
  element.style.fontSize = "0.875rem";
  element.style.letterSpacing = "0.01071em";
  element.style.fontFamily = "Roboto, Helvetica, Arial, sans-serif";
  element.style.opacity = "0";
  element.style.position = "fixed";
  element.style.top = "-1000px";
  element.style.left = "-1000px";
  element.style.whiteSpace = "nowrap";
  element.style.wordBreak = "normal";
  element.style.overflow = "hidden";
  element.style.textOverflow = "ellipsis";
  element.textContent = display;
  document.body.appendChild(element);
  const width = element.offsetWidth;
  document.body.removeChild(element);
  return width;
};

const anyToString = (any: any) => {
  if (typeof any === "object") {
    return JSON.stringify(any);
  }
  if (typeof any === "string") {
    return any;
  }
  return any.toString();
};

const OutputDataframe = React.memo(
  (props: {
    dataframe: { [key: string]: any }[];
    gridHeight: number;
    checkboxSelection: boolean;
  }) => {
    const isEmptyDataframe = props.dataframe.length === 0;
    // const apiRef = useGridApiRef();

    const { columns, newDataframe } = useMemo(() => {
      if (isEmptyDataframe) {
        return { columns: [], newDataframe: [] };
      }

      const hasId = "id" in props.dataframe[0];
      const easyColumns: Record<string, GridColDef> = {};
      const columns: GridColDef[] = [];
      const newDataframe: { [key: string]: any }[] = [];

      const row = props.dataframe[0];

      if (!hasId) {
        columns.push({
          field: "id",
          editable: false,
          headerName: "ID",
          minWidth: 100,
        });
      }

      Object.keys(row).forEach((key) => {
        const keyWidth = getStringDisplayLength(key);
        easyColumns[key] = {
          field: key,
          headerName: key,
          editable: false,
          minWidth: keyWidth * 1.25,
        };
      });

      props.dataframe.forEach((row, index) => {
        for (const key in row) {
          const width = getStringDisplayLength(anyToString(row[key])) * 1.25;
          if (key in easyColumns) {
            if (
              easyColumns[key].minWidth !== undefined &&
              width > easyColumns[key].minWidth
            ) {
              easyColumns[key].minWidth = width;
            }
          }
        }
        if (!hasId) {
          newDataframe[index] = {
            id: index,
            ...row,
          };
        } else {
          newDataframe[index] = row;
        }
      });

      columns.push(...Object.values(easyColumns));

      return { columns, newDataframe, hasId };
    }, [props.dataframe, isEmptyDataframe]);

    // useEffect(() => {
    //   if (!apiRef.current) return;
    //   apiRef.current?.autosizeColumns({
    //     ...defaultAutoSizeOptions,
    //     columns: columns.map((column) => column.field),
    //   });
    // }, [apiRef, columns, newDataframe]);

    if (isEmptyDataframe) {
      return (
        <Stack
          sx={{
            justifyContent: "center",
            alignItems: "center",
            minHeight: props.gridHeight,
            width: "100%",
          }}
        >
          <Typography>No data available</Typography>
        </Stack>
      );
    }

    return (
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          width: "100%",
          height: props.gridHeight,
        }}
      >
        <DataGrid
          autoPageSize
          // apiRef={apiRef as any}
          rows={newDataframe}
          columns={columns}
          slots={{
            toolbar: GridToolbar,
          }}
          autosizeOnMount
          // onStateChange={() => {
          //   apiRef.current?.autosizeColumns({
          //     ...defaultAutoSizeOptions,
          //     columns: columns.map((column) => column.field),
          //   });
          // }}
          disableVirtualization
          checkboxSelection={props.checkboxSelection}
          disableAutosize
          autosizeOptions={{
            includeHeaders: true,
            includeOutliers: true,
            outliersFactor: 1.5,
            columns: columns.map((column) => column.field),
          }}
          initialState={{
            columns: {
              columnVisibilityModel: {
                id: false,
              },
            },
          }}
        />
      </Box>
    );
  },
);

export default OutputDataframe;
