import { Card } from "@mui/material";
import { Prism } from "react-syntax-highlighter";
import { coy } from "react-syntax-highlighter/dist/esm/styles/prism";

interface OutputCodeProps {
  code: string;
  language?: string;
}

export default function OutputCode(props: OutputCodeProps) {
  return (
    <Card
      sx={{
        width: "100%",
      }}
    >
      <Prism
        language={props.language}
        showLineNumbers
        wrapLongLines
        style={coy}
      >
        {props.code}
      </Prism>
    </Card>
  );
}
