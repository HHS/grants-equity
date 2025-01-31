import {
  gettUserSavedOpportunity,
  postUserSavedOpportunity,
} from "src/services/fetch/fetchers/fetchers";

export const postSavedOpportunity = async (
  token: string,
  user_id: string,
  opportunity_id: number,
  save: boolean,
) => {
  const ssgToken = {
    "X-SGG-Token": token,
  };
  const subPath = save
    ? `${user_id}/saved-opportunities`
    : `${user_id}/saved-opportunities/${opportunity_id}`;

  const body = save
    ? {
        opportunity_id: String(opportunity_id),
      }
    : {};
  return postUserSavedOpportunity({
    subPath,
    additionalHeaders: ssgToken,
    body,
  });
};

export const getSavedOpportunity = async (
  token: string,
  user_id: string,
  opportunity_id: number,
) => {
  const ssgToken = {
    "X-SGG-Token": token,
  };
  const subPath = `${user_id}/saved-opportunities`;
  const resp = await gettUserSavedOpportunity({
    subPath,
    additionalHeaders: ssgToken,
  });
  const savedOpportunities = resp.data as [];
  const savedOpportunity = savedOpportunities.find(
    (savedOpportunity: { opportunity_id: number }) =>
      savedOpportunity.opportunity_id === opportunity_id,
  );
  return savedOpportunity ?? [];
};
