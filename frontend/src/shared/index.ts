import { CellType, cellTypes } from "./sheet";
import { History } from "./useFunixHistory";

const f = (...args: Parameters<typeof fetch>) =>
  fetch(...args).then((response) => response.json());

export type BaseType = "int" | "str" | `list[${string}]` | "dict";
export type FunixType =
  | "Markdown"
  | "HTML"
  | "Images"
  | "Videos"
  | "Audios"
  | "Files"
  | "Code";
export type ReturnType =
  | "string"
  | "text"
  | "number"
  | "integer"
  | "boolean"
  | "array"
  | "list"
  | "object"
  | "dict"
  | "Figure"
  | "List"
  | "Dict"
  | FunixType
  | null;

export function matchType(type: BaseType): CellType {
  switch (type) {
    case "str": {
      return cellTypes.String;
    }
    case "int": {
      return cellTypes.Number;
    }
    case "list": {
      return cellTypes.Array;
    }
    case "dict": {
      return cellTypes.Json;
    }
    default: {
      return cellTypes.String;
    }
  }
}

export type FunctionPreview = {
  name: string;
  /**
   * Unique path that won't make conflict
   */
  path: string;
  /**
   * Module path to the function, for tree viewer
   */
  module: null | string;
  /**
   * Is this function protected by token
   */
  secret: boolean;
};

export type GetListResponse = {
  list: FunctionPreview[];
};

export async function getList(
  url: URL,
  init?: RequestInit
): Promise<GetListResponse> {
  return f(url, {
    ...init,
    method: "GET",
  });
}

export type Param = {
  type: BaseType;
  treat_as: "config" | "column" | "cell";
  whitelist?: string[];
  example?: any[];
};

export type FunctionDetail = {
  /**
   * Unique ID that won't make conflict
   */
  id: string;
  /**
   * Display Name
   */
  name: string;
  /**
   * Params of the function
   */
  params: Record<string, Param>;
  /**
   * Return data type
   */
  return_type?:
    | {
        [key: string]: BaseType;
      }
    | ReturnType[]
    | ReturnType;
  /**
   * Description of this function
   */
  description: string;
  /**
   * Schema for react-jsonschema-form
   */
  schema: Record<string, any>;
  /**
   * Theme for this function
   */
  theme: Record<string, any>;
  /**
   * Function source code
   */
  source: string;
  /**
   * Function direction
   */
  direction: "row" | "column" | "row-reverse" | "column-reverse";
};

export async function getParam(
  url: URL,
  init?: RequestInit
): Promise<FunctionDetail> {
  return f(url, {
    ...init,
    method: "GET",
  });
}

export type CallBody = {
  [x: string]: any;
};

export type PostCallResponseSuccess = {
  // we cannot find a type that describe different responses
  [key: string]: any;
};

export type PostCallResponseError = {
  error_type: "wrapper" | "function";
  error_body: string;
};

export type PostCallResponse = PostCallResponseSuccess | PostCallResponseError;

export async function callFunction(
  url: URL,
  body: CallBody,
  init?: RequestInit
): Promise<PostCallResponse> {
  return f(url, {
    ...init,
    method: "POST",
    body: JSON.stringify(body),
    headers: {
      ...init?.headers,
      "Content-Type": "application/json",
    },
  });
}

export async function callFunctionRaw(
  url: URL,
  body: CallBody,
  init?: RequestInit
): Promise<string | PostCallResponseError> {
  return fetch(url, {
    ...init,
    method: "POST",
    body: JSON.stringify(body),
    headers: {
      ...init?.headers,
      "Content-Type": "application/json",
    },
  }).then((response) => response.text());
}

export async function verifyToken(
  url: URL,
  secret: string,
  init?: RequestInit
): Promise<boolean> {
  return f(url, {
    ...init,
    method: "POST",
    body: JSON.stringify({ secret }),
    headers: {
      ...init?.headers,
      "Content-Type": "application/json",
    },
  }).then((response) => response.success);
}

export function exportHistories(histories: History[]) {
  const a = document.createElement("a");
  const now = new Date().toISOString();
  a.href = URL.createObjectURL(
    new Blob([JSON.stringify(histories, null, 2)], {
      type: "application/json",
    })
  );
  a.setAttribute("download", `${now}_Histories_Export.json`);
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

export function exportHistory(history: History) {
  const a = document.createElement("a");
  const now = new Date().toISOString();
  a.href = URL.createObjectURL(
    new Blob([JSON.stringify(history, null, 2)], {
      type: "application/json",
    })
  );
  a.setAttribute("download", `${now}_${history.functionName}_Export.json`);
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
