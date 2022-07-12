import React from "react";
import { FunctionDetail, FunctionPreview } from "@textea/shared";
import { Card, CardContent, Divider, Typography } from "@mui/material";
import ReactJson from "react-json-view";
import useSWR from "swr";
import { localApiURL } from "../../shared";
import TexteaFunctionCallerCard from "./TexteaFunctionCallerCard";

export type FunctionDetailProps = {
  preview: FunctionPreview;
};

export const TexteaFunction: React.FC<FunctionDetailProps> = ({ preview }) => {
  const { data: detail } = useSWR<FunctionDetail>(
    new URL(preview.path, localApiURL).toString()
  );
  if (!detail) {
    return <Typography>Cannot fetch function detail</Typography>;
  }
  return (
    <>
      <Card>
        <CardContent>
          <Typography variant="h5" component="div">
            {detail.name}
          </Typography>
          <Typography sx={{ mb: 1.5 }} color="text.secondary">
            {new URL(detail.callee, localApiURL).toString()}
          </Typography>
          <Divider />
          <Typography variant="body2">Param</Typography>
          <ReactJson src={detail.params} />
        </CardContent>
      </Card>
      <TexteaFunctionCallerCard detail={detail} />
    </>
  );
};
