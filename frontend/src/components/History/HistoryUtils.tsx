import { History } from "../../shared/useFunixHistory";
import { Step, StepLabel, Stepper } from "@mui/material";
import { Done, Error, Pending, QuestionMark } from "@mui/icons-material";

export enum HistoryEnum {
  // No input and/nor no output
  Unknown,
  // Just input
  Pending,
  // Input and output
  Done,
  // Error
  Error,
}

export type HistoryInfoProps = {
  status: HistoryEnum;
  hasSecret: boolean;
};

export const getHistoryInfo = (history: History): HistoryInfoProps => {
  let status: HistoryEnum;

  if (history.input === null) {
    status = HistoryEnum.Unknown;
  } else {
    if (history.output === null) {
      status = HistoryEnum.Pending;
    } else {
      status = HistoryEnum.Done;
    }
  }

  const hasSecret =
    history.input !== null ? "__funix_secret" in history.input : false;
  if (history.output !== null) {
    try {
      let output = history.output;
      if (typeof history.output === "string") {
        output = JSON.parse(history.output);
      }
      if (output.hasOwnProperty("error_body")) {
        status = HistoryEnum.Error;
      }
    } catch {
      // Do nothing
    }
  }
  return {
    status,
    hasSecret,
  };
};

export const FunixHistoryStepper = (props: { status: HistoryEnum }) => {
  const activeStep =
    props.status === HistoryEnum.Done || props.status === HistoryEnum.Error
      ? 2
      : props.status === HistoryEnum.Pending
      ? 1
      : 0;
  return (
    <Stepper
      activeStep={activeStep}
      sx={{
        paddingBottom: 2,
      }}
    >
      <Step>
        <StepLabel>Input</StepLabel>
      </Step>

      <Step>
        <StepLabel error={props.status === HistoryEnum.Error}>Output</StepLabel>
      </Step>
    </Stepper>
  );
};

export const getHistoryStatusColor = (status: HistoryEnum) => {
  return status === HistoryEnum.Done
    ? "success"
    : status === HistoryEnum.Error
    ? "error"
    : "primary";
};

export const getHistoryStatusIcon = (status: HistoryEnum) => {
  return status === HistoryEnum.Done ? (
    <Done />
  ) : status === HistoryEnum.Error ? (
    <Error />
  ) : status === HistoryEnum.Pending ? (
    <Pending />
  ) : (
    <QuestionMark />
  );
};
