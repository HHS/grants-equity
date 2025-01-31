import "server-only";

import { compact } from "lodash";
import { environment } from "src/constants/environments";
import {
  ApiRequestError,
  BadRequestError,
  ForbiddenError,
  InternalServerError,
  NetworkError,
  NotFoundError,
  RequestTimeoutError,
  ServiceUnavailableError,
  UnauthorizedError,
  ValidationError,
} from "src/errors";
import { APIResponse } from "src/types/apiResponseTypes";
import { QueryParamData } from "src/types/search/searchRequestTypes";

export type ApiMethod = "DELETE" | "GET" | "PATCH" | "POST" | "PUT";
export interface JSONRequestBody {
  [key: string]: unknown;
}

export interface HeadersDict {
  [header: string]: string;
}

// Configuration of headers to send with all requests
export function getDefaultHeaders(): HeadersDict {
  const headers: HeadersDict = {};

  if (environment.API_AUTH_TOKEN) {
    headers["X-AUTH"] = environment.API_AUTH_TOKEN;
  }
  headers["Content-Type"] = "application/json";
  return headers;
}

export function createRequestUrl(
  method: ApiMethod,
  basePath: string,
  version: string,
  namespace: string,
  subPath = "",
  body?: JSONRequestBody,
) {
  // Remove leading slash
  const cleanedPaths = compact([basePath, version, namespace, subPath]).map(
    removeLeadingSlash,
  );
  let url = [...cleanedPaths].join("/");
  if (method === "GET" && body && !(body instanceof FormData)) {
    // Append query string to URL
    const newBody: { [key: string]: string } = {};
    Object.entries(body).forEach(([key, value]) => {
      const stringValue =
        typeof value === "string" ? value : JSON.stringify(value);
      newBody[key] = stringValue;
    });

    const params = new URLSearchParams(newBody).toString();
    url = `${url}?${params}`;
  }
  return url;
}

/**
 * Remove leading slash
 */
function removeLeadingSlash(path: string) {
  return path.replace(/^\//, "");
}

/**
 * Transform the request body into a format that fetch expects
 */
export function createRequestBody(
  payload?: JSONRequestBody,
): XMLHttpRequestBodyInit {
  if (payload instanceof FormData) {
    return payload;
  }

  return JSON.stringify(payload);
}

/**
 * Handle request errors
 */
export function fetchErrorToNetworkError(
  error: unknown,
  searchInputs?: QueryParamData,
) {
  // Request failed to send or something failed while parsing the response
  // Log the JS error to support troubleshooting
  console.error(error);
  return searchInputs
    ? new NetworkError(error, searchInputs)
    : new NetworkError(error);
}

export const throwError = (responseBody: APIResponse, url: string) => {
  const { status_code = 0, message = "", errors } = responseBody;
  console.error(`API request error at ${url} (${status_code}): ${message}`);

  const details = (errors && errors[0]) || {};

  switch (status_code) {
    case 400:
      throw new BadRequestError(message, details);
    case 401:
      throw new UnauthorizedError(message, details);
    case 403:
      throw new ForbiddenError(message, details);
    case 404:
      throw new NotFoundError(message, details);
    case 422:
      throw new ValidationError(message, details);
    case 408:
      throw new RequestTimeoutError(message, details);
    case 500:
      throw new InternalServerError(message, details);
    case 503:
      throw new ServiceUnavailableError(message, details);
    default:
      throw new ApiRequestError(
        message,
        "APIRequestError",
        status_code,
        details,
      );
  }
};
