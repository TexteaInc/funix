import { DataGrid } from "@mui/x-data-grid";
import { DataGridPro, LicenseInfo } from "@mui/x-data-grid-pro";

const LICENSE_KEY = process.env.REACT_APP_MUI_PRO_LICENSE_KEY;

const registerLicense = () => {
  if (LICENSE_KEY) {
    LicenseInfo.setLicenseKey(LICENSE_KEY);
  }
};

const WrappedDataGrid = LICENSE_KEY ? DataGridPro : DataGrid;

export { WrappedDataGrid as DataGrid, registerLicense };
