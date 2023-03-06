import { Card } from "@mui/material";
import { Prism } from "react-syntax-highlighter";
import mcoy from "./mcoy";

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
        wrapLongLines
        showLineNumbers
        lineProps={{ style: { flexWrap: "wrap" } }}
        style={mcoy as any}
      >
        {props.code}
      </Prism>
    </Card>
  );
}
