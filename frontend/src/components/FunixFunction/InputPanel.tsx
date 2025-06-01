import {
  Button,
  CardContent,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  Grid,
  Typography,
} from "@mui/material";
import Card from "@mui/material/Card";
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
import { Form } from "@rjsf/mui";
import validator from "@rjsf/validator-ajv8";
import { RJSFSchema } from "@rjsf/utils";

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
      showFunctionTitle,
      callableDefault,
      theme,
    },
    setStore,
  ] = useAtom(storeAtom);
  const { setInputOutput } = useFunixHistory();
  const { enqueueSnackbar } = useSnackbar();

  const [tempOutput, setTempOutput] = useState<string | null>(null);
  const tempOutputRef = React.useRef<string | null>(null);
  const [autoRun, setAutoRun] = useState(
    props.preview.autorun === "always" || props.preview.autorun === "toggleable"
      ? true
      : false,
  );
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

    if (callableDefault !== null && props.preview.path in callableDefault) {
      setForm(callableDefault[props.preview.path]);
      if (
        (props.preview.autorun === "always" ||
          props.preview.autorun === "toggleable") &&
        autoRun
      ) {
        handleSubmitWithoutHistory(callableDefault[props.preview.path]).then();
      }
      setStore((store) => {
        const newCallableDefault = { ...store.callableDefault };
        delete newCallableDefault[props.preview.path];
        return {
          ...store,
          callableDefault: newCallableDefault,
        };
      });
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
    setForm(formData);

    if (props.preview.reactive) {
      _.debounce(() => {
        fetch(new URL(`/update/${props.preview.id}`, props.backend), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
          credentials: "include",
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

    if (
      (props.preview.autorun === "always" ||
        props.preview.autorun === "toggleable") &&
      autoRun
    ) {
      _.debounce(() => {
        handleSubmitWithoutHistory(formData).then();
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
      ? props.preview.path in functionSecret &&
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

  const handleSubmitWithoutHistory = async (
    form: Record<string, any> | undefined = undefined,
  ) => {
    const newForm = form ? form : getNewForm();
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
        newForm,
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
                currentOutput,
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
        newForm,
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
            result,
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
        {showFunctionTitle && (
          <Typography
            variant="h5"
            sx={{
              marginBottom: 2,
            }}
          >
            {props.preview.name}
          </Typography>
        )}
        <Form
          validator={validator}
          schema={props.detail.schema as RJSFSchema}
          formData={form}
          onChange={handleChange}
          widgets={widgets}
          uiSchema={uiSchema}
          formContext={{
            advancedExamples: props.detail.schema.advanced_examples,
            form: form,
          }}
        />
        <Grid
          container
          spacing={2}
          direction="row"
          justifyContent="center"
          alignItems="center"
        >
          <Grid item xs>
            {props.preview.autorun === "toggleable" && (
              <FormControlLabel
                control={
                  <Checkbox
                    value={autoRun}
                    onChange={(event) => {
                      setAutoRun(() => event.target.checked);
                    }}
                    defaultChecked={true}
                  />
                }
                label={theme?.funix_autorun_label || "Auto-run"}
              />
            )}
          </Grid>
          <Grid item>
            {props.preview.autorun !== "always" && (
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
                {theme?.funix_run_button || "Run"}
              </Button>
            )}
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
