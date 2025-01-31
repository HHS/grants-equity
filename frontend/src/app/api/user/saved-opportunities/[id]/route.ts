import { getSession } from "src/services/auth/session";
import { getSavedOpportunity } from "src/services/fetch/fetchers/savedOpportunityFetcher";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const opportunity_id = (await params).id;

  try {
    const session = await getSession();
    if (!session || !session.token) {
      throw new Error("No active session to get saved opportunity");
    }
    const savedOpportunities = await getSavedOpportunity(
      session.token,
      session.user_id as string,
      Number(opportunity_id),
    );
    if (!savedOpportunities) {
      throw new Error("No response from API");
    }
    return new Response(JSON.stringify(savedOpportunities), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    });
  } catch (e) {
    const error = e as Error;
    return Response.json(
      { message: `Error fetching opportunity: ${error.message}` },
      { status: 500 },
    );
  }
}
