import React, { useCallback, useEffect, useState } from "react";
import {
  Card,
  CardContent,
  Collapse,
  FormControl,
  FormControlLabel,
  FormLabel,
  List,
  ListItemButton,
  ListItemText,
  ListSubheader,
  Radio,
  RadioGroup,
  Typography,
} from "@mui/material";
import { storeAtom } from "../store";
import { useAtom } from "jotai";
import { FunctionPreview, getList } from "../shared";
import { useNavigate, useLocation } from "react-router-dom";
import { ExpandLess, ExpandMore } from "@mui/icons-material";

export type FunctionListProps = {
  backend: URL;
};

const FunixFunctionTreeOrList = (props: {
  functions: FunctionPreview[];
  value: string | null;
  onChange: (event: React.ChangeEvent<HTMLInputElement>, value: string) => void;
  setResponse: (functionName: string) => void;
}) => {
  const needTree = props.functions.some((f) => typeof f.module === "string");
  if (!needTree) {
    return (
      <FormControl>
        <FormLabel id="function-list-radio-group-label">
          <Typography>Select a function/page:</Typography>
        </FormLabel>
        <RadioGroup
          aria-labelledby="function-list-radio-group-label"
          name="function-list-radio-group"
          value={props.value}
          onChange={props.onChange}
          row
        >
          {props.functions.map((functionPreview) => (
            <FormControlLabel
              key={functionPreview.name}
              value={functionPreview.name}
              control={<Radio />}
              label={functionPreview.name}
            />
          ))}
        </RadioGroup>
      </FormControl>
    );
  }
  const tree = props.functions.reduce((acc, f) => {
    let current = acc;
    for (const m of f.module ? f.module.split(".") : ["NFunix"]) {
      if (current[m] === undefined) {
        current[m] = [];
      }
      current = current[m];
    }
    current.push(f.name);
    return acc;
  }, {} as Record<string, any>);
  const renderTree = (
    tree: Record<string, any> | string[],
    now: number
  ): any => {
    if (Array.isArray(tree)) {
      return tree.map((v) => (
        <ListItemButton
          onClick={() => props.setResponse(v)}
          key={v}
          sx={{
            paddingLeft: `${now * 2}rem`,
          }}
        >
          <ListItemText primary={v} />
        </ListItemButton>
      ));
    }
    return Object.entries(tree).map(([k, v]) => {
      if (typeof v === "object") {
        const [open, setOpen] = useState(false);
        return (
          <>
            <ListItemButton
              onClick={() => {
                setOpen((open) => !open);
              }}
            >
              <ListItemText primary={k} />
              {open ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
            <Collapse in={open} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                {renderTree(v, now + 1)}
              </List>
            </Collapse>
          </>
        );
      }
      return <></>;
    });
  };
  return (
    <List
      sx={{
        width: "100%",
        bgcolor: "background.paper",
      }}
      component="nav"
      aria-labelledby="function-list-radio-group-label"
      subheader={
        <ListSubheader id="function-list-radio-group-label">
          Select a function/page:
        </ListSubheader>
      }
    >
      {renderTree(tree, 0)}
    </List>
  );
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
    async function queryData() {
      const { list } = await getList(new URL("/list", backend));
      console.log(list);
      setState(list);
      if (list.length === 1) {
        handleFetchFunctionDetail(list[0]);
        setRadioGroupValue(list[0].name);
      }
    }
    queryData().then();
    setURL(backend.origin);
  }, [backend, url]);

  const changeRadioGroupValue = (functionName: string) => {
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

  const handleRadioGroupChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const functionName: string | null = e.currentTarget.value;
    changeRadioGroupValue(functionName);
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
        <FunixFunctionTreeOrList
          functions={state}
          value={radioGroupValue}
          onChange={handleRadioGroupChange}
          setResponse={changeRadioGroupValue}
        />
      </CardContent>
    </Card>
  );
};

export default React.memo(FunixFunctionList);
