import { PostCallResponse } from "./index";
import * as localforage from "localforage";

export type History = {
  input: Record<any, any> | null;
  output: PostCallResponse | string | object | null;
  functionName: string;
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
          name: null,
          timestamp,
          uuid: window.crypto.randomUUID(),
        });
      }
      localforage
        .setItem("funix-history", JSON.stringify(histories))
        .then(() => {
          // ignore
        });
    });
  };

  const setOutput = async (
    timestamp: number,
    functionName: string,
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
          name: null,
          timestamp,
          uuid: window.crypto.randomUUID(),
        });
      }
      localforage
        .setItem("funix-history", JSON.stringify(histories))
        .then(() => {
          // ignore
        });
    });
  };

  const setInputOutput = (
    timestamp: number,
    functionName: string,
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
          name: null,
          timestamp,
          uuid: window.crypto.randomUUID(),
        });
      }
      localforage
        .setItem("funix-history", JSON.stringify(histories))
        .then(() => {
          // ignore
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
          // ignore
        });
    });
  };

  const setHistoryName = (timestamp: number, name: string) => {
    getHistories().then((histories) => {
      const index = histories.findIndex((h) => h.timestamp === timestamp);
      if (index !== -1) {
        histories[index].name = name;
      }
      localforage
        .setItem("funix-history", JSON.stringify(histories))
        .then(() => {
          // ignore
        });
    });
  };

  const clearHistory = () => {
    localforage.removeItem("funix-history").then(() => {
      // ignore
    });
  };

  return {
    setInput,
    setOutput,
    setInputOutput,
    removeHistory,
    clearHistory,
    setHistoryName,
    getHistories,
  };
};

export default useFunixHistory;
