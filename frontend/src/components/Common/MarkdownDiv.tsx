import {
  Card,
  CardMedia,
  Checkbox,
  Divider,
  Link,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import ReactMarkdown, { Components } from "react-markdown";
import rehypeRaw from "rehype-raw";
import React from "react";
import { Variant } from "@mui/material/styles/createTypography";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import SyntaxHighlighter from "react-syntax-highlighter";
import { monokai } from "react-syntax-highlighter/dist/esm/styles/hljs";
import { useNavigate } from "react-router-dom";

interface MarkdownDivProps {
  markdown?: string;
  isRenderInline?: boolean;
}

const MarkdownHeading = (props: {
  level: number;
  children: React.ReactNode;
  isInline: boolean;
}) => {
  let variant: Variant;
  switch (props.level) {
    case 1:
      variant = "h4";
      break;
    case 2:
      variant = "h5";
      break;
    case 3:
      variant = "h6";
      break;
    case 4:
      variant = "subtitle1";
      break;
    case 5:
      variant = "subtitle2";
      break;
    case 6:
      variant = "body2";
      break;
    default:
      variant = "subtitle1";
  }
  return (
    <Typography variant={variant} gutterBottom={!props.isInline}>
      {props.children}
    </Typography>
  );
};

const MarkdownBlockquote = (props: {
  children: React.ReactNode;
  isInline: boolean;
}) => {
  if (props.isInline)
    return (
      <Typography
        variant="body1"
        sx={{
          fontStyle: "italic",
        }}
      >
        {(props.children ?? "").toString()}
      </Typography>
    );

  return (
    <Typography
      component="div"
      sx={{
        borderLeftWidth: "0.25rem",
        borderLeftStyle: "solid",
        borderLeftColor: (theme) => `${theme.palette.primary.main}80`,
        paddingLeft: "0.5rem",
      }}
    >
      {props.children}
    </Typography>
  );
};

const MarkdownCode: Components["code"] = ({
  children,
  className = "",
  node,
}) => {
  if (!node?.position || !children) {
    return <>{children}</>;
  }

  if (node.position.start.line == node.position.end.line) {
    return (
      <Typography
        component="span"
        sx={{
          fontFamily: "monospace",
          backgroundColor: (theme) =>
            theme.palette.mode === "light" ? "grey.100" : "grey.800",
          color: (theme) =>
            theme.palette.mode === "light"
              ? "grey.900"
              : theme.palette.warning.main,
          paddingX: "0.25rem",
          borderRadius: "0.25rem",
          whiteSpace: "pre-wrap",
        }}
      >
        {children}
      </Typography>
    );
  }

  const [, langauge] = className.split("-");
  return Array.isArray(children) ? (
    <>
      {children.map((child: any) => (
        <SyntaxHighlighter
          language={langauge || "plaintext"}
          style={monokai}
          showLineNumbers
          wrapLines
          wrapLongLines
          lineProps={{
            style: {
              wordBreak: "break-all",
              whiteSpace: "pre-wrap",
            },
          }}
        >
          {child.props.value}
        </SyntaxHighlighter>
      ))}
    </>
  ) : (
    <SyntaxHighlighter
      language={langauge || "plaintext"}
      style={monokai}
      showLineNumbers
      wrapLines
      wrapLongLines
      lineProps={{
        style: {
          wordBreak: "break-all",
          whiteSpace: "pre-wrap",
        },
      }}
    >
      {children as string}
    </SyntaxHighlighter>
  );
};

const MarkdownImage = (props: {
  src?: string;
  alt?: string;
  title?: string;
}) => {
  if (!props.src) return null;
  return (
    <Card variant="elevation" elevation={0}>
      <CardMedia
        component="img"
        image={props.src}
        alt={props.alt}
        title={props.title || props.alt}
        sx={{
          width: "auto",
          height: "auto",
          margin: "auto",
          maxWidth: "100%",
        }}
      />
    </Card>
  );
};

const MarkdownCheckbox = (props: { checked?: boolean; disabled?: boolean }) => {
  return (
    <Checkbox
      checked={props.checked}
      disabled={props.disabled}
      size="medium"
      sx={{
        padding: 0,
      }}
    />
  );
};

export default function MarkdownDiv(props: MarkdownDivProps) {
  const navigate = useNavigate();
  if (!props.markdown) return null;

  const isRenderInline = props.isRenderInline ?? false;
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm, remarkMath]}
      rehypePlugins={[
        rehypeRaw,
        [
          rehypeKatex,
          {
            output: "mathml",
          },
        ],
      ]}
      components={{
        p: "span",
        ul: (props) =>
          isRenderInline ? (
            <ul className="text-style">{props.children}</ul>
          ) : (
            <ul>{props.children}</ul>
          ),
        li: (props) =>
          isRenderInline ? (
            <li className="text-style">{props.children}</li>
          ) : (
            <li>{props.children}</li>
          ),
        ol: (props) =>
          isRenderInline ? (
            <ol className="text-style">{props.children}</ol>
          ) : (
            <ol>{props.children}</ol>
          ),
        h1: (props) => (
          <MarkdownHeading
            level={1}
            children={props.children}
            isInline={isRenderInline}
          />
        ),
        h2: (props) => (
          <MarkdownHeading
            level={2}
            children={props.children}
            isInline={isRenderInline}
          />
        ),
        h3: (props) => (
          <MarkdownHeading
            level={3}
            children={props.children}
            isInline={isRenderInline}
          />
        ),
        h4: (props) => (
          <MarkdownHeading
            level={4}
            children={props.children}
            isInline={isRenderInline}
          />
        ),
        h5: (props) => (
          <MarkdownHeading
            level={5}
            children={props.children}
            isInline={isRenderInline}
          />
        ),
        h6: (props) => (
          <MarkdownHeading
            level={6}
            children={props.children}
            isInline={isRenderInline}
          />
        ),
        a: (props) =>
          props.href?.startsWith("/") ? (
            <Link
              component="button"
              onClick={() => {
                navigate(`${props.href}`);
              }}
              color="inherit"
            >
              {props.children}
            </Link>
          ) : (
            <Link
              href={props.href}
              target="_blank"
              rel="noopener noreferrer"
              color="inherit"
            >
              {props.children}
            </Link>
          ),
        blockquote: (props) => (
          <MarkdownBlockquote
            children={props.children}
            isInline={isRenderInline}
          />
        ),
        code: MarkdownCode,
        em: (props) => (
          <Typography
            component="span"
            sx={{
              fontStyle: "italic",
            }}
          >
            {props.children}
          </Typography>
        ),
        hr: () => <Divider />,
        img: (props) => (
          <MarkdownImage src={props.src} alt={props.alt} title={props.title} />
        ),
        strong: (props) => (
          <Typography
            component="span"
            sx={{
              fontWeight: "bold",
            }}
          >
            {props.children}
          </Typography>
        ),
        del: (props) => (
          <Typography
            component="span"
            sx={{
              textDecoration: "line-through",
            }}
          >
            {props.children}
          </Typography>
        ),
        input: (props) => (
          <MarkdownCheckbox disabled={props.disabled} checked={props.checked} />
        ),
        thead: TableHead as any,
        tbody: TableBody as any,
        th: TableCell as any,
        tr: TableRow as any,
        td: TableCell as any,
        table: (props) => (
          <TableContainer component={Paper} elevation={0}>
            <Table {...(props as any)} size="small" />
          </TableContainer>
        ),
      }}
    >
      {props.markdown}
    </ReactMarkdown>
  );
}
