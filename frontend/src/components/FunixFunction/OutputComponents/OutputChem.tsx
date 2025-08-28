import React, { useEffect, useRef, useState } from "react";

declare global {
  interface Window {
    indigo: any;
  }
}

const OutputChem = (props: { data: string }) => {
  const svgRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!svgRef.current || !props.data) return;

    const loadAndRender = async () => {
      setLoading(true);
      try {
        const options = new window.indigo.MapStringString();
        options.set("render-output-format", "svg");
        const rawRender = window.indigo.render(props.data, options);
        const svg = atob(rawRender);
        svgRef.current!.innerHTML = svg;
      } catch (e) {
        console.error(e);
      }
      setLoading(false);
    };

    loadAndRender();
  }, [props.data]);

  return (
    <div style={{ width: "100%", minHeight: "2rem", position: "relative" }}>
      {loading && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            color: "#666",
          }}
        >
          Loading chemistry renderer...
        </div>
      )}
      <div
        ref={svgRef}
        style={{
          width: "100%",
          height: "100%",
        }}
      />
    </div>
  );
};

export default React.memo(OutputChem);
