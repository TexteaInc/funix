import { DataGrid, DataGridProps } from "@mui/x-data-grid";
import { DataGridPro, DataGridProProps } from "@mui/x-data-grid-pro";
import { LicenseInfo } from "@mui/x-license";

const LICENSE_KEY = process.env.REACT_APP_MUI_PRO_LICENSE_KEY;

const registerLicense = () => {
  if (LICENSE_KEY) {
    LicenseInfo.setLicenseKey(LICENSE_KEY);
  }
};

const WrappedDataGrid = (props: DataGridProps & DataGridProProps) => {
  return LICENSE_KEY ? (
    <DataGridPro pagination pageSizeOptions={[5, 10, 20, 50, 100]} {...props} />
  ) : (
    <DataGrid pageSizeOptions={[5, 10, 20, 50, 100]} {...props} />
  );
};

export { WrappedDataGrid as DataGrid, registerLicense };
