export declare module "json-schema" {
  type inputRowItem = {
    type: "markdown" | "argument" | "dividing" | "html";
    content?: string;
    argument?: string;
    width?: number;
    offset?: number;
    position?: "left" | "center" | "right";
  };

  type outputRowItem = {
    type:
      | "markdown"
      | "html"
      | "dividing"
      | "images"
      | "videos"
      | "audios"
      | "files"
      | "code"
      | "return";
    content?: string | string[];
    return?: number;
    argument?: string;
    width?: number;
    offset?: number;
    position?: "left" | "center" | "right";
    lang?: string;
  };

  type inputRow = inputRowItem[];
  type outputRow = outputRowItem[];

  interface JSONSchema7 {
    widget?: string;
    keys?: { [key: string]: string };
    customLayout: boolean;
    input_layout: inputRow[];
    output_layout: outputRow[];
    output_indexs: number[];
  }
}
