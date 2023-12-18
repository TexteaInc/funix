import { atom } from "jotai";
import { FunctionPreview } from "./shared";
import { History } from "./shared/useFunixHistory";
import { getCookie } from "typescript-cookie";

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
  doNotTrackMe: boolean;
};

export const storeAtom = atom<Store>({
  selectedFunction: null,
  functions: null,
  theme: null,
  showFunctionDetail: false,
  inputOutputWidth: ["50%", "50%"],
  viewType: "json",
  functionSecret: {},
  backend: null,
  backHistory: null,
  backConsensus: [false, false, false],
  saveHistory: true,
  appSecret: null,
  histories: [],
  doNotTrackMe: getCookie("DO_NOT_LOG_ME") === "YES",
});
