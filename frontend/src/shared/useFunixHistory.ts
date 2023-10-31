import { PostCallResponse } from "./index";
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

const useFunixHistory = () => {
  const getHistories = async () => {
    return localforage
      .getItem("funix-history")
      .then((value) => {
        if (value) {
          // By my hand, I think I will handle it (oh, e, hah
          return JSON.parse(value as string) as History[];
        }
        return [] as History[];
      })
      .catch(() => {
        return [] as History[];
      });
  };

  const setInput = async (
    timestamp: number,
    functionName: string,
    functionPath: string,
    input: Record<any, any>
  ) => {
    getHistories().then((histories) => {
      const index = histories.findIndex((h) => h.timestamp === timestamp);
      if (index !== -1) {
        histories[index].input = input;
      } else {
        histories.push({
          input,
          output: null,
          functionName,
          functionPath,
          name: null,
          timestamp,
          uuid: uuid4(),
        });
      }
      localforage
        .setItem("funix-history", JSON.stringify(histories))
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
    });
  };

  const setOutput = async (
    timestamp: number,
    functionName: string,
    functionPath: string,
    output: PostCallResponse | string
  ) => {
    getHistories().then((histories) => {
      const index = histories.findIndex((h) => h.timestamp === timestamp);
      let newOutput = output;
      if (typeof output === "string") {
        try {
          newOutput = JSON.parse(output);
        } catch (e) {
          newOutput = output;
        }
      }
      if (index !== -1) {
        histories[index].output = newOutput;
      } else {
        histories.push({
          input: null,
          output: newOutput,
          functionName,
          functionPath,
          name: null,
          timestamp,
          uuid: uuid4(),
        });
      }
      localforage
        .setItem("funix-history", JSON.stringify(histories))
        .then(() => {
          window.dispatchEvent(new CustomEvent("funix-history-update"));
        })
        .catch((error) => {
          enqueueSnackbar(
            "Cannot save output to history, check your console for more information",
            {
              variant: "error",
            }
          );
          console.error("Funix History Error:");
          console.error(error);
        });
    });
  };

  const setInputOutput = (
    timestamp: number,
    functionName: string,
    functionPath: string,
    input: Record<any, any>,
    output: string | PostCallResponse
  ) => {
    getHistories().then((histories) => {
      const index = histories.findIndex((h) => h.timestamp === timestamp);
      let newOutput = output;
      if (typeof output === "string") {
        try {
          newOutput = JSON.parse(output);
        } catch (e) {
          newOutput = output;
        }
      }
      if (index !== -1) {
        histories[index].input = input;
        histories[index].output = newOutput;
      } else {
        histories.push({
          input,
          output: newOutput,
          functionName,
          functionPath,
          name: null,
          timestamp,
          uuid: uuid4(),
        });
      }
      localforage
        .setItem("funix-history", JSON.stringify(histories))
        .then(() => {
          window.dispatchEvent(new CustomEvent("funix-history-update"));
        })
        .catch((error) => {
          enqueueSnackbar(
            "Cannot save input and output to history, check your console for more information",
            {
              variant: "error",
            }
          );
          console.error("Funix History Error:");
          console.error(error);
        });
    });
  };

  const removeHistory = (uuid: string) => {
    getHistories().then((histories) => {
      localforage
        .setItem(
          "funix-history",
          JSON.stringify(histories.filter((h) => h.uuid !== uuid))
        )
        .then(() => {
          window.dispatchEvent(new CustomEvent("funix-history-update"));
        });
    });
  };

  const setHistoryNameAndPath = (
    timestamp: number,
    name: string,
    path: string
  ) => {
    getHistories().then((histories) => {
      const index = histories.findIndex((h) => h.timestamp === timestamp);
      if (index !== -1) {
        histories[index].name = name;
        histories[index].functionPath = path;
      }
      localforage
        .setItem("funix-history", JSON.stringify(histories))
        .then(() => {
          window.dispatchEvent(new CustomEvent("funix-history-update"));
        });
    });
  };

  const clearHistory = () => {
    localforage.removeItem("funix-history").then(() => {
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
