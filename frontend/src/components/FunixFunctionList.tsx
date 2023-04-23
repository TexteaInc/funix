import React, { useCallback, useEffect, useState } from "react";
import {
  Collapse,
  List,
  ListItemButton,
  ListItemText,
  ListSubheader,
} from "@mui/material";
import { storeAtom } from "../store";
import { useAtom } from "jotai";
import { FunctionPreview, getList } from "../shared";
import { useNavigate, useLocation } from "react-router-dom";
import { ExpandLess, ExpandMore } from "@mui/icons-material";
import MarkdownDiv from "./Common/MarkdownDiv";

export type FunctionListProps = {
  backend: URL;
};

// Just need children
const FunixList = (props: {
  children: React.ReactNode;
  functionLength: number;
}) => (
  <List
    sx={{
      width: "100%",
      bgcolor: "background.paper",
    }}
    component="nav"
    aria-labelledby="function-list"
    subheader={
      <ListSubheader id="function-list">
        Functions / Pages ({props.functionLength})
      </ListSubheader>
    }
  >
    {props.children}
  </List>
);

const FunixFunctionList: React.FC<FunctionListProps> = ({ backend }) => {
  type TreeState = Record<string, boolean>;
  const [{ functionSecret, backHistory, backConsensus }, setStore] =
    useAtom(storeAtom);
  const [state, setState] = useState<FunctionPreview[]>([]);
  const [radioGroupValue, setRadioGroupValue] = useState<string | null>(null);
  const [url, setURL] = useState("");
  const [isTree, setTree] = useState(false);
  const { pathname, search } = useLocation();
  const navigate = useNavigate();
  const [treeState, setTreeState] = useState<TreeState>({});

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
      setState(list);
      setStore((store) => ({
        ...store,
        functions: list.map((f) => f.name),
      }));
      setTree(list.some((f) => typeof f.module === "string"));
      if (list.length === 1) {
        handleFetchFunctionDetail(list[0]);
        setRadioGroupValue(list[0].name);
      }
    }
    queryData().then();
    setURL(backend.origin);
  }, [backend, url]);

  useEffect(() => {
    if (backHistory === null) return;
    changeRadioGroupValue(backHistory.functionName);
    setStore((store) => {
      const newBackConsensus = [...store.backConsensus];
      newBackConsensus[0] = true;
      return {
        ...store,
        backConsensus: newBackConsensus,
      };
    });
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

  useEffect(() => {
    if (search === "" || typeof radioGroupValue !== "string") return;
    const searchParams = new URLSearchParams(search);
    const secret = searchParams.get("secret");
    const newFunctionSecret = {
      ...functionSecret,
      [radioGroupValue]: secret,
    };
    setStore((store) => ({
      ...store,
      functionSecret: newFunctionSecret,
    }));
    navigate(`/${radioGroupValue}`);
  }, [search, radioGroupValue]);

  if (!isTree) {
    return (
      <FunixList functionLength={state.length}>
        {state.map((functionPreview) => (
          <ListItemButton
            onClick={() => {
              changeRadioGroupValue(functionPreview.name);
            }}
            key={functionPreview.name}
            selected={radioGroupValue === functionPreview.name}
          >
            <ListItemText
              primary={
                <MarkdownDiv
                  markdown={functionPreview.name}
                  isRenderInline={true}
                />
              }
              disableTypography
            />
          </ListItemButton>
        ))}
      </FunixList>
    );
  }

  let functionsLength = 0;

  const tree = state.reduce((acc, f) => {
    let current = acc;
    for (const m of f.module ? f.module.split(".") : ["NFunix"]) {
      if (current[m] === undefined) {
        current[m] = [];
      }
      current = current[m];
    }
    current.push(f.name);
    functionsLength += 1;
    return acc;
  }, {} as Record<string, any>);

  const renderTree = (
    tree: Record<string, any> | string[],
    now: number
  ): any => {
    if (Array.isArray(tree)) {
      return tree.map((v) => (
        <ListItemButton
          onClick={() => {
            changeRadioGroupValue(v);
          }}
          key={v}
          sx={{
            paddingLeft: `${now * 2}rem`,
          }}
        >
          <ListItemText
            primary={<MarkdownDiv markdown={v} isRenderInline={true} />}
            disableTypography
          />
        </ListItemButton>
      ));
    }
    return Object.entries(tree).map(([k, v]) => {
      if (typeof v === "object") {
        return (
          <>
            <ListItemButton
              onClick={() => {
                setTreeState((state) => ({
                  ...state,
                  [`${k}${v}`]: state.hasOwnProperty(`${k}${v}`)
                    ? !state[`${k}${v}`]
                    : true,
                }));
              }}
            >
              <ListItemText
                primary={<MarkdownDiv markdown={k} isRenderInline={true} />}
                disableTypography
              />
              {treeState.hasOwnProperty(`${k}${v}`) ? (
                treeState[`${k}${v}`] ? (
                  <ExpandLess />
                ) : (
                  <ExpandMore />
                )
              ) : (
                <ExpandMore />
              )}
            </ListItemButton>
            <Collapse
              in={
                treeState.hasOwnProperty(`${k}${v}`)
                  ? treeState[`${k}${v}`]
                  : false
              }
              timeout="auto"
              unmountOnExit
            >
              <List>{renderTree(v, now + 1)}</List>
            </Collapse>
          </>
        );
      }
      return <></>;
    });
  };
  return (
    <FunixList functionLength={functionsLength}>
      {renderTree(tree, 0)}
    </FunixList>
  );
};

export default React.memo(FunixFunctionList);
