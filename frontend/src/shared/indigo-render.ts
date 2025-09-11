const renderSvg = (data: string) => {
  const options = new window.indigo.MapStringString();
  options.set("render-output-format", "svg");
  const rawRender = window.indigo.render(data, options);
  const img = new Image();
  img.src = `data:image/svg+xml;base64,${rawRender}`;
  return img.src;
};

export default renderSvg;
