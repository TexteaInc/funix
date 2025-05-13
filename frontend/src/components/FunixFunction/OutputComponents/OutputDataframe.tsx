import { GridColDef, GridToolbar } from "@mui/x-data-grid";
import { DataGrid } from "../../../Key";
import { Box, Stack, Typography } from "@mui/material";

export default function OutputDataframe(props: {
  dataframe: { [key: string]: any }[];
  gridHeight: number;
  checkboxSelection: boolean;
}) {
  const isEmptyDataframe = props.dataframe.length === 0;

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
        rows={newDataframe}
        columns={columns}
        slots={{
          toolbar: GridToolbar,
        }}
        disableVirtualization
        checkboxSelection={props.checkboxSelection}
        autosizeOptions={{
          includeHeaders: true,
          includeOutliers: true,
          outliersFactor: 1.5,
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
}
