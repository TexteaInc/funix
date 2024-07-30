import { DataGrid, DataGridProps } from "@mui/x-data-grid";
import { DataGridPro, LicenseInfo } from "@mui/x-data-grid-pro";

const LICENSE_KEY = process.env.REACT_APP_MUI_PRO_LICENSE_KEY;

const registerLicense = () => {
  if (LICENSE_KEY) {
    LicenseInfo.setLicenseKey(LICENSE_KEY);
  }
};

const WrappedDataGrid = (props: DataGridProps) => {
  return LICENSE_KEY ? (
    <DataGridPro
      pagination
      rowsPerPageOptions={[5, 10, 20, 50, 100]}
      {...props}
    />
  ) : (
    <DataGrid rowsPerPageOptions={[5, 10, 20, 50, 100]} {...props} />
  );
};

export { WrappedDataGrid as DataGrid, registerLicense };
