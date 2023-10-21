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
  useTheme,
} from "@mui/material";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import React from "react";
import { Variant } from "@mui/material/styles/createTypography";
import Editor from "@monaco-editor/react";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

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

const MarkdownCode = (props: {
  children: React.ReactNode;
  inline?: boolean;
  className?: string;
}) => {
  const theme = useTheme();

  if (props.inline) {
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
        }}
      >
        {props.children}
      </Typography>
    );
  }

  const language = props.className
    ? props.className.startsWith("```")
      ? props.className.substring(3)
      : props.className.startsWith("language-")
      ? props.className.substring(9)
      : "plaintext"
    : "plaintext";

  return (
    <Editor
      width="100%"
      value={(props.children ?? "").toString()}
      language={language}
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
        pre: React.Fragment,
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
        a: (props) => (
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
        code: (props) => (
          <MarkdownCode
            children={props.children}
            inline={props.inline}
            className={props.className}
          />
        ),
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
        thead: TableHead,
        tbody: TableBody,
        th: TableCell as any,
        tr: TableRow,
        td: TableCell as any,
        table: (props) => (
          <TableContainer component={Paper} elevation={0}>
            <Table {...props} size="small" />
          </TableContainer>
        ),
      }}
    >
      {props.markdown}
    </ReactMarkdown>
  );
}
