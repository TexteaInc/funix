import type { PostCallResponse } from "./index";
import * as localforage from "localforage";
import { enqueueSnackbar } from "notistack";
import { v4 as uuid4 } from "uuid";

export type History = {
  input: Record<any, any> | null;
  output: PostCallResponse | string | object | null;
  functionName: string;
  functionPath: string;
  name: string | null;
  timestamp: number;
  uuid: string;
};

const setHistory = async (historyKey: string, history: History) => {
  await localforage.setItem(historyKey, history);
  window.dispatchEvent(new CustomEvent("funix-history-update"));
};

const getHistoryOrMakeAnEmptyOne = async (
  historyKey: string,
  keys: string[],
  functionName: string,
  functionPath: string,
  timestamp: number
) => {
  return keys.indexOf(historyKey) !== -1
    ? await localforage.getItem<History>(historyKey)
    : {
        input: null,
        output: null,
        functionName,
        functionPath,
        name: null,
        timestamp,
        uuid: uuid4(),
      };
};

const useFunixHistory = () => {
  const getHistories = async () => {
    const histories: History[] = [];
    const keys = await localforage.keys();
    const historyKeys = keys.filter((key) => key.startsWith("funix-history-"));

    for (const historyKey of historyKeys) {
      const history = await localforage.getItem<History>(historyKey);
      if (history !== null) {
        histories.push(history);
      }
    }

    return histories.sort((a, b) => b.timestamp - a.timestamp);
  };

  const setInput = async (
    timestamp: number,
    functionName: string,
    functionPath: string,
    input: Record<any, any>
  ) => {
    const historyKey = `funix-history-${timestamp}`;

    const history: History | null = await getHistoryOrMakeAnEmptyOne(
      historyKey,
      await localforage.keys(),
      functionName,
      functionPath,
      timestamp
    );

    if (history !== null) {
      await setHistory(historyKey, {
        ...history,
        input,
      });
    }
  };

  const setOutput = async (
    timestamp: number,
    functionName: string,
    functionPath: string,
    output: PostCallResponse | string
  ) => {
    const historyKey = `funix-history-${timestamp}`;

    let newOutput = output;
    if (typeof output === "string") {
      try {
        newOutput = JSON.parse(output);
      } catch (e) {
        newOutput = output;
      }
    }

    const history: History | null = await getHistoryOrMakeAnEmptyOne(
      historyKey,
      await localforage.keys(),
      functionName,
      functionPath,
      timestamp
    );

    if (history !== null) {
      await setHistory(historyKey, {
        ...history,
        output: newOutput,
      });
    }
  };

  const setInputOutput = async (
    timestamp: number,
    functionName: string,
    functionPath: string,
    input: Record<any, any>,
    output: string | PostCallResponse
  ) => {
    // await setInput(timestamp, functionName, functionPath, input);
    // await setOutput(timestamp, functionName, functionPath, output);
    const historyKey = `funix-history-${timestamp}`;

    let newOutput = output;
    if (typeof output === "string") {
      try {
        newOutput = JSON.parse(output);
      } catch (e) {
        newOutput = output;
      }
    }

    const history: History | null = await getHistoryOrMakeAnEmptyOne(
      historyKey,
      await localforage.keys(),
      functionName,
      functionPath,
      timestamp
    );

    if (history !== null) {
      await setHistory(historyKey, {
        ...history,
        input,
        output: newOutput,
      });
    }
  };

  const removeHistory = (timestamp: number) => {
    localforage.keys().then((keys) => {
      const historyKey = `funix-history-${timestamp}`;
      if (keys.indexOf(historyKey) !== -1) {
        localforage.removeItem(historyKey).then(() => {
          window.dispatchEvent(new CustomEvent("funix-history-update"));
        });
      }
    });
  };

  const setHistoryNameAndPath = (
    timestamp: number,
    name: string,
    path: string
  ) => {
    localforage.keys().then((keys) => {
      const historyKey = `funix-history-${timestamp}`;
      if (keys.indexOf(historyKey) !== -1) {
        localforage.getItem<History>(historyKey).then((history) => {
          if (history !== null) {
            const newHistory = {
              ...history,
              name,
              functionPath: path,
            };
            localforage
              .setItem(historyKey, newHistory)
              .then(() => {
                window.dispatchEvent(new CustomEvent("funix-history-update"));
              })
              .catch((error) => {
                enqueueSnackbar(
                  "Cannot save input to history, check your console for more information",
                  {
                    variant: "error",
                  }
                );
                console.error("Funix History Error:");
                console.error(error);
              });
          }
        });
      }
    });
  };

  const clearHistory = () => {
    localforage.clear().then(() => {
      window.dispatchEvent(new CustomEvent("funix-history-update"));
    });
  };

  return {
    setInput,
    setOutput,
    setInputOutput,
    removeHistory,
    clearHistory,
    setHistoryNameAndPath,
    getHistories,
  };
};

export default useFunixHistory;
