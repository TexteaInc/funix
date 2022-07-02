import create from "zustand";

export type Store = {
  selectedFunction: null | any;
};

export const useStore = create<Store>(() => ({
  selectedFunction: null,
}));
