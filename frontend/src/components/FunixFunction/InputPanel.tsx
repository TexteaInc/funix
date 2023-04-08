import {
  Button,
  CardContent,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  Grid,
} from "@mui/material";
import Card from "@mui/material/Card";
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import Form from "@rjsf/material-ui/v5";
import React, { useEffect, useState } from "react";
import { callFunctionRaw, FunctionDetail, FunctionPreview } from "../../shared";
import ObjectFieldExtendedTemplate from "./ObjectFieldExtendedTemplate";
import SwitchWidget from "./SwitchWidget";
import TextExtendedWidget from "./TextExtendedWidget";
import { useAtom } from "jotai";
import { storeAtom } from "../../store";

const InputPanel = (props: {
  detail: FunctionDetail;
  backend: URL;
  setResponse: React.Dispatch<React.SetStateAction<string | null>>;
  preview: FunctionPreview;
}) => {
  const [form, setForm] = useState<Record<string, any>>({});
  const [waiting, setWaiting] = useState(false);
  const [asyncWaiting, setAsyncWaiting] = useState(false);
  const [requestDone, setRequestDone] = useState(true);
  const [{ functionSecret }] = useAtom(storeAtom);

  useEffect(() => {
    setWaiting(() => !requestDone);
  }, [asyncWaiting]);

  const handleChange = ({ formData }: Record<string, any>) => {
    // console.log("Data changed: ", formData);
    setForm(formData);
  };

  const widgets = {
    TextWidget: TextExtendedWidget,
    CheckboxWidget: SwitchWidget,
  };

  const uiSchema = {
    "ui:ObjectFieldTemplate": ObjectFieldExtendedTemplate,
    "ui:submitButtonOptions": {
      norender: true,
    },
  };

  const formElement = (
    <Form
      schema={props.detail.schema}
      formData={form}
      onChange={handleChange}
      widgets={widgets}
      uiSchema={uiSchema}
      safeRenderCompletion
    />
  );

  const checkResponse = async () => {
    setTimeout(() => {
      setAsyncWaiting((asyncWaiting) => !asyncWaiting);
    }, 300);
  };

  const handleSubmit = async () => {
    let newForm = form;
    if (props.preview.secret) {
      if (
        props.preview.name in functionSecret &&
        typeof functionSecret[props.preview.name] === "string"
      ) {
        newForm = {
          ...form,
          __funix_secret: functionSecret[props.preview.name],
        };
      }
    }
    console.log("Data submitted: ", newForm);
    setRequestDone(() => false);
    checkResponse().then();
    const response = await callFunctionRaw(
      new URL(`/call/${props.detail.id}`, props.backend),
      newForm
    );
    props.setResponse(() => response.toString());
    setWaiting(() => false);
    setRequestDone(() => true);
  };

  return (
    <Card
      onKeyDown={(event) => {
        if (event.ctrlKey && event.key === "Enter") {
          handleSubmit().then();
        }
      }}
    >
      <CardContent
        sx={{
          paddingY: 1,
        }}
      >
        {formElement}
        <Grid
          container
          spacing={2}
          direction="row"
          justifyContent="center"
          alignItems="center"
        >
          <Grid item xs>
            <FormControlLabel
              control={<Checkbox defaultChecked={false} disabled />}
              label="Continuously Run"
            />
          </Grid>
          <Grid item>
            <Button
              variant="contained"
              size="large"
              onClick={handleSubmit}
              sx={{ mt: 1 }}
              disabled={waiting}
              startIcon={
                waiting && <CircularProgress size={20} color="inherit" />
              }
            >
              Run
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default React.memo(InputPanel, (prevProps, nextProps) => {
  return (
    prevProps.detail === nextProps.detail &&
    prevProps.backend === nextProps.backend &&
    prevProps.setResponse === nextProps.setResponse
  );
});
