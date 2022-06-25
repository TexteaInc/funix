import { Card, CardContent, Divider, Stack, Typography } from "@mui/material";
import React from "react";

export interface TexteaFunctionInfoWindowProps {
  functionName: string;
  functionParams: any;
}

export default function TexteaFunctionInfoCard(
  props: TexteaFunctionInfoWindowProps
) {
  return (
    <Card>
      <CardContent>
        <Stack spacing={1}>
          <Typography variant="h4">Function Info</Typography>
          <Divider />
          <Typography variant="body1">
            Function Name:&nbsp;
            <code>{props.functionName}</code>
          </Typography>
          <Typography variant="body1">
            Function Param:&nbsp;
            <code>{JSON.stringify(props.functionParams ?? {}, null, 1)}</code>
          </Typography>
          <Typography variant="body1">
            Function Path:&nbsp;
            <code>{props.functionParams?.path}</code>
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
