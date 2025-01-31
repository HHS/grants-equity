import { getSession } from "src/services/auth/session";
import { postSavedOpportunity, deleteSavedOpportunity } from "src/services/fetch/fetchers/savedOpportunityFetcher";

export const POST = async (request: Request) => {
  const headers = request.headers;
  const opportunity_id = headers.get("opportunity_id");

  try {
    const session = await getSession();
    if (!session || !session.token) {
      throw new Error("No active session to save opportunity");
    }
    const response = await postSavedOpportunity(
      session.token,
      session.user_id as string,
      Number(opportunity_id),
    );
    if (!response) {
      throw new Error("No logout response from API");
    }
    return Response.json({ type: "save", message: "saved opportunity save success" });
  } catch (e) {
    const error = e as Error;
    return Response.json(
      { message: `Error saving opportunity: ${error.message}` },
      { status: 500 },
    );
  }
};

export const DELETE = async (request: Request) => {
  const headers = request.headers;
  const opportunity_id = headers.get("opportunity_id");

  try {
    const session = await getSession();
    if (!session || !session.token) {
      throw new Error("No active session to save opportunity");
    }
    const response = await deleteSavedOpportunity(
      session.token,
      session.user_id as string,
      Number(opportunity_id),
    );
    if (!response) {
      throw new Error("No logout response from API");
    }
    return Response.json({ type: "delete", message: "deleted opportunity save success" });
  } catch (e) {
    const error = e as Error;
    return Response.json(
      { message: `Error saving opportunity: ${error.message}` },
      { status: 500 },
    );
  }
}
