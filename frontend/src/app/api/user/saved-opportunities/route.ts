import { getSession } from "src/services/auth/session";
import { postSavedOpportunity } from "src/services/fetch/fetchers/savedOpportunityFetcher";

export const POST = async (request: Request) => {
  const headers = request.headers;
  const opportunity_id = headers.get("opportunity_id");
  const saved = headers.get("saved");

  try {
    const session = await getSession();
    if (!session || !session.token) {
      throw new Error("No active session to save opportunity");
    }
    const response = await postSavedOpportunity(
      session.token,
      session.user_id as string,
      Number(opportunity_id),
      saved === "true",
    );
    if (!response) {
      throw new Error("No logout response from API");
    }
    return Response.json({ message: "saved opportunity save success" });
  } catch (e) {
    const error = e as Error;
    return Response.json(
      { message: `Error saving opportunity: ${error.message}` },
      { status: 500 },
    );
  }
};
