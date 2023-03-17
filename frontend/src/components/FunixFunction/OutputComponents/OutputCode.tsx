import Editor from "@monaco-editor/react";

interface OutputCodeProps {
  code: string;
  language?: string;
}

export default function OutputCode(props: OutputCodeProps) {
  return (
    <Editor
      height={300}
      width="100%"
      value={props.code}
      language={props.language || "plaintext"}
      options={{
        readOnly: true,
      }}
    />
  );
}
