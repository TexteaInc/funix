const sliderWidgetParser = (widget: string) => {
  let args = [0, 100, 1];
  if (widget.indexOf("[") !== -1 && widget.indexOf("]") !== -1) {
    args = JSON.parse(widget.trim().split("slider")[1]);
  }
  return args;
};

export { sliderWidgetParser };
