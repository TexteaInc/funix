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

const stringTemplate = (
  template: string,
  records: Record<string, string>,
): string => {
  const keys = Object.keys(records);
  return template.replace(/{{([^}]+)}}/g, (match, key) => {
    if (keys.includes(key)) {
      return records[key];
    }
    return match;
  });
};

export { TemplateString, stringTemplate };
