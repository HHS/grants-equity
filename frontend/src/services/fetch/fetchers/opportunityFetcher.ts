import { OpportunityApiResponse } from "src/types/opportunity/opportunityResponseTypes";

import { fetchOpportunity } from "./fetchers";

export const getOpportunityDetails = async (
  id: string,
): Promise<OpportunityApiResponse> => {
  const response = await fetchOpportunity({ subPath: id });
  const responseBody = (await response.json()) as OpportunityApiResponse;
  return responseBody;
};
