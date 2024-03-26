import { atom } from "jotai";
import { FunctionPreview } from "./shared";
import { History } from "./shared/useFunixHistory";

export type Store = {
  selectedFunction: null | FunctionPreview;
  functions: null | string[];
  theme: null | Record<string, any>;
  showFunctionDetail: boolean;
  inputOutputWidth: string[];
  viewType: "json" | "sheet";
  functionSecret: Record<string, string | null>;
  backend: null | URL;
  backHistory: null | History;
  backConsensus: boolean[];
  saveHistory: boolean;
  appSecret: null | string;
  histories: History[];
};

// atomWithStorage("saveHistory", true);

const fromLocalStorage = () => {
  let saveHistory = localStorage.getItem("saveHistory");
  if (saveHistory === null) {
    saveHistory = "true";
    localStorage.setItem("saveHistory", saveHistory);
  }

  let showFunctionDetail = localStorage.getItem("showFunctionDetail");
  if (showFunctionDetail === null) {
    showFunctionDetail = "false";
    localStorage.setItem("showFunctionDetail", showFunctionDetail);
  }

  return {
    saveHistory: saveHistory === "true",
    showFunctionDetail: showFunctionDetail === "true",
  };
};

export const storeAtom = atom<Store>({
  selectedFunction: null,
  functions: null,
  theme: null,
  inputOutputWidth: ["50%", "50%"],
  viewType: "json",
  functionSecret: {},
  backend: null,
  backHistory: null,
  backConsensus: [false, false, false],
  appSecret: null,
  histories: [],
  ...fromLocalStorage(),
});
