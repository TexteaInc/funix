import { DataGrid, DataGridProps } from "@mui/x-data-grid";
import { DataGridPro, DataGridProProps } from "@mui/x-data-grid-pro";
import {
  DataGridPremium,
  DataGridPremiumProps,
} from "@mui/x-data-grid-premium";
import { LicenseInfo } from "@mui/x-license";
import { useGridApiRef as useGridApiRefNormal } from "@mui/x-data-grid";
import { useGridApiRef as useGridApiRefPro } from "@mui/x-data-grid-pro";
import { useGridApiRef as useGridApiRefPremium } from "@mui/x-data-grid-premium";

type MUI_LICENSE = {
  pro?: string;
  premium?: string;
};

const LICENSE_KEY: MUI_LICENSE = {
  pro: process.env.REACT_APP_MUI_PRO_LICENSE_KEY,
  premium: process.env.REACT_APP_MUI_PERMIUM_LICENSE_KEY,
};

const registerLicense = () => {
  if (LICENSE_KEY.premium) {
    LicenseInfo.setLicenseKey(LICENSE_KEY.premium);
  } else if (LICENSE_KEY.pro) {
    LicenseInfo.setLicenseKey(LICENSE_KEY.pro);
  }
};

const WrappedDataGrid = (
  props: DataGridProps & DataGridProProps & DataGridPremiumProps,
) => {
  return LICENSE_KEY.premium ? (
    <DataGridPremium
      autosizeOnMount
      pagination
      pageSizeOptions={[5, 10, 20, 50, 100]}
      {...props}
    />
  ) : LICENSE_KEY.pro ? (
    <DataGridPro
      autosizeOnMount
      pagination
      pageSizeOptions={[5, 10, 20, 50, 100]}
      {...props}
    />
  ) : (
    <DataGrid
      autosizeOnMount
      pagination
      pageSizeOptions={[5, 10, 20, 50, 100]}
      {...props}
    />
  );
};

const useGridApiRef = LICENSE_KEY.premium
  ? useGridApiRefPremium
  : LICENSE_KEY.pro
    ? useGridApiRefPro
    : useGridApiRefNormal;

export { WrappedDataGrid as DataGrid, registerLicense, useGridApiRef };
