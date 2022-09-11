import { GridRenderCellParams } from "@mui/x-data-grid";

export interface SheetInterface {
  widget: string;
  type: string;
  params: GridRenderCellParams<any, any, any>;
  customChange: object;
}
