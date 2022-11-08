export declare module "json-schema" {
  type rowItem = {
    type: "markdown" | "argument" | "dividing" | "html";
    content?: string;
    argument?: string;
    width?: number;
    offset?: number;
    position?: "left" | "center" | "right";
  };

  type row = rowItem[];

  interface JSONSchema7 {
    widget?: string;
    keys?: { [key: string]: string };
    customLayout: boolean;
    layout: row[];
  }
}
