import Editor from "@monaco-editor/react";
import { useTheme } from "@mui/material";

interface OutputCodeProps {
  code: string;
  language?: string;
}

export default function OutputCode(props: OutputCodeProps) {
  const theme = useTheme();

  return (
    <Editor
      width="100%"
      value={props.code}
      language={props.language || "plaintext"}
      onMount={(editor) => {
        const height = editor.getContentHeight();
        editor.layout({ height });
      }}
      theme={theme.palette.mode === "dark" ? "vs-dark" : "light"}
      options={{
        readOnly: true,
        minimap: {
          enabled: false,
        },
      }}
    />
  );
}
