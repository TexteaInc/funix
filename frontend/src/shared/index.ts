import { CellType, cellTypes } from "./sheet";

const f = (...args: Parameters<typeof fetch>) =>
  fetch(...args).then((response) => response.json());

export type BaseType = "int" | "str" | `list[${string}]` | "dict";

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
   * Result is HTML format
   */
  isHTML: boolean;
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

export type GetConfigResponse = {
  backend: string;
};

export async function getConfig(): Promise<GetConfigResponse> {
  return f("/config.json", {
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
  return_type: {
    [key: string]: BaseType;
  };
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
   * For return result parser
   */
  parse_type: "plot" | "html" | "";
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
