import React, { useCallback, useEffect, useRef, useState } from "react";
import { localApiURL } from "../constants";
import { List, ListItem, ListItemButton } from "@mui/material";
import { storeAtom } from "../store";
import { useAtom } from "jotai";
import { FunctionPreview, getList } from "../shared";

export const TexteaFunctionList: React.FC = () => {
  const [, setStore] = useAtom(storeAtom);
  const onceRef = useRef(true);
  const [state, setState] = useState<FunctionPreview[]>([]);
  useEffect(() => {
    async function queryData() {
      const { list } = await getList(new URL("/list", localApiURL));
      setState(list);
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
  return (
    <List>
      {state.map((preview) => (
        <ListItem key={`TexteaFunctionList-${preview.name}`}>
          <ListItemButton onClick={() => handleFetchFunctionDetail(preview)}>
            {preview.name}
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );
};
