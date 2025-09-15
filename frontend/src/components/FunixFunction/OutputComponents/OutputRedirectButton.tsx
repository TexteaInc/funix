import { useAtom } from "jotai";
import { callableDefaultAtom } from "../../../store";
import { useNavigate } from "react-router-dom";
import Button from "@mui/material/Button";
import { useCallback, useEffect, useMemo } from "react";

type RedirectButtonResponse = {
  path: string;
  args: string;
  text: string;
  auto_direct: boolean;
};

interface OutputRedirectButtonProps {
  response: RedirectButtonResponse;
}

const OutputRedirectButton = (props: OutputRedirectButtonProps) => {
  const [callableDefault, setCallableDefault] = useAtom(callableDefaultAtom);
  const navigate = useNavigate();
  const { response } = props;

  const parsedArgs = useMemo(() => {
    try {
      return JSON.parse(response.args);
    } catch (error) {
      console.error("Failed to parse args:", error);
      return {};
    }
  }, [response.args]);

  const toPath = useCallback(() => {
    const newCallableDefault = { ...callableDefault };
    newCallableDefault[response.path] = parsedArgs;
    setCallableDefault(newCallableDefault);
    navigate(response.path);
  }, [
    callableDefault,
    parsedArgs,
    response.path,
    setCallableDefault,
    navigate,
  ]);

  useEffect(() => {
    if (response.auto_direct) {
      toPath();
    }
  }, [response.auto_direct, toPath]);

  return (
    <Button variant="contained" onClick={toPath} sx={{ width: "100%" }}>
      {response.text}
    </Button>
  );
};

export default OutputRedirectButton;
