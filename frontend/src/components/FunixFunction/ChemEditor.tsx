import { WidgetProps } from "@rjsf/utils";
import { Editor } from "ketcher-react";
import { StandaloneStructServiceProvider } from "ketcher-standalone";
import "miew/dist/miew.min.css";
import "ketcher-react/dist/index.css";
import { Ketcher } from "ketcher-core";
import React, { useCallback, useMemo, useState } from "react";
import { Box } from "@mui/material";

interface ChemEditorProps {
  widget: WidgetProps;
}

type ChemEditorValue = {
  smiles: string;
  inchi: string | null;
  inchiAuxInfo: string | null;
  inchiKey: string | null;
  smarts: string;
  ket: string;
  svg: string;
};

const svgToText = (svg: Blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("Failed to read SVG file"));
    reader.readAsText(svg);
  });
};

const ChemEditor: React.FC<ChemEditorProps> = React.memo((props) => {
  const [_, setValue] = useState<ChemEditorValue | null>(
    props.widget.value ?? props.widget.formData ?? null,
  );

  const syncSetValue = useCallback(
    (newValue: ChemEditorValue) => {
      setValue(newValue);
      props.widget.onChange(newValue);
    },
    [props.widget],
  );

  const structServiceProvider = useMemo(
    () => new StandaloneStructServiceProvider(),
    [],
  );

  return (
    <Box
      sx={{
        width: "100%",
        height: "600px",
        resize: "vertical",
      }}
    >
      <Editor
        staticResourcesUrl={""}
        structServiceProvider={structServiceProvider}
        errorHandler={() => {}}
        onInit={(ketcher: Ketcher) => {
          if (props.widget.value || props.widget.formData) {
            const value = props.widget.value ?? props.widget.formData;
            if (value) {
              ketcher.setMolecule(value.ket);
            }
          }
          ketcher.editor.subscribe("change", async () => {
            const ket = await ketcher.getKet();
            const svg = await ketcher
              .generateImage(ket, {
                outputFormat: "svg",
              })
              .then((svg) => svgToText(svg));
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
                svg: svg as string,
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
                svg: svg as string,
              });
            }
          });
        }}
      />
    </Box>
  );
});

export default ChemEditor;
