import { GridColDef, GridToolbar } from "@mui/x-data-grid";
import { DataGrid } from "../../../Key";
import { Box } from "@mui/material";

export default function OutputDataframe(props: {
  dataframe: { [key: string]: any }[];
}) {
  const hasId = props.dataframe[0].hasOwnProperty("id");
  const columns: GridColDef[] = [];
  const newDataframe: { [key: string]: any }[] = [];

  const row = props.dataframe[0];

  if (!hasId) {
    columns.push({ field: "id", editable: false, headerName: "ID" });
  }

  Object.keys(row).forEach((key) => {
    columns.push({
      field: key,
      headerName: key,
      width: 150,
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
    <Box sx={{ height: 400, width: "100%" }}>
      <DataGrid
        rows={newDataframe}
        columns={columns}
        components={{
          Toolbar: GridToolbar,
        }}
        checkboxSelection
      />
    </Box>
  );
}
