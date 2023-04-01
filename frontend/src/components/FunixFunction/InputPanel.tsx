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
import { callFunctionRaw, FunctionDetail } from "../../shared";
import ObjectFieldExtendedTemplate from "./ObjectFieldExtendedTemplate";
import SwitchWidget from "./SwitchWidget";
import TextExtendedWidget from "./TextExtendedWidget";

const InputPanel = (props: {
  detail: FunctionDetail;
  backend: URL;
  setResponse: React.Dispatch<React.SetStateAction<string | null>>;
}) => {
  const [form, setForm] = useState<Record<string, any>>({});
  const [waiting, setWaiting] = useState(false);
  const [asyncWaiting, setAsyncWaiting] = useState(false);
  const [requestDone, setRequestDone] = useState(true);

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
    />
  );

  const checkResponse = async () => {
    setTimeout(() => {
      setAsyncWaiting((asyncWaiting) => !asyncWaiting);
    }, 300);
  };

  const handleSubmit = async () => {
    console.log("Data submitted: ", form);
    setRequestDone(() => false);
    checkResponse().then();
    const response = await callFunctionRaw(
      new URL(`/call/${props.detail.id}`, props.backend),
      form
    );
    props.setResponse(() => response.toString());
    setWaiting(() => false);
    setRequestDone(() => true);
  };

  return (
    <Card>
      <CardContent>
        {formElement}
        <Grid
          container
          spacing={2}
          direction="row"
          justifyContent="center"
          alignItems="center"
        >
          <Grid item xs>
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
          <Grid item>
            <FormControlLabel
              control={<Checkbox defaultChecked={false} disabled />}
              label="Continuous run"
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default InputPanel;
