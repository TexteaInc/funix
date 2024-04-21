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
import React, { useEffect, useRef, useState } from "react";
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
  setOutdated: React.Dispatch<React.SetStateAction<boolean>>;
  preview: FunctionPreview;
}) => {
  const [form, setForm] = useState<Record<string, any>>({});
  const [waiting, setWaiting] = useState(false);
  const [asyncWaiting, setAsyncWaiting] = useState(false);
  const [requestDone, setRequestDone] = useState(true);
  const [
    {
      functionSecret,
      backHistory,
      backConsensus,
      saveHistory,
      appSecret,
      last,
    },
    setStore,
  ] = useAtom(storeAtom);
  const { setInputOutput } = useFunixHistory();
  const { enqueueSnackbar } = useSnackbar();

  const [tempOutput, setTempOutput] = useState<string | null>(null);
  const tempOutputRef = React.useRef<string | null>(null);
  const [autoRun, setAutoRun] = useState(false);
  const lock = useRef(false);

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

  useEffect(() => {
    if (lock.current) return;
    lock.current = true;
    if (props.preview.keepLast && props.preview.id in last) {
      setForm(last[props.preview.id].input);
    }
  }, []);

  useEffect(() => {
    setWaiting(() => !requestDone);
  }, [asyncWaiting]);

  useEffect(() => {
    tempOutputRef.current = tempOutput;
  }, [tempOutput]);

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

    if (props.preview.reactive) {
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
    }

    if (props.preview.autorun && autoRun) {
      _.debounce(() => {
        handleSubmitWithoutHistory().then();
      }, 100)();
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

  const getNewForm = () => {
    return props.preview.secret
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
  };

  const getWebsocketUrl = () => {
    return (
      (props.backend.protocol === "https:" ? "wss" : "ws") +
      "://" +
      props.backend.host +
      "/call/" +
      props.detail.id
    );
  };

  const handleSubmitWithoutHistory = async () => {
    const newForm = getNewForm();
    setRequestDone(() => false);
    checkResponse().then();
    if (props.preview.websocket) {
      const socket = new WebSocket(getWebsocketUrl());
      socket.addEventListener("open", function () {
        socket.send(JSON.stringify(newForm));
        props.setOutdated(() => false);
      });

      socket.addEventListener("message", function (event) {
        props.setResponse(() => event.data);
        props.setOutdated(() => false);
        setTempOutput(() => event.data);
      });

      socket.addEventListener("close", async function () {
        setWaiting(() => false);
        setRequestDone(() => true);
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
    }
  };

  const handleSubmit = async () => {
    const now = new Date().getTime();
    const newForm = getNewForm();

    setRequestDone(() => false);
    checkResponse().then();
    if (props.preview.websocket) {
      const socket = new WebSocket(getWebsocketUrl());
      socket.addEventListener("open", function () {
        setTempOutput(() => null);
        socket.send(JSON.stringify(newForm));
        props.setOutdated(() => false);
      });

      socket.addEventListener("message", function (event) {
        const data = structuredClone(event.data);
        props.setResponse(() => data);
        setTempOutput(() => data);
      });

      socket.addEventListener("close", async function () {
        setWaiting(() => false);
        setRequestDone(() => true);
        if (tempOutputRef.current !== null) {
          const currentOutput = tempOutputRef.current;
          setStore((store) => {
            const newLast = { ...store.last };
            newLast[props.preview.id] = {
              input: newForm,
              output: JSON.parse(currentOutput),
            };
            return {
              ...store,
              last: newLast,
            };
          });

          if (saveHistory && !isLarge) {
            try {
              await setInputOutput(
                now,
                props.preview.name,
                props.preview.path,
                newForm,
                currentOutput
              );
            } catch (e) {
              enqueueSnackbar("Failed to save history, check your console", {
                variant: "error",
              });
              console.error(e);
            }
          }
        }
      });
    } else {
      const response = await callFunctionRaw(
        new URL(`/call/${props.detail.id}`, props.backend),
        newForm
      );
      const result = response.toString();
      props.setResponse(() => result);
      props.setOutdated(() => false);
      setWaiting(() => false);
      setRequestDone(() => true);

      setStore((store) => {
        const newLast = { ...store.last };
        newLast[props.preview.id] = {
          input: newForm,
          output: JSON.parse(result),
        };
        return {
          ...store,
          last: newLast,
        };
      });

      if (saveHistory && !isLarge) {
        try {
          await setInputOutput(
            now,
            props.preview.name,
            props.preview.path,
            newForm,
            result
          );
        } catch (e) {
          enqueueSnackbar("Failed to save history, check your console", {
            variant: "error",
          });
          console.error(e);
        }
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
              control={
                <Checkbox
                  defaultChecked={false}
                  value={autoRun}
                  onChange={(event) => {
                    setAutoRun(() => event.target.checked);
                  }}
                  disabled={!props.preview.autorun}
                />
              }
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
    prevProps.setResponse === nextProps.setResponse &&
    prevProps.setOutdated === nextProps.setOutdated
  );
});
