import { GridColDef, GridToolbar } from "@mui/x-data-grid";
import { DataGrid, useGridApiRef } from "../../../Key";
import { Box, Stack, Typography } from "@mui/material";
import { useEffect, useMemo } from "react";
import React from "react";

const defaultAutoSizeOptions = {
  includeHeaders: true,
  includeOutliers: true,
  outliersFactor: 1.5,
};

const OutputDataframe = React.memo(
  (props: {
    dataframe: { [key: string]: any }[];
    gridHeight: number;
    checkboxSelection: boolean;
  }) => {
    const isEmptyDataframe = props.dataframe.length === 0;
    const apiRef = useGridApiRef();

    const { columns, newDataframe } = useMemo(() => {
      if (isEmptyDataframe) {
        return { columns: [], newDataframe: [] };
      }

      const hasId = "id" in props.dataframe[0];
      const columns: GridColDef[] = [];
      const newDataframe: { [key: string]: any }[] = [];

      const row = props.dataframe[0];

      if (!hasId) {
        columns.push({
          field: "id",
          editable: false,
          headerName: "ID",
        });
      }

      Object.keys(row).forEach((key) => {
        columns.push({
          field: key,
          headerName: key,
          editable: false,
        });
      });

      props.dataframe.forEach((row, index) => {
        if (!hasId) {
          newDataframe[index] = {
            id: index,
            ...row,
          };
        } else {
          newDataframe[index] = row;
        }
      });

      return { columns, newDataframe, hasId };
    }, [props.dataframe, isEmptyDataframe]);

    useEffect(() => {
      if (!apiRef.current) return;
      apiRef.current?.autosizeColumns({
        ...defaultAutoSizeOptions,
        columns: columns.map((column) => column.field),
      });
    }, [apiRef, columns, newDataframe]);

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
          apiRef={apiRef as any}
          rows={newDataframe}
          columns={columns}
          slots={{
            toolbar: GridToolbar,
          }}
          autosizeOnMount
          onStateChange={() => {
            apiRef.current?.autosizeColumns({
              ...defaultAutoSizeOptions,
              columns: columns.map((column) => column.field),
            });
          }}
          disableVirtualization
          checkboxSelection={props.checkboxSelection}
          autosizeOptions={{
            ...defaultAutoSizeOptions,
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
