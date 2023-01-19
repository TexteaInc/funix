import { Prism } from "react-syntax-highlighter";

interface OutputCodeProps {
  code: string;
  language?: string;
}

export default function OutputCode(props: OutputCodeProps) {
  return <Prism language={props.language}>{props.code}</Prism>;
}
