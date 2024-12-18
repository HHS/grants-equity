import { getSession } from "src/services/auth/session";

import { NextResponse } from "next/server";

export async function GET() {
  const currentSession = await getSession();
  if (currentSession) {
    return NextResponse.json({
      token: currentSession.token,
    });
  } else {
    return NextResponse.json({ token: "" });
  }
}
