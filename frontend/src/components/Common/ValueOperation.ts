const getInitValue = (
  type: string | undefined
): number | string | boolean | object | null => {
  switch (type) {
    case "string":
      return "";
    case "text":
      return "";
    case "number":
      return 0.0;
    case "boolean":
      return false;
    case "integer":
      return 0;
    default:
      return null;
  }
};

const castValue = (
  value: any,
  type: string | undefined
): number | string | boolean | object | null | undefined => {
  if (value === null || value == undefined) return value;
  switch (type) {
    case "string":
      return value.toString();
    case "text":
      return value.toString();
    case "number":
      const parsedFloat = parseFloat(value);
      if (!isNaN(parsedFloat) && isFinite(parsedFloat)) return parsedFloat;
      else return 0.0;
    case "integer":
      const parsedInt = parseInt(value);
      if (!isNaN(parsedInt) && isFinite(parsedInt)) return parsedInt;
      else return 0;
    case "boolean":
      if (typeof value === "boolean") return value;
      else if (typeof value === "string") {
        if (value.toLowerCase() === "false") return false;
        else return value.toLowerCase() === "true";
      } else return !!value;
    default:
      return value;
  }
};

export { getInitValue, castValue };
