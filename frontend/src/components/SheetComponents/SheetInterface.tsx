import { GridRenderCellParams, GridRowId } from "@mui/x-data-grid";

export interface SheetInterface {
  widget: string;
  type: string;
  params: GridRenderCellParams<any, any, any>;
  customChange: (rowId: GridRowId, field: string, value: any) => void;
}
