import { PostCallResponse } from "./index";
import { useCallback, useEffect, useState } from "react";
import { useEventCallback } from "@mui/material";

export type History = {
  input: Record<any, any> | null;
  output: PostCallResponse | string | object | null;
  functionName: string;
  timestamp: number;
};

declare global {
  interface WindowEventMap {
    "funix-history-changed": CustomEvent;
  }
}

const useFunixHistory = () => {
  const getHistories = useCallback(() => {
    const funixHistories = localStorage.getItem("funix-history");
    if (funixHistories) {
      return JSON.parse(funixHistories) as History[];
    }
    return [];
  }, []);

  const [histories, setHistories] = useState<History[]>(getHistories);

  const setInput = useEventCallback(
    (timestamp: number, functionName: string, input: Record<any, any>) => {
      setHistories(() => {
        // no previous history, may cause bug (last action is not recorded)
        const newHistories = getHistories();
        const index = newHistories.findIndex((h) => h.timestamp === timestamp);
        if (index !== -1) {
          newHistories[index].input = input;
        } else {
          newHistories.push({
            input,
            output: null,
            functionName,
            timestamp,
          });
        }
        localStorage.setItem("funix-history", JSON.stringify(newHistories));
        return newHistories;
      });
      window.dispatchEvent(new Event("funix-history-changed"));
    }
  );

  const setOutput = useEventCallback(
    (
      timestamp: number,
      functionName: string,
      output: PostCallResponse | string
    ) => {
      setHistories(() => {
        const newHistories = getHistories();
        const index = newHistories.findIndex((h) => h.timestamp === timestamp);
        let newOutput = output;
        if (typeof output === "string") {
          try {
            newOutput = JSON.parse(output);
          } catch (e) {
            newOutput = output;
          }
        }
        if (index !== -1) {
          newHistories[index].output = newOutput;
        } else {
          newHistories.push({
            input: null,
            output: newOutput,
            functionName,
            timestamp,
          });
        }
        localStorage.setItem("funix-history", JSON.stringify(newHistories));
        return newHistories;
      });
      window.dispatchEvent(new Event("funix-history-changed"));
    }
  );

  const setInputOutput = useEventCallback(
    (
      timestamp: number,
      functionName: string,
      input: Record<any, any>,
      output: string | PostCallResponse
    ) => {
      setHistories(() => {
        const newHistories = getHistories();
        const index = newHistories.findIndex((h) => h.timestamp === timestamp);
        let newOutput = output;
        if (typeof output === "string") {
          try {
            newOutput = JSON.parse(output);
          } catch (e) {
            newOutput = output;
          }
        }
        if (index !== -1) {
          newHistories[index].input = input;
          newHistories[index].output = newOutput;
        } else {
          newHistories.push({
            input,
            output: newOutput,
            functionName,
            timestamp,
          });
        }
        localStorage.setItem("funix-history", JSON.stringify(newHistories));
        return newHistories;
      });
      window.dispatchEvent(new Event("funix-history-changed"));
    }
  );

  const removeHistory = useEventCallback((timestamp: number) => {
    setHistories(() => {
      const prevHistories = getHistories();
      const newHistories = prevHistories.filter(
        (h) => h.timestamp !== timestamp
      );
      localStorage.setItem("funix-history", JSON.stringify(newHistories));
      return newHistories;
    });
    window.dispatchEvent(new Event("funix-history-changed"));
  });

  const clearHistory = useEventCallback(() => {
    setHistories([]);
    localStorage.removeItem("funix-history");
    window.dispatchEvent(new Event("funix-history-changed"));
  });

  useEffect(() => {
    setHistories(getHistories());
  }, []);

  const handleStorageChange = useCallback(
    (event: StorageEvent | CustomEvent) => {
      if (
        (event as StorageEvent)?.key &&
        (event as StorageEvent)?.key !== "funix-history"
      ) {
        return;
      }
      setHistories(getHistories);
    },
    [getHistories]
  );

  window.addEventListener("storage", handleStorageChange);
  window.addEventListener("funix-history-changed", handleStorageChange);

  return {
    setInput,
    setOutput,
    setInputOutput,
    removeHistory,
    clearHistory,
    histories,
    getHistories,
  };
};

export default useFunixHistory;
