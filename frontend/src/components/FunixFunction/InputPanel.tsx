import {
  Button,
  CardContent,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  Grid,
} from "@mui/material";
import Card from "@mui/material/Card"; // eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import Form from "@rjsf/material-ui/v5";
import React, { useEffect, useState } from "react";
import {
  callFunctionRaw,
  FunctionDetail,
  FunctionPreview,
  UpdateResult,
} from "../../shared";
import ObjectFieldExtendedTemplate from "./ObjectFieldExtendedTemplate";
import SwitchWidget from "./SwitchWidget";
import TextExtendedWidget from "./TextExtendedWidget";
import { useAtom } from "jotai";
import { storeAtom } from "../../store";
import useFunixHistory from "../../shared/useFunixHistory";
import { useSnackbar } from "notistack";
import _ from "lodash";

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
  const [
    { functionSecret, backHistory, backConsensus, saveHistory, appSecret },
    setStore,
  ] = useAtom(storeAtom);
  const { setInput, setOutput } = useFunixHistory();
  const { enqueueSnackbar } = useSnackbar();

  const [tempOutput, setTempOutput] = useState<string | null>(null);

  useEffect(() => {
    setWaiting(() => !requestDone);
  }, [asyncWaiting]);

  useEffect(() => {
    if (backHistory === null) return;
    if (backHistory.input !== null) {
      setForm(backHistory.input);
      window.dispatchEvent(new CustomEvent("funix-rollback-now"));
      setStore((store) => {
        const newBackConsensus = [...store.backConsensus];
        newBackConsensus[2] = true;
        return {
          ...store,
          backConsensus: newBackConsensus,
        };
      });
    }
  }, [backHistory]);

  useEffect(() => {
    if (backConsensus.every((v) => v)) {
      setStore((store) => ({
        ...store,
        backConsensus: [false, false, false],
        backHistory: null,
      }));
    }
  }, [backConsensus]);

  const handleChange = ({ formData }: Record<string, any>) => {
    // console.log("Data changed: ", formData);
    setForm(formData);

    if (!props.preview.reactive) {
      return;
    }

    _.debounce(() => {
      fetch(new URL(`/update/${props.preview.id}`, props.backend), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })
        .then((body) => {
          return body.json();
        })
        .then((data: UpdateResult) => {
          const result = data.result;

          if (result !== null) {
            for (const [key, value] of Object.entries(result)) {
              setForm((form) => {
                return {
                  ...form,
                  [key]: value,
                };
              });
            }
          }
        });
    }, 100)();
  };

  const saveOutput = async (
    now: number,
    name: string,
    path: string,
    output: string
  ) => {
    try {
      await setOutput(now, name, path, output);
    } catch (e) {
      enqueueSnackbar(
        "Cannot save output to history, check your console for more information",
        {
          variant: "error",
        }
      );
      console.error("Funix History Error:");
      console.error(e);
    }
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

  const checkResponse = async () => {
    setTimeout(() => {
      setAsyncWaiting((asyncWaiting) => !asyncWaiting);
    }, 300);
  };

  const handleSubmit = async () => {
    const now = new Date().getTime();
    const newForm = props.preview.secret
      ? props.preview.name in functionSecret &&
        functionSecret[props.preview.path] !== null
        ? {
            ...form,
            __funix_secret: functionSecret[props.preview.path],
          }
        : appSecret !== null
        ? {
            ...form,
            __funix_secret: appSecret,
          }
        : form
      : form;
    const isLarge =
      Object.values(props.detail.schema.properties).findIndex((value) => {
        const newValue = value as unknown as any;
        const largeWidgets = ["image", "video", "audio", "file"];
        if ("items" in newValue) {
          return largeWidgets.includes(newValue.items.widget);
        } else {
          return largeWidgets.includes(newValue.widget);
        }
      }) !== -1;

    if (saveHistory && !isLarge) {
      try {
        await setInput(now, props.preview.name, props.preview.path, newForm);
      } catch (error) {
        enqueueSnackbar(
          "Cannot save input to history, check your console for more information",
          {
            variant: "error",
          }
        );
        console.error("Funix History Error:");
        console.error(error);
      }
    }
    // console.log("Data submitted: ", newForm);
    setRequestDone(() => false);
    checkResponse().then();
    if (props.preview.websocket) {
      const websocketUrl =
        props.backend.protocol === "https:"
          ? "wss"
          : "ws" + "://" + props.backend.host + "/call/" + props.detail.id;
      const socket = new WebSocket(websocketUrl);
      socket.addEventListener("open", function () {
        socket.send(JSON.stringify(newForm));
      });

      socket.addEventListener("message", function (event) {
        props.setResponse(() => event.data);
        setTempOutput(() => event.data);
      });

      socket.addEventListener("close", async function () {
        setWaiting(() => false);
        setRequestDone(() => true);
        if (saveHistory && tempOutput) {
          await saveOutput(
            now,
            props.preview.name,
            props.preview.path,
            tempOutput
          );
        }
      });
    } else {
      const response = await callFunctionRaw(
        new URL(`/call/${props.detail.id}`, props.backend),
        newForm
      );
      const result = response.toString();
      props.setResponse(() => result);
      setWaiting(() => false);
      setRequestDone(() => true);

      if (saveHistory) {
        await saveOutput(now, props.preview.name, props.preview.path, result);
      }
    }
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
        <Form
          schema={props.detail.schema}
          formData={form}
          onChange={handleChange}
          widgets={widgets}
          uiSchema={uiSchema}
          safeRenderCompletion
        />
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
