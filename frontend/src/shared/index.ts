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
    default: {
      return cellTypes.String;
    }
  }
}

export type FunctionPreview = {
  /**
   * Unique ID that won't make conflict
   */
  id: string;
  name: string;
  description: string;
  path: `/param/${string}`;
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
   * Output data type
   */
  output_type: {
    [key: string]: BaseType;
  };
  /**
   * Where to call this function
   */
  callee: `/call/${string}`;
  /**
   * Description of this function
   */
  description: string;
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
