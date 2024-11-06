import { ReactNode } from "react";
import reactStringReplace from "react-string-replace";

const TemplateString = ({
  template,
  records,
}: {
  template: string;
  records: Record<string, string | ReactNode[] | ReactNode>;
}) => {
  const keys = Object.keys(records);
  let result: string | ReactNode[] = template;
  result = reactStringReplace(result, /{{([^}]+)}}/g, (match, _i) => {
    if (keys.includes(match)) {
      return records[match];
    }
    return match;
  });

  return result;
};

export default TemplateString;
