import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  Card,
  CardContent,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
} from "@mui/material";
import { storeAtom } from "../store";
import { useAtom } from "jotai";
import { FunctionPreview, getList } from "../shared";

export type FunctionListProps = {
  backend: URL;
};

const TexteaFunctionList: React.FC<FunctionListProps> = ({ backend }) => {
  const [, setStore] = useAtom(storeAtom);
  const onceRef = useRef(true);
  const [state, setState] = useState<FunctionPreview[]>([]);
  useEffect(() => {
    async function queryData() {
      const { list } = await getList(new URL("/list", backend));
      setState(list);
      if (list.length >= 1) {
        handleFetchFunctionDetail(list[0]);
        setRadioGroupValue(list[0].name);
      }
    }
    if (onceRef.current) {
      queryData().then();
      onceRef.current = false;
    }
  }, []);

  const handleFetchFunctionDetail = useCallback(
    (functionPreview: FunctionPreview) => {
      setStore((store) => ({
        ...store,
        selectedFunction: functionPreview,
      }));
    },
    []
  );

  const [radioGroupValue, setRadioGroupValue] = useState<string | null>(null);

  const handleRadioGroupChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const functionName: string | null = e.currentTarget.value;
    const selectedFunctionPreview = state.filter(
      (preview) => preview.name === functionName
    );
    if (selectedFunctionPreview.length != 1) {
      setRadioGroupValue(null);
    } else {
      handleFetchFunctionDetail(selectedFunctionPreview[0]);
      setRadioGroupValue(functionName);
    }
  };

  return (
    <Card>
      <CardContent>
        <FormControl>
          <FormLabel id="function-list-radio-group-label">Function</FormLabel>
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

export default TexteaFunctionList;
