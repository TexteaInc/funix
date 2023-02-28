import { atom } from "jotai";
import { FunctionPreview } from "./shared";

export type Store = {
  selectedFunction: null | FunctionPreview;
  theme: null | Record<string, any>;
  showFunctionDetail: boolean;
  inputOutputWidth: string[];
};

export const storeAtom = atom<Store>({
  selectedFunction: null,
  theme: null,
  showFunctionDetail: false,
  inputOutputWidth: ["50%", "50%"],
});
