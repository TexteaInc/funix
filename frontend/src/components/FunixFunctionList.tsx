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

interface TreeNode {
  [key: string]: TreeNode | string[];
}

const addFileToTree = (tree: TreeNode, parts: string[]) => {
  let currentNode = tree;

  for (const part of parts) {
    if (!currentNode[part]) {
      currentNode[part] = {};
    }
    currentNode = currentNode[part] as TreeNode;
  }
};

const treeToList = (tree: TreeNode): any[] => {
  const list: any[] = [];

  for (const key in tree) {
    if (Array.isArray(tree[key])) {
      const asList = tree[key] as string[];
      list.push(...asList);
    } else {
      const nestedList = treeToList(tree[key] as TreeNode);
      if (nestedList.length > 0) {
        list.push({ [key]: nestedList });
      } else {
        list.push(key);
      }
    }
  }

  return list;
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

  const functionsLength = state.length;
  const fileTree: TreeNode = {};

  state.forEach((preview) => {
    const path = preview.module ?? "";
    const pathList = path.split(".");
    pathList.push(preview.name);
    addFileToTree(fileTree, pathList);
  });

  const treeList = treeToList(fileTree);

  const renderNodeString = (node: string, now: number) => (
    <ListItemButton
      onClick={() => {
        changeRadioGroupValue(node);
      }}
      key={node}
      selected={radioGroupValue === node}
      sx={{
        paddingLeft: `${2 + now}rem`,
      }}
    >
      <ListItemText
        primary={<MarkdownDiv markdown={node} isRenderInline={true} />}
        disableTypography
      />
    </ListItemButton>
  );

  const renderNode = (node: any, now: number) => {
    if (typeof node === "string") {
      return renderNodeString(node, now);
    }

    const [k, v] = Object.entries(node)[0];
    if (k == "") {
      return (v as string[]).map((element) => renderNodeString(element, now));
    }
    return (
      <React.Fragment key={k}>
        <ListItemButton
          onClick={() => {
            setTreeState((state) => ({
              ...state,
              [`${k}${v}`]: state.hasOwnProperty(`${k}${v}`)
                ? !state[`${k}${v}`]
                : true,
            }));
          }}
          sx={{
            paddingLeft: `${2 + now}rem`,
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
            treeState.hasOwnProperty(`${k}${v}`) ? treeState[`${k}${v}`] : false
          }
          timeout="auto"
          unmountOnExit
        >
          <List>{renderRoot(v as any[], now + 1)}</List>
        </Collapse>
      </React.Fragment>
    );
  };

  const renderRoot = (tree: any[], now: number) => {
    return tree.map((element) => renderNode(element, now));
  };

  return (
    <FunixList functionLength={functionsLength}>
      {renderRoot(treeList, 0)}
    </FunixList>
  );
};

export default React.memo(FunixFunctionList);
