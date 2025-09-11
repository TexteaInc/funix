import { useCallback, useMemo, useState } from "react";
import { Ketcher } from "ketcher-core";
import { StandaloneStructServiceProvider } from "ketcher-standalone";

export type ChemEditorValue = {
  smiles: string;
  inchi: string | null;
  inchiAuxInfo: string | null;
  inchiKey: string | null;
  smarts: string;
  ket: string;
};

export interface UseKetcherEditorOptions {
  initialValue?: ChemEditorValue | null;
  onChange?: (value: ChemEditorValue) => void;
}

export const useKetcherEditor = (options: UseKetcherEditorOptions = {}) => {
  const { initialValue, onChange } = options;

  const [value, setValue] = useState<ChemEditorValue | null>(
    initialValue ?? null,
  );

  const syncSetValue = useCallback(
    (newValue: ChemEditorValue) => {
      setValue(newValue);
      onChange?.(newValue);
    },
    [onChange],
  );

  const structServiceProvider = useMemo(
    () => new StandaloneStructServiceProvider(),
    [],
  );

  const handleInit = useCallback(
    (ketcher: Ketcher) => {
      if (window.ketcher) {
        ketcher.editor.clear();
        ketcher.editor.clearHistory();
      }
      window.ketcher = ketcher;

      if (initialValue) {
        ketcher.setMolecule(initialValue.ket);
      }

      ketcher.editor.subscribe("change", async () => {
        const ket = await ketcher.getKet();
        if (ketcher.containsReaction()) {
          const smiles = await ketcher.getSmiles();
          const smarts = await ketcher.getSmarts();
          syncSetValue({
            ket,
            smiles,
            inchi: null,
            inchiAuxInfo: null,
            inchiKey: null,
            smarts,
          });
        } else {
          const smiles = await ketcher.getSmiles();
          const inchi = await ketcher.getInchi();
          const inchiAuxInfo = await ketcher.getInchi(true);
          const inchiKey = await ketcher.getInChIKey();
          const smarts = await ketcher.getSmarts();
          syncSetValue({
            ket,
            smiles,
            inchi,
            inchiAuxInfo,
            inchiKey,
            smarts,
          });
        }
      });
    },
    [initialValue, syncSetValue],
  );

  return {
    value,
    setValue: syncSetValue,
    structServiceProvider,
    handleInit,
  };
};
