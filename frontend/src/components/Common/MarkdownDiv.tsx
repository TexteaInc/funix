import MarkdownIt from "markdown-it";

interface MarkdownDivProps {
  markdown: string;
}

export default function MarkdownDiv(props: MarkdownDivProps) {
  const markdownHTML = new MarkdownIt({
    html: true,
    xhtmlOut: true,
    breaks: true,
    linkify: true,
    typographer: true,
  }).renderInline(props.markdown);

  return <div dangerouslySetInnerHTML={{ __html: markdownHTML }} />;
}
