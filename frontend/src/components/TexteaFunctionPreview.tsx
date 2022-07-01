import { useStore } from "../store";
import { Stack, Box, Typography } from "@mui/material";
import React, { useMemo } from "react";
import { markdown } from "../shared";
import ReactJson from "react-json-view";

type PreviewProps = {
  name: string;
  description: string;
};
export const Preview: React.FC<PreviewProps> = (props) => {
  const { name, description } = props;
  const html = useMemo(() => markdown.render(description), [description]);
  return (
    <Stack spacing={1}>
      <Typography variant="h4">{name}</Typography>
      <Box dangerouslySetInnerHTML={{ __html: html }} />
      <Typography variant="h5">data preview</Typography>
      <ReactJson src={props} />
    </Stack>
  );
};

export const TexteaFunctionPreview: React.FC = () => {
  const selected = useStore((store) => store.selectedFunction);
  if (!selected) {
    return <Typography variant="h5">No selected function</Typography>;
  }
  return <Preview {...selected} />;
};
