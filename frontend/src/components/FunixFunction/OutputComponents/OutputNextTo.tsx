import { useAtom } from "jotai";
import { callableDefaultAtom } from "../../../store";
import { useNavigate } from "react-router-dom";
import { useCallback, useEffect } from "react";

interface OutputNextToProps {
  response: string;
}

type NextToResponse = {
  args: any;
  path: string;
};

const OutputNextTo = (props: OutputNextToProps) => {
  const response = JSON.parse(props.response) as NextToResponse;
  const [callableDefault, setCallableDefault] = useAtom(callableDefaultAtom);
  const navigate = useNavigate();

  const toPath = useCallback(() => {
    const newCallableDefault = { ...callableDefault };
    newCallableDefault[response.path] = response.args;
    setCallableDefault(newCallableDefault);
    navigate(response.path);
  }, [
    callableDefault,
    response.args,
    response.path,
    setCallableDefault,
    navigate,
  ]);

  useEffect(() => {
    toPath();
  }, [toPath]);
  return <></>;
};

export default OutputNextTo;
