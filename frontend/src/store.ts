import { atom } from "jotai";
import { FunctionPreview, PostCallResponse } from "./shared";
import { History } from "./shared/useFunixHistory";

export type LastStore = {
  input: Record<any, any>;
  output: PostCallResponse | string;
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

export const selectedFunctionAtom = atom<null | FunctionPreview>(null);
export const functionsAtom = atom<null | string[]>(null);
export const themeAtom = atom<null | Record<string, any>>(null);
export const showFunctionDetailAtom = atom<boolean>(
  fromLocalStorage().showFunctionDetail,
);
export const viewTypeAtom = atom<"json" | "sheet">("json");
export const functionSecretAtom = atom<Record<string, string | null>>({});
export const backendAtom = atom<null | URL>(null);
export const backHistoryAtom = atom<null | History>(null);
export const backConsensusAtom = atom<boolean[]>([false, false, false]);
export const saveHistoryAtom = atom<boolean>(fromLocalStorage().saveHistory);
export const appSecretAtom = atom<null | string>(null);
export const historiesAtom = atom<History[]>([]);
export const lastAtom = atom<Record<string, LastStore>>({});
export const showFunctionTitleAtom = atom<boolean>(false);
export const callableDefaultAtom = atom<Record<string, Record<any, any>>>({});
