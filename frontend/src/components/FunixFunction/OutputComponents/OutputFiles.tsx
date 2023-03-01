import {
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
} from "@mui/material";
import { FileDownload } from "@mui/icons-material";

export default function OutputFiles(props: {
  files: string[] | string;
  backend: string;
}) {
  const files = Array.isArray(props.files) ? props.files : [props.files];

  return (
    <TableContainer component={Paper}>
      <Table
        sx={{
          width: "100%",
        }}
        size="small"
      >
        <TableBody>
          {files.map((file, index) => {
            const relativeFile = file.startsWith("/file/")
              ? new URL(file, props.backend).toString()
              : file;
            return (
              <TableRow key={index}>
                <TableCell
                  align="left"
                  size="small"
                  sx={{
                    width: 16,
                  }}
                >
                  <IconButton
                    size="small"
                    onClick={() => {
                      const link = document.createElement("a");
                      link.download = "";
                      link.href = relativeFile;
                      link.click();
                    }}
                  >
                    <FileDownload sx={{ margin: "auto" }} />
                  </IconButton>
                </TableCell>
                <TableCell align="left" size="small">
                  {relativeFile}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
