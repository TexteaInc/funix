import MarkdownIt from "markdown-it";

interface MarkdownDivProps {
  markdown?: string;
  isRenderInline?: boolean;
}

export default function MarkdownDiv(props: MarkdownDivProps) {
  if (!props.markdown) return null;

  const markdown = new MarkdownIt({
    html: true,
    xhtmlOut: true,
    breaks: true,
    linkify: true,
    typographer: true,
  });

  return props.isRenderInline ? (
    <span
      dangerouslySetInnerHTML={{
        __html: markdown.renderInline(props.markdown),
      }}
    />
  ) : (
    <div
      dangerouslySetInnerHTML={{ __html: markdown.render(props.markdown) }}
    />
  );
}
