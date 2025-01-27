import "server-only";

import {
  EndpointConfig,
  fetchAgenciesEndpoint,
  fetchOpportunityEndpoint,
  opportunitySearchEndpoint,
  userLogoutEndpoint,
} from "src/services/fetch/endpointConfigs";
import {
  createRequestBody,
  createRequestUrl,
  getDefaultHeaders,
  HeadersDict,
  JSONRequestBody,
  sendRequest,
} from "src/services/fetch/fetcherHelpers";
import { APIResponse } from "src/types/apiResponseTypes";
import { OpportunityApiResponse } from "src/types/opportunity/opportunityResponseTypes";
import { QueryParamData } from "src/types/search/searchRequestTypes";
import { SearchAPIResponse } from "src/types/search/searchResponseTypes";

import { cache } from "react";

// returns a function which can be used to make a request to an endpoint defined in the passed config
// note that subpath is dynamic per request, any static paths at this point would need to be included in the namespace
// making this more flexible is a future todo
export function requesterForEndpoint<ResponseType extends APIResponse>({
  method,
  basePath,
  version,
  namespace,
}: EndpointConfig) {
  return async function (
    options: {
      subPath?: string;
      queryParamData?: QueryParamData; // only used for error handling purposes
      body?: JSONRequestBody;
      additionalHeaders?: HeadersDict;
    } = {},
  ): Promise<ResponseType> {
    const { additionalHeaders = {}, body, queryParamData, subPath } = options;
    const url = createRequestUrl(
      method,
      basePath,
      version,
      namespace,
      subPath,
      body,
    );
    const headers: HeadersDict = {
      ...getDefaultHeaders(),
      ...additionalHeaders,
    };

    const response = await sendRequest<ResponseType>(
      url,
      {
        body: method === "GET" || !body ? null : createRequestBody(body),
        headers,
        method,
      },
      queryParamData,
    );

    return response;
  };
}

export const fetchOpportunity = cache(
  requesterForEndpoint<OpportunityApiResponse>(fetchOpportunityEndpoint),
);

export const fetchOpportunitySearch = requesterForEndpoint<SearchAPIResponse>(
  opportunitySearchEndpoint,
);

export const postUserLogout =
  requesterForEndpoint<APIResponse>(userLogoutEndpoint);

export const fetchAgencies = requesterForEndpoint<APIResponse>(
  fetchAgenciesEndpoint,
);
