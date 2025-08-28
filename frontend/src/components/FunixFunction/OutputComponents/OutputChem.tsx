import { Card, CardMedia } from "@mui/material";
import React, { useEffect, useState } from "react";

declare global {
  interface Window {
    indigo: any;
  }
}

const OutputChem = (props: { data: string }) => {
  const [src, setSrc] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!props.data) return;

    const loadAndRender = async () => {
      setLoading(true);
      try {
        const options = new window.indigo.MapStringString();
        options.set("render-output-format", "svg");
        const rawRender = window.indigo.render(props.data, options);
        const img = new Image();
        img.src = `data:image/svg+xml;base64,${rawRender}`;
        setSrc(img.src);
      } catch (e) {
        console.error(e);
      }
      setLoading(false);
    };

    loadAndRender();
  }, [props.data]);

  return (
    <>
      {loading ? (
        <div>Indigo Drawing...</div>
      ) : (
        <Card variant="elevation" elevation={0}>
          <CardMedia
            component="img"
            image={src ?? ""}
            alt="Chemistry"
            sx={{
              maxWidth: "100%",
              width: "auto",
              height: "auto",
            }}
          />
        </Card>
      )}
    </>
  );
};

export default React.memo(OutputChem);
