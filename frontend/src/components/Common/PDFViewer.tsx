import React from "react";
import { Document, Page, pdfjs } from "react-pdf/dist/esm/entry.webpack5";
import { Button, Grid, Stack, Typography } from "@mui/material";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = `//cdn.jsdelivr.net/npm/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

const PDFViewer = (props: { pdf: string | File }) => {
  const [numPages, setNumPages] = React.useState<number>(0);
  const [pageNumber, setPageNumber] = React.useState<number>(1);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  return (
    <>
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        spacing={2}
      >
        <Button
          onClick={() => setPageNumber(pageNumber - 1)}
          disabled={pageNumber === 1}
        >
          Previous
        </Button>
        <Typography variant="body2">
          Page {pageNumber} of {numPages}
        </Typography>
        <Button
          onClick={() => setPageNumber(pageNumber + 1)}
          disabled={pageNumber === numPages}
        >
          Next
        </Button>
      </Stack>
      <Grid
        container
        direction="row"
        justifyContent="center"
        alignItems="center"
      >
        <Document file={props.pdf} onLoadSuccess={onDocumentLoadSuccess}>
          <Page pageNumber={pageNumber} />
        </Document>
      </Grid>
    </>
  );
};

export default PDFViewer;
