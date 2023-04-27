import Editor from "@monaco-editor/react";

interface OutputCodeProps {
  code: string;
  language?: string;
}

export default function OutputCode(props: OutputCodeProps) {
  return (
    <Editor
      width="100%"
      value={props.code}
      language={props.language || "plaintext"}
      onMount={(editor) => {
        const height = editor.getContentHeight();
        editor.layout({ height });
      }}
      options={{
        readOnly: true,
        minimap: {
          enabled: false,
        },
      }}
    />
  );
}
