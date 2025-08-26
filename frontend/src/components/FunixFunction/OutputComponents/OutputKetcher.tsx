import Box from "@mui/material/Box/Box";
import { Ketcher } from "ketcher-core";
import { Editor } from "ketcher-react";
import { StandaloneStructServiceProvider } from "ketcher-standalone";
import React from "react";
import { useState } from "react";

declare global {
  interface Window {
    ketcher: Ketcher;
  }
}

const svgToText = (svg: Blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("Failed to read SVG file"));
    reader.readAsText(svg);
  });
};

const OutputKetcher = (props: { data: string }) => {
  const structServiceProvider = new StandaloneStructServiceProvider();
  const [svg, setSvg] = useState<string>("");

  return (
    <>
      <div
        dangerouslySetInnerHTML={{ __html: svg }}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
          overflow: "hidden",
        }}
      />
      <Box
        sx={{
          width: "0",
          height: "0",
          overflow: "hidden",
        }}
      >
        <Editor
          staticResourcesUrl={""}
          structServiceProvider={structServiceProvider}
          errorHandler={() => {}}
          onInit={async (ketcher: Ketcher) => {
            const svg = await ketcher
              .generateImage(props.data, {
                outputFormat: "svg",
              })
              .then((svg) => svgToText(svg));
            setSvg(svg as string);
          }}
        />
      </Box>
    </>
  );
};

export default React.memo(OutputKetcher);
