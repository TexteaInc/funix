import { atom } from "jotai";
import { FunctionPreview } from "./shared";

export type Store = {
  selectedFunction: null | FunctionPreview;
};

export const storeAtom = atom<Store>({ selectedFunction: null });
