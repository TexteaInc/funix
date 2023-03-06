import React, { useCallback, useEffect, useState } from "react";
import {
  Card,
  CardContent,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
  Typography,
} from "@mui/material";
import { storeAtom } from "../store";
import { useAtom } from "jotai";
import { FunctionPreview, getList } from "../shared";
import { useNavigate, useLocation } from "react-router-dom";

export type FunctionListProps = {
  backend: URL;
};
const FunixFunctionList: React.FC<FunctionListProps> = ({ backend }) => {
  const [, setStore] = useAtom(storeAtom);
  const [state, setState] = useState<FunctionPreview[]>([]);
  const [radioGroupValue, setRadioGroupValue] = useState<string | null>(null);
  const [url, setURL] = useState("");
  const { pathname } = useLocation();
  const navigate = useNavigate();

  const handleFetchFunctionDetail = useCallback(
    (functionPreview: FunctionPreview) => {
      setStore((store) => ({
        ...store,
        selectedFunction: functionPreview,
      }));
    },
    []
  );

  useEffect(() => {
    if (backend.origin === url) return;
    setStore((store) => ({
      ...store,
      selectedFunction: null,
    }));
    setRadioGroupValue(null);
    async function queryData() {
      const { list } = await getList(new URL("/list", backend));
      setState(list);
      if (list.length === 1) {
        handleFetchFunctionDetail(list[0]);
        setRadioGroupValue(list[0].name);
      }
    }
    queryData().then();
    setURL(backend.origin);
  }, [backend, url]);

  const handleRadioGroupChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const functionName: string | null = e.currentTarget.value;
    const selectedFunctionPreview = state.filter(
      (preview) => preview.name === functionName
    );
    if (selectedFunctionPreview.length !== 1) {
      setRadioGroupValue(null);
    } else {
      navigate(`/${selectedFunctionPreview[0].name}`);
      handleFetchFunctionDetail(selectedFunctionPreview[0]);
      setRadioGroupValue(functionName);
    }
  };

  useEffect(() => {
    const pathParams = pathname.split("/").filter((value) => value !== "");
    if (
      pathParams.length !== 0 &&
      state.length !== 0 &&
      pathParams[0] !== radioGroupValue
    ) {
      const functionName = decodeURIComponent(pathParams[0]);
      const selectedFunctionPreview = state.filter(
        (preview) => preview.name === functionName
      );
      if (selectedFunctionPreview.length !== 0) {
        setStore((store) => ({
          ...store,
          selectedFunction: selectedFunctionPreview[0],
        }));
        setRadioGroupValue(functionName);
      }
    }
  }, [pathname, state]);

  if (state.length === 1) return <></>;

  return (
    <Card>
      <CardContent>
        <FormControl>
          <FormLabel id="function-list-radio-group-label">
            <Typography>Select a function/page:</Typography>
          </FormLabel>
          <RadioGroup
            aria-labelledby="function-list-radio-group-label"
            name="function-list-radio-group"
            value={radioGroupValue}
            onChange={handleRadioGroupChange}
            row
          >
            {state.map((preview) => (
              <FormControlLabel
                value={preview.name}
                control={<Radio />}
                label={preview.name}
              />
            ))}
          </RadioGroup>
        </FormControl>
      </CardContent>
    </Card>
  );
};

export default React.memo(FunixFunctionList);
