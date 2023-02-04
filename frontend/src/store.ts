import { atom } from "jotai";
import { FunctionPreview } from "./shared";

export type Store = {
  selectedFunction: null | FunctionPreview;
  theme: null | Record<string, any>;
  showFunctionDetail: boolean;
};

export const storeAtom = atom<Store>({
  selectedFunction: null,
  theme: null,
  showFunctionDetail: false,
});
