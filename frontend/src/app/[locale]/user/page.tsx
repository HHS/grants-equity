import { Metadata } from "next";
import { LocalizedPageProps } from "src/types/intl";

import { getTranslations } from "next-intl/server";
import { GridContainer } from "@trussworks/react-uswds";

import { LogoutButton } from "./LogoutButton";

export async function generateMetadata({ params }: LocalizedPageProps) {
  const { locale } = await params;
  const t = await getTranslations({ locale });
  const meta: Metadata = {
    title: t("User.pageTitle"),
    description: t("Index.meta_description"),
  };
  return meta;
}

// this is a placeholder page used as temporary landing page for login redirects.
// Note that this page only functions to display the message passed down in query params from
// the /api/auth/callback route, and it does not handle errors.
// How to handle errors or failures from the callback route in the UI will need to be revisited
// later on, but note that throwing to an error page won't be an option, as that produces a 500
// response in the client.
export default async function UserDisplay({
  searchParams,
  params,
}: LocalizedPageProps & { searchParams: Promise<{ message?: string }> }) {
  const { message } = await searchParams;
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "User" });

  return (
    <GridContainer>
      <h1>{t("heading")}</h1>
      {message && <div>{message}</div>}
      <LogoutButton />
    </GridContainer>
  );
}
