import React, { SyntheticEvent, useState } from "react";
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import Form from "@rjsf/material-ui/v5";
import { callFunctionRaw, FunctionDetail, FunctionPreview } from "../../shared";
import useSWR from "swr";
import { localApiURL } from "../../constants";
import { Card, CardContent, Stack, Typography } from "@mui/material";
import ReactJson from "react-json-view";
import TextExtendedWidget from "./TextExtendedWidget";

export type FunctionDetailProps = {
  preview: FunctionPreview;
};

const TexteaFunction: React.FC<FunctionDetailProps> = ({ preview }) => {
  const { data: detail } = useSWR<FunctionDetail>(
    new URL(`/param/${preview.path}`, localApiURL).toString()
  );
  const [form, setForm] = useState<Record<string, any>>({});
  const [response, setResponse] = useState<string | null>(null);

  if (detail == null) {
    console.log("Failed to display function detail");
    return <div />;
  }

  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const functionDetail = detail!;

  const onSubmit = async (
    { formData }: Record<string, any>,
    e: SyntheticEvent
  ) => {
    setForm(formData);
    console.log("Data submitted: ", formData);
    console.log("Event: ", e);
    const response = await callFunctionRaw(
      new URL(`/call/${functionDetail.id}`, localApiURL),
      {
        ...formData,
      }
    );
    setResponse(response.toString());
  };

  const widgets = {
    TextWidget: TextExtendedWidget,
  };

  type ResponseViewProps = {
    response: string | null;
  };

  const ResponseView: React.FC<ResponseViewProps> = ({ response }) => {
    if (response == null) {
      return (
        <Typography variant="body1">
          Execute the function first to see response here
        </Typography>
      );
    } else {
      try {
        const parsedResponse = JSON.parse(response);
        return <ReactJson src={parsedResponse ?? {}} />;
      } catch (e) {
        return <code>{response ?? ""}</code>;
      }
    }
  };

  return (
    <Stack spacing={2}>
      <Card>
        <CardContent>
          <Form
            schema={functionDetail.schema}
            formData={form}
            onSubmit={onSubmit}
            widgets={widgets}
          />
        </CardContent>
      </Card>
      <Card>
        <CardContent>
          <Typography variant="h5">Response</Typography>
          <ResponseView response={response} />
        </CardContent>
      </Card>
      <Card>
        <CardContent>
          <Typography variant="h5">Function Detail</Typography>
          <ReactJson src={functionDetail} collapsed />
        </CardContent>
      </Card>
    </Stack>
  );
};

export default TexteaFunction;
