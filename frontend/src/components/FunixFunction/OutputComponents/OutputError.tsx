import { Alert, AlertTitle } from "@mui/material";

export default function OutputError(props: { error: { error_body: string } }) {
  return (
    <Alert severity="error">
      <AlertTitle>Oops! Something went wrong</AlertTitle>
      <pre
        style={{
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          wordWrap: "break-word",
        }}
      >
        {props.error.error_body}
      </pre>
    </Alert>
  );
}
