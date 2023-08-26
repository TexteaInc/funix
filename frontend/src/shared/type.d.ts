export declare global {
  interface WindowEventMap {
    "funix-history-update": CustomEvent;
    "funix-rollback-now": CustomEvent;
  }
}

export declare module "json-schema" {
  type inputRowItem = {
    type: "markdown" | "argument" | "divider" | "html";
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
      | "divider"
      | "images"
      | "videos"
      | "audios"
      | "files"
      | "code"
      | "index";
    content?: string | string[];
    index?: number | number[];
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
    output_indexes: number[];
  }
}
