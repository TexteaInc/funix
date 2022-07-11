import React, { useCallback, useEffect, useState } from "react";
import { localApiURL } from "../shared";
import { List, ListItem, ListItemButton } from "@mui/material";
import { useStore } from "../store";

import { FunctionPreview, getList } from "@textea/shared";

export const TexteaFunctionList: React.FC = () => {
  const [state, setState] = useState<FunctionPreview[]>([]);
  useEffect(() => {
    async function queryData() {
      try {
        const { list } = await getList(new URL("/list", localApiURL));
        setState(list);
      } catch (e) {
        if (e instanceof Error && e.name === "AbortError") {
          // do nothing, only expect AbortError
        } else {
          throw e;
        }
      }
    }

    queryData().then();
  }, []);

  const handleFetchFunctionDetail = useCallback(async (name: string) => {
    useStore.setState({
      selectedFunction: name,
    });
  }, []);
  return (
    <List>
      {state.map((preview) => (
        <ListItem key={`TexteaFunctionList-${preview.name}`}>
          <ListItemButton
            onClick={() => handleFetchFunctionDetail(preview.name)}
          >
            {preview.name}
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );
};
