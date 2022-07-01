import React, { useCallback, useEffect, useState } from "react";
import { API_URL } from "../shared";
import { List, ListItem, ListItemButton } from "@mui/material";
import { useStore } from "../store";

export const TexteaFunctionList: React.FC = () => {
  const [all, setAll] = useState<{ path: string; name: string }[]>([]);
  useEffect(() => {
    const abortController = new AbortController();
    async function queryData() {
      try {
        const record: Record<string, any> = await fetch(new URL("/", API_URL), {
          signal: abortController.signal,
        }).then((response) => response.json());
        setAll(
          Object.entries(record).map(([path, value]) => ({
            path,
            name: value.name,
          }))
        );
        console.log("fetch data success");
      } catch (e) {
        if (e instanceof Error && e.name === "AbortError") {
          // do nothing, only expect AbortError
        } else {
          throw e;
        }
      }
    }
    queryData().then();
    return () => {
      abortController.abort();
    };
  }, []);

  const handleFetchFunctionDetail = useCallback(
    async (item: { name: string; path: string }) => {
      const result = await fetch(new URL(item.path, API_URL)).then((res) =>
        res.json()
      );
      console.debug("detail", result);
      useStore.setState({
        selectedFunction: {
          ...item,
          ...result,
        },
      });
    },
    []
  );
  return (
    <List>
      {all.map((item) => (
        <ListItem key={item.path}>
          <ListItemButton onClick={() => handleFetchFunctionDetail(item)}>
            {item.name}
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );
};
